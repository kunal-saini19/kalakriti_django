from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UserProfile(models.Model):
    """Extended User Profile for Buyer/Seller"""
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"
    
    class Meta:
        verbose_name_plural = 'User Profiles'


class Seller(models.Model):
    """Seller Profile for Product Management"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True)
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, blank=True, related_name='sellers')
    phone = models.CharField(max_length=20)
    bank_account = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    total_products = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.FloatField(default=0)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.shop_name
    
    class Meta:
        ordering = ['-created_at']


class SellerProduct(models.Model):
    """Seller-specific Product with seller tracking"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='seller_products')
    seller_sku = models.CharField(max_length=100, unique=True)
    seller_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller_stock = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.seller.shop_name} - {self.product.name}"
    
    class Meta:
        unique_together = ('seller', 'product')
        ordering = ['-added_at']


class ProductActivity(models.Model):
    """Track product activities - views, clicks, sales"""
    ACTIVITY_TYPES = [
        ('view', 'Product Viewed'),
        ('click', 'Product Clicked'),
        ('add_cart', 'Added to Cart'),
        ('purchase', 'Purchased'),
        ('review', 'Review Added'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='activities')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.seller.shop_name} - {self.get_activity_type_display()}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['product', '-created_at']),
        ]


class Category(models.Model):
    """Product Category Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'


class Region(models.Model):
    """Indian Region/State Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='regions/')
    cultural_heritage = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Artisan(models.Model):
    """Artisan/Craftsperson Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    bio = models.TextField()
    image = models.ImageField(upload_to='artisans/')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='artisans')
    specialty = models.CharField(max_length=200)
    years_of_experience = models.IntegerField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-featured', '-created_at']


class Product(models.Model):
    """Product Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    artisan = models.ForeignKey(Artisan, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    gallery_images = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    rating = models.FloatField(default=0, blank=True)
    reviews_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['region']),
        ]


class CulturalStory(models.Model):
    """Cultural Heritage Story Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    featured_image = models.ImageField(upload_to='stories/')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='stories')
    category = models.CharField(max_length=100, default='Heritage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cultural Stories'


class GalleryImage(models.Model):
    """Gallery Image Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='gallery_images', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_items', blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='gallery_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-featured', '-created_at']


class Order(models.Model):
    """Order Model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Order Item Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Newsletter(models.Model):
    """Newsletter Subscription Model"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']
