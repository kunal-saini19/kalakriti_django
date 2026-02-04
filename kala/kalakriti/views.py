from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import (
    Category, Region, Artisan, Product, CulturalStory, 
    GalleryImage, Order, OrderItem, Newsletter
)


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
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials!')
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
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
                password=password
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'Registration failed!')
    
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


@login_required(login_url='login')
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


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


@login_required(login_url='login')
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
