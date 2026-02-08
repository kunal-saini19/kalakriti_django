from django.urls import path
from . import views

app_name = 'kalakriti'

urlpatterns = [
    # Home & Main Pages
    path('', views.home, name='home'),
    path('search/', views.search_all, name='search_all'),
    path('gallery/', views.gallery, name='gallery'),
    path('private/', views.private_page, name='private'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<uuid:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<uuid:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/click/<uuid:product_id>/', views.log_product_click, name='log_product_click'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/category/<slug:slug>/', views.category_products, name='category_products'),
    
    # Artisans
    path('artisans/', views.artisans_list, name='artisans_list'),
    path('artisans/<slug:slug>/', views.artisan_detail, name='artisan_detail'),
    
    # Regions
    path('regions/', views.regions_list, name='regions_list'),
    path('regions/<slug:slug>/', views.region_detail, name='region_detail'),
    
    # Cultural Stories
    path('stories/', views.cultural_stories, name='cultural_stories'),
    path('stories/<slug:slug>/', views.story_detail, name='story_detail'),
    
    # Newsletter
    path('subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Seller Routes
    path('seller/setup/', views.seller_setup, name='seller_setup'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/bulk-upload/', views.add_bulk_products, name='bulk_upload'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/activity/', views.seller_activity, name='seller_activity'),
    path('seller/analytics/', views.seller_analytics, name='seller_analytics'),
]
