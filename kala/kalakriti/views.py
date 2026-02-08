from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Category, Region, Artisan, Product, CulturalStory, 
    GalleryImage, Order, OrderItem, Newsletter, UserProfile,
    Seller, SellerProduct, ProductActivity
)
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
import re
import secrets
import time


def _get_cart(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    request.session['cart'] = cart
    return cart


def _throttle(request, key, limit=5, window_seconds=600):
    now = time.time()
    attempts = request.session.get(key, [])
    attempts = [ts for ts in attempts if now - ts < window_seconds]
    if len(attempts) >= limit:
        request.session[key] = attempts
        return True
    attempts.append(now)
    request.session[key] = attempts
    request.session.modified = True
    return False


def _send_verification_email(request, user):
    signer = TimestampSigner(salt='kalakriti-email-verify')
    token = signer.sign(str(user.id))
    verify_url = request.build_absolute_uri(
        f"/verify-email/{token}/"
    )
    subject = "Verify your KalaKriti account"
    message = (
        "Welcome to KalaKriti!\n\n"
        "Please verify your email to activate your account:\n"
        f"{verify_url}\n\n"
        "If you did not create this account, you can ignore this email."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)


def _require_seller(request, require_verified=True):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return None, redirect('kalakriti:home')

    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        messages.error(request, 'Seller account pending verification. Please complete setup.')
        return None, redirect('kalakriti:seller_setup')

    if require_verified and not profile.seller_verified:
        profile.seller_verified = True
        profile.save(update_fields=['seller_verified'])

    return (profile, seller), None


def cart_view(request):
    cart = _get_cart(request)
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids)

    items = []
    subtotal = Decimal('0.00')

    for product in products:
        quantity = int(cart.get(str(product.id), 0))
        if quantity <= 0:
            continue
        line_total = product.price * quantity
        subtotal += line_total
        items.append({
            'product': product,
            'quantity': quantity,
            'line_total': line_total,
        })

    shipping = Decimal('0.00')
    total = subtotal + shipping

    context = {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'cart.html', context)


@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not product.in_stock:
        messages.error(request, 'This product is currently out of stock.')
        return redirect('kalakriti:product_detail', slug=product.slug)

    cart = _get_cart(request)
    current_qty = int(cart.get(str(product.id), 0))
    cart[str(product.id)] = current_qty + 1
    request.session['cart'] = cart
    request.session.modified = True

    if product.seller:
        ProductActivity.objects.create(
            seller=product.seller,
            product=product,
            activity_type='add_cart',
            user=request.user if request.user.is_authenticated else None,
            details={'quantity': 1},
        )

    messages.success(request, f'Added "{product.name}" to your cart.')
    return redirect('kalakriti:cart')


@require_http_methods(["POST"])
def update_cart(request, product_id):
    cart = _get_cart(request)
    quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.pop(str(product_id), None)
        messages.info(request, 'Item removed from cart.')
    else:
        cart[str(product_id)] = quantity
        messages.success(request, 'Cart updated.')

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('kalakriti:cart')


@require_http_methods(["POST"])
def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    messages.info(request, 'Item removed from cart.')
    return redirect('kalakriti:cart')


# ============ Authentication Views ============

@ensure_csrf_cookie
def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        if _throttle(request, 'login_attempts', limit=8, window_seconds=600):
            messages.error(request, 'Too many login attempts. Please try again later.')
            return render(request, 'auth/login.html')

        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'auth/login.html')
        
        try:
            user = User.objects.get(email__iexact=email)
            if not user.is_active:
                if settings.DEBUG:
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                else:
                    messages.error(request, 'Please verify your email to activate your account.')
                    return render(request, 'auth/login.html')

            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth is not None:
                login(request, user_auth)
                if not remember:
                    request.session.set_expiry(0)
                messages.success(request, 'Logged in successfully!')
                
                # Redirect based on user type
                try:
                    profile = user_auth.profile
                    if profile.user_type == 'seller':
                        return redirect('kalakriti:seller_dashboard')
                except UserProfile.DoesNotExist:
                    pass
                
                return redirect('kalakriti:home')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'auth/login.html')


