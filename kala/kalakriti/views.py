from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import (
    Category, Region, Artisan, Product, CulturalStory, 
    GalleryImage, Order, OrderItem, Newsletter, UserProfile,
    Seller, SellerProduct, ProductActivity
)
from django.utils.text import slugify
import json


# ============ Authentication Views ============

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth is not None:
                login(request, user_auth)
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
                messages.error(request, 'Invalid credentials!')
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """Handle user registration with buyer/seller selection"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        user_type = request.POST.get('user_type', 'buyer')  # buyer or seller
        first_name = request.POST.get('first_name', '')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'auth/register.html')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name
            )
            
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                user_type=user_type
            )
            
            # If seller, redirect to seller setup page
            if user_type == 'seller':
                login(request, user)
                messages.success(request, 'Registration successful! Please set up your shop.')
                return redirect('kalakriti:seller_setup')
            else:
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('kalakriti:home')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'auth/register.html')


def forgot_password_view(request):
    """Handle forgot password"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
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
            return redirect('login')
    
    return render(request, 'auth/reset-password.html')


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
    
    context = {
        'gallery_images': images,
    }
    return render(request, 'gallery.html', context)


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
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


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
    
    context = {
        'regions': regions,
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
    if region_slug:
        region = get_object_or_404(Region, slug=region_slug)
        stories = stories.filter(region=region)
    
    context = {
        'stories': stories,
        'regions': regions,
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
        
        messages.success(request, f'Shop "{shop_name}" created successfully!')
        return redirect('kalakriti:seller_dashboard')
    
    regions = Region.objects.all()
    context = {'regions': regions}
    return render(request, 'seller/seller_setup.html', context)


@login_required(login_url='kalakriti:login')
def seller_dashboard(request):
    """Main seller dashboard with statistics"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    seller = get_object_or_404(Seller, user=request.user)
    
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
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    seller = get_object_or_404(Seller, user=request.user)
    
    if request.method == 'POST':
        products_data = request.POST.getlist('product_name[]')
        categories = request.POST.getlist('category[]')
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
                category = get_object_or_404(Category, id=categories[i]) if i < len(categories) else None
                
                product, created = Product.objects.get_or_create(
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
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    seller = get_object_or_404(Seller, user=request.user)
    seller_products = seller.seller_products.select_related('product').all()
    
    # Get activity stats for each product
    product_stats = []
    for sp in seller_products:
        views = ProductActivity.objects.filter(
            seller=seller, product=sp.product, activity_type='view'
        ).count()
        sales = ProductActivity.objects.filter(
            seller=seller, product=sp.product, activity_type='purchase'
        ).count()
        
        product_stats.append({
            'seller_product': sp,
            'views': views,
            'sales': sales,
        })
    
    context = {
        'seller': seller,
        'product_stats': product_stats,
    }
    
    return render(request, 'seller/products.html', context)


@login_required(login_url='kalakriti:login')
def seller_activity(request):
    """View seller's activity log"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    seller = get_object_or_404(Seller, user=request.user)
    
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
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'seller':
        messages.error(request, 'Only sellers can access this page!')
        return redirect('kalakriti:home')
    
    seller = get_object_or_404(Seller, user=request.user)
    
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
