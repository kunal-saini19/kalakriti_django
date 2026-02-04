# KalaKriti - Django Version

A beautiful Django-based e-commerce and cultural marketplace platform for Indian artisans and handcrafted products.

## Project Overview

This is a Django conversion of the original Next.js/TSX application. The project features:

- **Artisan Marketplace** - Connect with authentic Indian craftspeople
- **Product Catalog** - Browse and purchase handcrafted products
- **Regional Showcase** - Explore different Indian regions and their heritage
- **Cultural Stories** - Learn about artisans and their craftsmanship
- **User Authentication** - Account management and order history
- **Admin Dashboard** - Comprehensive management interface

## Technology Stack

- **Backend**: Django 6.0.2
- **Database**: SQLite (development)
- **Frontend**: HTML/Tailwind CSS
- **Python**: 3.x

## Project Structure

```
kala/
├── kala/                          # Django project settings
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── kalakriti/                    # Main Django app
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── urls.py                   # App URL patterns
│   ├── admin.py                  # Admin configuration
│   ├── templates/                # HTML templates
│   │   ├── base.html            # Base template
│   │   ├── home.html            # Home page
│   │   ├── auth/                # Authentication pages
│   │   ├── products/            # Product templates
│   │   ├── artisans/            # Artisan templates
│   │   ├── regions/             # Region templates
│   │   ├── stories/             # Story templates
│   │   └── components/          # Reusable components
│   ├── static/                   # Static files (CSS, JS)
│   └── migrations/               # Database migrations
└── manage.py                      # Django management script
```

## Database Models

### Core Models

1. **Category** - Product categories
2. **Region** - Indian regions/states
3. **Artisan** - Craftspeople profiles
4. **Product** - Handcrafted products
5. **CulturalStory** - Heritage stories
6. **GalleryImage** - Image gallery items
7. **Order** - Customer orders
8. **OrderItem** - Items in orders
9. **Newsletter** - Newsletter subscriptions

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv myenv
myenv\Scripts\activate

# On macOS/Linux
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django==6.0.2
pip install pillow  # For image handling
```

### 4. Database Setup

```bash
# Navigate to project directory
cd kala

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow the prompts to create admin user
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## Admin Interface

Access the Django admin at: `http://127.0.0.1:8000/admin/`

### Admin Features

- **Artisan Management** - Create, edit, feature artisans
- **Product Management** - Manage inventory and product details
- **Category & Region Management** - Organize content
- **Order Management** - Track customer orders
- **Newsletter Management** - View subscribers
- **Story Management** - Publish cultural stories
- **Gallery Management** - Manage image galleries

## URL Routes

### Public Routes

- `/` - Home page
- `/login/` - User login
- `/register/` - User registration
- `/forgot-password/` - Password recovery
- `/reset-password/` - Password reset
- `/logout/` - User logout

### Content Routes

- `/products/` - Product listing and search
- `/products/<slug>/` - Product detail
- `/artisans/` - Artisan directory
- `/artisans/<slug>/` - Artisan profile
- `/regions/` - Region listing
- `/regions/<slug>/` - Region detail with products and artisans
- `/gallery/` - Image gallery
- `/stories/` - Cultural stories
- `/stories/<slug>/` - Story detail

### Protected Routes

- `/private/` - User dashboard (requires login)

### Admin Routes

- `/admin/` - Django admin interface

## Key Features

### 1. Authentication System
- User registration and login
- Password recovery
- Session management
- Dashboard for authenticated users

### 2. Product Showcase
- Advanced search and filtering
- Filter by category and region
- Product ratings and reviews
- Related products
- Artisan association

### 3. Artisan Profiles
- Detailed artisan information
- Contact information (email, phone, website)
- Social media links
- Years of experience
- Portfolio of products

### 4. Regional Content
- Region profiles with cultural heritage info
- Region-specific artisans
- Regional products
- Cultural stories per region
- Regional image galleries

### 5. Admin Dashboard
- Comprehensive model management
- Search and filtering capabilities
- Bulk operations
- Custom admin pages
- Permission system

## Template Features

All templates use:
- **Tailwind CSS** for styling
- **Font Awesome** for icons
- **Responsive Design** for mobile compatibility
- **Component-based** structure

### Template Hierarchy

```
base.html (Main template)
├── components/navbar.html
├── components/footer.html
├── home.html
├── gallery.html
├── private.html
├── auth/
│   ├── login.html
│   ├── register.html
│   ├── forgot-password.html
│   └── reset-password.html
├── products/
│   ├── products_list.html
│   ├── product_detail.html
│   └── category_products.html
├── artisans/
│   ├── artisans_list.html
│   └── artisan_detail.html
├── regions/
│   ├── regions_list.html
│   └── region_detail.html
└── stories/
    ├── cultural_stories.html
    └── story_detail.html
```

## Styling

The project uses Tailwind CSS with a custom color scheme:

- **Primary Color (Orange)**: `#F97316` - Used for links, buttons, accents
- **Text Colors**: Various gray shades with proper contrast
- **Background**: Clean white with light gray accents

## Migration from Next.js to Django

### What Was Converted

1. **Pages** → **Templates** + **Views**
   - TSX pages converted to HTML templates
   - Client-side logic moved to server-side views

2. **Components** → **Template Partials**
   - React components converted to Django template includes
   - Props passed as context variables

3. **API Routes** → **Django Views**
   - Next.js API endpoints converted to view functions
   - Request/response handling via Django

4. **Styling** → **Tailwind CSS**
   - Maintained Tailwind classes for consistent styling
   - Added CDN link for Tailwind

5. **Authentication**
   - Supabase replaced with Django's built-in authentication
   - Session-based user management

## Development Tips

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Creating Data via Admin
1. Go to `/admin/`
2. Login with your superuser account
3. Use the intuitive admin interface to add:
   - Regions
   - Categories
   - Artisans
   - Products
   - Stories
   - Gallery Images

### Debugging
Enable debug logging in views.py:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Your message")
```

### Static Files (Production)
```bash
python manage.py collectstatic
```

## Security Considerations

- Change `SECRET_KEY` in `settings.py` for production
- Set `DEBUG = False` for production
- Add proper `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Enable CSRF protection (already enabled)

## Future Enhancements

- [ ] Shopping cart functionality
- [ ] Payment gateway integration
- [ ] Order tracking
- [ ] Review and rating system
- [ ] Wishlist feature
- [ ] Email notifications
- [ ] Social authentication
- [ ] Advanced analytics
- [ ] API for mobile app

## Common Issues & Solutions

### Issue: ModuleNotFoundError for Django
**Solution**: Install Django - `pip install django==6.0.2`

### Issue: No tables in database
**Solution**: Run migrations - `python manage.py migrate`

### Issue: Static files not loading
**Solution**: Run collectstatic - `python manage.py collectstatic --noinput`

### Issue: 404 errors on routes
**Solution**: Check URL patterns in `kala/urls.py` and `kalakriti/urls.py`

## Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.

## License

This project is part of the KalaKriti initiative celebrating Indian craftsmanship.

---

**Last Updated**: February 2024
**Version**: 1.0.0
