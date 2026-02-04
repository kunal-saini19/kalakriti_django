from django.urls import path
from . import views

app_name = 'kalakriti'

urlpatterns = [
    # Home & Main Pages
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('private/', views.private_page, name='private'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
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
]
