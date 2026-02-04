# Quick Start Guide - KalaKriti Django

## 🚀 Get Started in 5 Minutes

### Step 1: Activate Virtual Environment

**Windows:**
```bash
myenv\Scripts\activate
```

**Mac/Linux:**
```bash
source myenv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install django==6.0.2 pillow
```

### Step 3: Run Database Migrations

Navigate to the kala directory:
```bash
cd c:\Users\kunal saini\OneDrive\Desktop\kala\kala
```

Create database tables:
```bash
python manage.py migrate
```

### Step 4: Create Admin Account

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Email: (enter your email)
- Password: (enter a strong password)
- Confirm password: (repeat password)

### Step 5: Start Development Server

```bash
python manage.py runserver
```

### Step 6: Access the Application

- **Website**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📝 First Steps

1. **Login to Admin**: Go to `/admin/` and login with your superuser credentials

2. **Add Your First Region**:
   - Click "Regions" → "Add Region"
   - Fill in the details (name, description, image)
   - Save

3. **Add Categories**:
   - Click "Categories" → "Add Category"
   - Fill in details
   - Save

4. **Add An Artisan**:
   - Click "Artisans" → "Add Artisan"
   - Select the region you created
   - Add bio, specialty, experience, contact info
   - Upload an image
   - Save

5. **Add Products**:
   - Click "Products" → "Add Product"
   - Select the artisan and category
   - Add price, description
   - Upload product image
   - Mark as "Featured" if desired
   - Save

6. **Add Gallery Images**:
   - Click "Gallery Images" → "Add Image"
   - Upload image
   - Assign to artisan or product
   - Save

7. **Add Cultural Stories**:
   - Click "Cultural Stories" → "Add Cultural Story"
   - Write the story
   - Select region
   - Upload featured image
   - Mark as published
   - Save

## 🌐 Main Pages

- **Homepage** (`/`): Displays featured content
- **Products** (`/products/`): Browse and search products
- **Artisans** (`/artisans/`): Discover artisans
- **Regions** (`/regions/`): Explore regions
- **Gallery** (`/gallery/`): View image galleries
- **Stories** (`/stories/`): Read cultural stories

## 🔐 User Features

- **Register**: `/register/`
- **Login**: `/login/`
- **Dashboard**: `/private/` (after login)
- **Logout**: `/logout/`

## ⚙️ Admin Features

Access at `/admin/` with superuser account

### Models You Can Manage:
- **Artisans** - Craftspeople profiles
- **Products** - Items for sale
- **Categories** - Product categories
- **Regions** - Indian regions
- **Gallery Images** - Image collections
- **Cultural Stories** - Heritage narratives
- **Orders** - Customer purchases
- **Newsletter** - Email subscriptions

## 💡 Tips

1. **Featured Items**: Check the "Featured" checkbox to show items on homepage
2. **Search**: Use the search box in admin to find items quickly
3. **Filters**: Use filter options in admin list views
4. **Images**: Always include high-quality images for better presentation
5. **Slugs**: These auto-generate from names but can be customized

## 🐛 Troubleshooting

**Problem**: "Module not found django"
```bash
pip install django==6.0.2
```

**Problem**: Database locked
```bash
# Delete db.sqlite3 and run:
python manage.py migrate
```

**Problem**: Port 8000 already in use
```bash
python manage.py runserver 8001
```

## 📚 Useful Commands

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic
```

## 🎨 Customize

### Change Colors
Edit `base.html` to modify the color variables:
```html
<style>
    :root {
        --color-orange: #F97316;  /* Change this color */
    }
</style>
```

### Change Site Title
Edit `settings.py`:
```python
# Around line 40 in admin.py
admin.site.site_header = 'Your Site Name'
admin.site.site_title = 'Your Title'
```

## 📞 Support

- Check the full `DJANGO_SETUP_GUIDE.md` for detailed documentation
- Review template files in `kalakriti/templates/`
- Check admin configuration in `kalakriti/admin.py`

---

**Happy Crafting! 🎨**