@ensure_csrf_cookie
def register_view(request):
    """Handle user registration with buyer/seller selection"""
    if request.method == 'POST':
        if _throttle(request, 'signup_attempts', limit=5, window_seconds=600):
            messages.error(request, 'Too many signup attempts. Please try again later.')
            return render(request, 'auth/register.html')

        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        user_type = request.POST.get('user_type', 'buyer')  # buyer or seller
        first_name = request.POST.get('first_name', '')
        terms_accepted = request.POST.get('terms')

        full_name = " ".join(first_name.strip().split())
        if not (2 <= len(full_name) <= 60):
            messages.error(request, 'Full name must be between 2 and 60 characters.')
            return render(request, 'auth/register.html')

        if not re.match(r"^[A-Za-z][A-Za-z\s'.-]+[A-Za-z]$", full_name):
            messages.error(request, 'Full name contains invalid characters.')
            return render(request, 'auth/register.html')

        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'auth/register.html')

        email = email.strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Enter a valid email address.')
            return render(request, 'auth/register.html')

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messages.error(request, 'Enter a valid email address with a domain (e.g. name@example.com).')
            return render(request, 'auth/register.html')

        blocked_domains = {
            'mailinator.com', 'guerrillamail.com', '10minutemail.com', 'tempmail.com',
            'yopmail.com', 'trashmail.com', 'getnada.com', 'dispostable.com',
            'maildrop.cc', 'mintemail.com'
        }
        domain = email.split('@')[-1]
        if domain in blocked_domains:
            messages.error(request, 'Please use a non-disposable email address.')
            return render(request, 'auth/register.html')

        if not terms_accepted:
            messages.error(request, 'You must accept the terms to continue.')
            return render(request, 'auth/register.html')

        if len(password or '') < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'auth/register.html')

        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password) or not re.search(r"[^A-Za-z\d]", password):
            messages.error(request, 'Password must include letters, numbers, and symbols.')
            return render(request, 'auth/register.html')

        try:
            validate_password(password)
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
            return render(request, 'auth/register.html')

        if user_type not in ['buyer', 'seller']:
            messages.error(request, 'Invalid account type selected.')
            return render(request, 'auth/register.html')
        
        if not secrets.compare_digest(password or '', password_confirm or ''):
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'auth/register.html')
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name
                )
                if settings.DEBUG:
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                else:
                    user.is_active = False
                    user.save(update_fields=['is_active'])

                UserProfile.objects.create(
                    user=user,
                    user_type=user_type,
                    terms_accepted_at=timezone.now(),
                    terms_version=getattr(settings, 'TERMS_VERSION', 'v1'),
                    seller_verified=False,
                )

            if settings.DEBUG:
                messages.success(request, 'Account created! You can now log in.')
                return redirect('kalakriti:login')

            _send_verification_email(request, user)
            messages.success(request, 'Account created! Please verify your email to activate your account.')
            return redirect('kalakriti:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'auth/register.html')


def forgot_password_view(request):
    """Handle forgot password"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email__iexact=email).exists():
            messages.success(request, 'Check your email for password reset instructions!')
        else:
            messages.error(request, 'Email not found!')
    
    return render(request, 'auth/forgot-password.html')


def reset_password_view(request):
    """Handle password reset"""
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/reset-password.html')
        
        if request.user.is_authenticated:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('kalakriti:login')
    
    return render(request, 'auth/reset-password.html')


def verify_email(request, token):
    signer = TimestampSigner(salt='kalakriti-email-verify')
    try:
        user_id = signer.unsign(token, max_age=60 * 60 * 24 * 3)
        user = User.objects.get(id=user_id)
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(request, 'Email verified. You can now log in.')
        else:
            messages.info(request, 'Your email is already verified.')
    except (BadSignature, SignatureExpired, User.DoesNotExist):
        messages.error(request, 'Verification link is invalid or expired.')

    return redirect('kalakriti:login')


@login_required(login_url='kalakriti:login')
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('kalakriti:home')


# ============ Main Pages ============

def home(request):
    """Home page with hero section and featured content"""
    featured_artisans = Artisan.objects.filter(featured=True)[:4]
    featured_products = Product.objects.filter(featured=True)[:8]
    regions = Region.objects.all()[:6]
    cultural_stories = CulturalStory.objects.filter(published=True)[:3]
    gallery_images = GalleryImage.objects.filter(featured=True)[:6]
    
    context = {
        'featured_artisans': featured_artisans,
        'featured_products': featured_products,
        'regions': regions,
        'cultural_stories': cultural_stories,
        'gallery_images': gallery_images,
    }
    return render(request, 'home.html', context)


def gallery(request):
    """Gallery page - showcase all gallery images"""
    images = GalleryImage.objects.all()
    search_query = request.GET.get('q')

    if search_query:
        images = images.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(artisan__name__icontains=search_query) |
            Q(product__name__icontains=search_query) |
            Q(region__name__icontains=search_query)
        )
    
    context = {
        'gallery_images': images,
        'search_query': search_query,
    }
    return render(request, 'gallery.html', context)


def search_all(request):
    """Global search across products, artisans, stories, regions, and gallery."""
    query = (request.GET.get('q') or '').strip()

    products = Product.objects.none()
    artisans = Artisan.objects.none()
    stories = CulturalStory.objects.none()
    regions = Region.objects.none()
    gallery_images = GalleryImage.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(region__name__icontains=query) |
            Q(artisan__name__icontains=query)
        ).distinct()

        artisans = Artisan.objects.filter(
            Q(name__icontains=query) |
            Q(bio__icontains=query) |
            Q(specialty__icontains=query) |
            Q(region__name__icontains=query)
        ).distinct()

        stories = CulturalStory.objects.filter(published=True).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(region__name__icontains=query) |
            Q(category__icontains=query)
        ).distinct()

        regions = Region.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(cultural_heritage__icontains=query)
        ).distinct()

        gallery_images = GalleryImage.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(artisan__name__icontains=query) |
            Q(product__name__icontains=query) |
            Q(region__name__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'products': products[:12],
        'artisans': artisans[:12],
        'stories': stories[:8],
        'regions': regions[:8],
        'gallery_images': gallery_images[:12],
        'total_results': (
            products.count() + artisans.count() + stories.count() + regions.count() + gallery_images.count()
            if query else 0
        ),
    }
    return render(request, 'search_results.html', context)


@login_required(login_url='kalakriti:login')
def private_page(request):
    """Private/Dashboard page - only for authenticated users"""
    user_orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': user_orders,
    }
    return render(request, 'private.html', context)


# ============ Products ============

def products_list(request):
    """Products listing page with filtering"""
    products = Product.objects.all()
    categories = Category.objects.all()
    regions = Region.objects.all()
    
    # Filtering
    category_slug = request.GET.get('category')
    region_slug = request.GET.get('region')
    search_query = request.GET.get('q')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if region_slug:
        region = get_object_or_404(Region, slug=region_slug)
        products = products.filter(region=region)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'regions': regions,
        'selected_category': category_slug,
        'selected_region': region_slug,
        'search_query': search_query,
    }
    return render(request, 'products/products_list.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug)
    if product.seller:
        ProductActivity.objects.create(
            seller=product.seller,
            product=product,
            activity_type='view',
            user=request.user if request.user.is_authenticated else None,
            details={'source': 'product_detail'},
        )

        referrer = request.META.get('HTTP_REFERER', '')
        if referrer:
            ProductActivity.objects.create(
                seller=product.seller,
                product=product,
                activity_type='click',
                user=request.user if request.user.is_authenticated else None,
                details={'source': 'referrer', 'ref': referrer},
            )
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


@require_http_methods(["GET", "POST"])
def log_product_click(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.seller:
        ProductActivity.objects.create(
            seller=product.seller,
            product=product,
            activity_type='click',
            user=request.user if request.user.is_authenticated else None,
            details={'source': 'listing_click', 'path': request.META.get('HTTP_REFERER', '')},
        )
    return JsonResponse({'ok': True})


def category_products(request, slug):
    """Products by category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)


