from django.contrib import admin
from .models import (
    Category, Region, Artisan, Product, CulturalStory, 
    GalleryImage, Order, OrderItem, Newsletter
)

# Customize admin site
admin.site.site_header = 'KalaKriti Administration'
admin.site.site_title = 'KalaKriti Admin'
admin.site.index_title = 'Welcome to KalaKriti Admin'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'specialty', 'featured', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'specialty', 'region__name')
    list_filter = ('featured', 'region', 'created_at', 'years_of_experience')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'artisan', 'price', 'in_stock', 'featured', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category__name', 'artisan__name')
    list_filter = ('category', 'region', 'featured', 'in_stock', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'region', 'artisan')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Stock', {
            'fields': ('stock', 'in_stock')
        }),
        ('Media', {
            'fields': ('image', 'gallery_images')
        }),
        ('Promotion', {
            'fields': ('featured',)
        }),
        ('Reviews', {
            'fields': ('rating', 'reviews_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CulturalStory)
class CulturalStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'region', 'category', 'published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'region__name')
    list_filter = ('region', 'published', 'category', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'artisan', 'product', 'region', 'featured', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('featured', 'created_at', 'artisan', 'product', 'region')
    readonly_fields = ('created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    inlines = [OrderItemInline]
    search_fields = ('user__email', 'id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'id')
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'status')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)
    readonly_fields = ('subscribed_at',)