# ============ Artisans & Regions ============

def artisans_list(request):
    """List all artisans"""
    artisans = Artisan.objects.all()
    regions = Region.objects.all()
    
    region_slug = request.GET.get('region')
    search_query = request.GET.get('q')
    
    if region_slug:
        region = get_object_or_404(Region, slug=region_slug)
        artisans = artisans.filter(region=region)
    
    if search_query:
        artisans = artisans.filter(
            Q(name__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    context = {
        'artisans': artisans,
        'regions': regions,
        'selected_region': region_slug,
        'search_query': search_query,
    }
    return render(request, 'artisans/artisans_list.html', context)


def artisan_detail(request, slug):
    """Artisan detail page"""
    artisan = get_object_or_404(Artisan, slug=slug)
    products = artisan.products.all()
    gallery_images = artisan.gallery_images.all()
    
    context = {
        'artisan': artisan,
        'products': products,
        'gallery_images': gallery_images,
    }
    return render(request, 'artisans/artisan_detail.html', context)


def regions_list(request):
    """List all regions"""
    regions = Region.objects.all()
    search_query = request.GET.get('q')

    if search_query:
        regions = regions.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(cultural_heritage__icontains=search_query)
        )
    
    context = {
        'regions': regions,
        'search_query': search_query,
    }
    return render(request, 'regions/regions_list.html', context)


def region_detail(request, slug):
    """Region detail page"""
    region = get_object_or_404(Region, slug=slug)
    artisans = region.artisans.all()
    products = region.products.all()
    stories = region.stories.filter(published=True)
    gallery_images = region.gallery_images.all()
    
    context = {
        'region': region,
        'artisans': artisans,
        'products': products,
        'stories': stories,
        'gallery_images': gallery_images,
    }
    return render(request, 'regions/region_detail.html', context)


# ============ Stories & Content ============

def cultural_stories(request):
    """List cultural stories"""
    stories = CulturalStory.objects.filter(published=True)
    regions = Region.objects.all()
    
    region_slug = request.GET.get('region')
    search_query = request.GET.get('q')
    if region_slug:
        region = get_object_or_404(Region, slug=region_slug)
        stories = stories.filter(region=region)
    if search_query:
        stories = stories.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(region__name__icontains=search_query)
        )
    
    context = {
        'stories': stories,
        'regions': regions,
        'selected_region': region_slug,
        'search_query': search_query,
    }
    return render(request, 'stories/cultural_stories.html', context)


# ============ Seller Dashboard Views ============

@login_required(login_url='kalakriti:login')
def seller_setup(request):
    """Seller shop setup page"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    # Check if seller profile already exists
    try:
        seller = request.user.seller_profile
        if profile.seller_verified:
            return redirect('kalakriti:seller_dashboard')
    except Seller.DoesNotExist:
        pass
    
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        shop_description = request.POST.get('shop_description')
        phone = request.POST.get('phone')
        region_id = request.POST.get('region')
        
        if not shop_name or not phone:
            messages.error(request, 'Shop name and phone are required!')
            return render(request, 'seller/seller_setup.html')
        
        seller = Seller.objects.create(
            user=request.user,
            shop_name=shop_name,
            shop_description=shop_description,
            phone=phone,
            region_id=region_id if region_id else None
        )

        profile.seller_verified = True
        profile.save(update_fields=['seller_verified'])
        
        messages.success(request, f'Shop "{shop_name}" created successfully!')
        return redirect('kalakriti:seller_dashboard')
    
    regions = Region.objects.all()
    context = {
        'regions': regions,
        'seller': seller if 'seller' in locals() else None,
    }
    return render(request, 'seller/seller_setup.html', context)


@login_required(login_url='kalakriti:login')
def seller_dashboard(request):
    """Main seller dashboard with statistics"""
    seller_data, response = _require_seller(request, require_verified=True)
    if response:
        return response
    profile, seller = seller_data
    
    # Statistics
    total_products = seller.seller_products.count()
    total_views = seller.activities.filter(activity_type='view').count()
    total_purchases = seller.activities.filter(activity_type='purchase').count()
    total_revenue = seller.activities.filter(activity_type='purchase').aggregate(
        total=Sum('details__amount')
    )['total'] or 0
    
    # Recent activities
    recent_activities = seller.activities.all()[:10]
    
    # Get products
    seller_products = seller.seller_products.select_related('product').all()
    
    context = {
        'seller': seller,
        'total_products': total_products,
        'total_views': total_views,
        'total_purchases': total_purchases,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities,
        'seller_products': seller_products,
    }
    
    return render(request, 'seller/dashboard.html', context)


@login_required(login_url='kalakriti:login')
def add_bulk_products(request):
    """Add products in bulk"""
    seller_data, response = _require_seller(request, require_verified=True)
    if response:
        return response
    profile, seller = seller_data
    
    if request.method == 'POST':
        products_data = request.POST.getlist('product_name[]')
        categories = request.POST.getlist('category[]')
        new_categories = request.POST.getlist('new_category[]')
        prices = request.POST.getlist('price[]')
        stocks = request.POST.getlist('stock[]')
        descriptions = request.POST.getlist('description[]')
        
        added_count = 0
        
        for i, product_name in enumerate(products_data):
            if not product_name:
                continue
            
            try:
                # Create or get product
                slug = slugify(product_name)
                category = None
                if i < len(new_categories) and new_categories[i].strip():
                    new_cat_name = new_categories[i].strip()
                    category, _ = Category.objects.get_or_create(
                        slug=slugify(new_cat_name),
                        defaults={'name': new_cat_name}
                    )
                elif i < len(categories) and categories[i]:
                    category = get_object_or_404(Category, id=categories[i])
                
                product, _ = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        'slug': slug,
                        'description': descriptions[i] if i < len(descriptions) else '',
                        'price': prices[i] if i < len(prices) else 0,
                        'stock': stocks[i] if i < len(stocks) else 0,
                        'category': category,
                        'seller': seller,
                    }
                )
                
                # Create seller product mapping
                SellerProduct.objects.update_or_create(
                    seller=seller,
                    product=product,
                    defaults={
                        'seller_sku': f'{seller.id}-{product.id}',
                        'seller_price': prices[i] if i < len(prices) else 0,
                        'seller_stock': stocks[i] if i < len(stocks) else 0,
                    }
                )
                
                added_count += 1
            except Exception as e:
                messages.warning(request, f'Error adding {product_name}: {str(e)}')
        
        if added_count > 0:
            messages.success(request, f'Successfully added {added_count} product(s)!')
            return redirect('kalakriti:seller_dashboard')
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'seller/bulk_upload.html', context)


@login_required(login_url='kalakriti:login')
def seller_products(request):
    """View seller's products with activity"""
    seller_data, response = _require_seller(request, require_verified=True)
    if response:
        return response
    profile, seller = seller_data
    seller_products = seller.seller_products.select_related('product').all()
    
    # Get activity stats for each product
    product_stats = []
    total_views = 0
    total_sales = 0
    for sp in seller_products:
        views = ProductActivity.objects.filter(
            seller=seller, product=sp.product, activity_type='view'
        ).count()
        sales = ProductActivity.objects.filter(
            seller=seller, product=sp.product, activity_type='purchase'
        ).count()

        total_views += views
        total_sales += sales
        
        product_stats.append({
            'seller_product': sp,
            'views': views,
            'sales': sales,
        })
    
    context = {
        'seller': seller,
        'product_stats': product_stats,
        'total_views': total_views,
        'total_sales': total_sales,
    }
    
    return render(request, 'seller/products.html', context)


@login_required(login_url='kalakriti:login')
def seller_activity(request):
    """View seller's activity log"""
    seller_data, response = _require_seller(request, require_verified=True)
    if response:
        return response
    profile, seller = seller_data
    
    # Filter by type if requested
    activity_type = request.GET.get('type')
    activities = seller.activities.select_related('product')
    
    if activity_type and activity_type in dict(ProductActivity.ACTIVITY_TYPES):
        activities = activities.filter(activity_type=activity_type)
    
    # Pagination
    paginator = Paginator(activities, 20)
    page_number = request.GET.get('page')
    activities = paginator.get_page(page_number)
    
    context = {
        'seller': seller,
        'activities': activities,
        'activity_type': activity_type,
    }
    
    return render(request, 'seller/activity.html', context)


@login_required(login_url='kalakriti:login')
def seller_analytics(request):
    """Seller analytics and insights"""
    seller_data, response = _require_seller(request, require_verified=True)
    if response:
        return response
    profile, seller = seller_data
    
    # Calculate analytics
    total_views = seller.activities.filter(activity_type='view').count()
    total_clicks = seller.activities.filter(activity_type='click').count()
    total_cart_adds = seller.activities.filter(activity_type='add_cart').count()
    total_purchases = seller.activities.filter(activity_type='purchase').count()
    
    # Conversion rates
    view_to_click = (total_clicks / total_views * 100) if total_views > 0 else 0
    click_to_cart = (total_cart_adds / total_clicks * 100) if total_clicks > 0 else 0
    cart_to_purchase = (total_purchases / total_cart_adds * 100) if total_cart_adds > 0 else 0
    
    context = {
        'seller': seller,
        'total_views': total_views,
        'total_clicks': total_clicks,
        'total_cart_adds': total_cart_adds,
        'total_purchases': total_purchases,
        'view_to_click': round(view_to_click, 2),
        'click_to_cart': round(click_to_cart, 2),
        'cart_to_purchase': round(cart_to_purchase, 2),
    }
    
    return render(request, 'seller/analytics.html', context)


def story_detail(request, slug):
    """Story detail page"""
    story = get_object_or_404(CulturalStory, slug=slug, published=True)
    related_stories = CulturalStory.objects.filter(
        region=story.region, published=True
    ).exclude(id=story.id)[:3]
    
    context = {
        'story': story,
        'related_stories': related_stories,
    }
    return render(request, 'stories/story_detail.html', context)


# ============ Newsletter ============

@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    email = request.POST.get('email')
    
    if email:
        newsletter, created = Newsletter.objects.get_or_create(email=email)
        if created:
            messages.success(request, 'Successfully subscribed to newsletter!')
        else:
            messages.info(request, 'Email already subscribed!')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))
