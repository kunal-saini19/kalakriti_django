# 🚀 Complete Setup & Run Instructions for KalaKriti Django

## ⚡ Quick Summary
This is a Django web application for KalaKriti - an artisan and handicraft marketplace. Follow these steps to get it running in 10 minutes.

---

## 📋 Prerequisites
- **Python 3.9+** (Check: `python --version`)
- **pip** (Python package manager)
- **Windows PowerShell** or Command Prompt

---

## 🔧 Step-by-Step Setup

### **Step 1: Navigate to Project Directory**
```powershell
cd "C:\Users\kunal saini\OneDrive\Desktop\kala\kala"
```

### **Step 2: Create Virtual Environment**
```powershell
python -m venv myenv
```

### **Step 3: Activate Virtual Environment**

**For PowerShell:**
```powershell
.\myenv\Scripts\Activate.ps1
```

**For Command Prompt:**
```cmd
.\myenv\Scripts\activate.bat
```

> If you see `(myenv)` at the start of your terminal line, it's active ✅

### **Step 4: Install Dependencies**
```powershell
pip install -r ..\requirements.txt
```

> This installs Django, Pillow, and other required packages

### **Step 5: Create Database Migrations**
```powershell
python manage.py makemigrations
```

### **Step 6: Apply Migrations**
```powershell
python manage.py migrate
```

### **Step 7: Create Admin User**
```powershell
python manage.py createsuperuser
```

You'll be asked for:
- **Username**: Enter any username (e.g., `admin`)
- **Email**: Enter your email (e.g., `admin@kalakriti.com`)
- **Password**: Enter a password (you'll need this to login)
- **Confirm Password**: Re-enter the password

### **Step 8: Start Development Server**
```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🌐 Access Your Application

### **Public Website**
- **Home**: http://127.0.0.1:8000/
- **Gallery**: http://127.0.0.1:8000/gallery/
- **Products**: http://127.0.0.1:8000/products/
- **Artisans**: http://127.0.0.1:8000/artisans/
- **Regions**: http://127.0.0.1:8000/regions/
- **Stories**: http://127.0.0.1:8000/stories/

### **Admin Panel** ⚙️
- **URL**: http://127.0.0.1:8000/admin/
- **Login**: Use the admin user you created in Step 7
- **Add Content**: 
  - Regions (Required first!)
  - Categories
  - Artisans
  - Products
  - Stories
  - Gallery Images

### **Private Dashboard** (Login Required)
- **URL**: http://127.0.0.1:8000/private/
- **Login**: Click "Login" on the website

---

## 📊 What's Included

### **Database Models (9 Total)**
1. ✅ Category - Product categories
2. ✅ Region - Indian regions/states
3. ✅ Artisan - Craftspeople profiles
4. ✅ Product - Products for sale
5. ✅ CulturalStory - Heritage stories
6. ✅ GalleryImage - Image gallery
7. ✅ Order - Customer orders
8. ✅ OrderItem - Items in orders
9. ✅ Newsletter - Email subscriptions

### **Features**
- 🔐 User authentication (Login/Register)
- 🛍️ Product catalog with filtering
- 👨‍🎨 Artisan profiles
- 🗺️ Region-based content
- 📖 Cultural stories
- 🖼️ Gallery with featured images
- 📧 Newsletter subscription
- 🛒 Order management
- ⚙️ Full admin interface

---

## 🐛 Troubleshooting

### **Issue: "pip install failed"**
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip

# Then try installing requirements again
pip install -r ..\requirements.txt
```

### **Issue: "Python not found"**
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation
- Restart terminal after installation

### **Issue: "Module not found" errors**
```powershell
# Make sure virtual environment is activated (you should see (myenv) in terminal)
pip install -r ..\requirements.txt
```

### **Issue: "Port 8000 is in use"**
```powershell
# Run on a different port
python manage.py runserver 8001
```

### **Issue: "No migrations found"**
```powershell
# Create migrations first
python manage.py makemigrations
python manage.py migrate
```

### **Issue: "admin user not found"**
```powershell
# Create a new admin user
python manage.py createsuperuser
```

---

## 🔄 Running Commands Cheat Sheet

```powershell
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Start server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Deactivate virtual environment
deactivate
```

---

## 📝 Adding Initial Data

After starting the server:

1. Go to **http://127.0.0.1:8000/admin/**
2. Login with your admin credentials
3. Follow this order to add data:
   - **Regions** first (other items depend on regions)
   - **Categories**
   - **Artisans** (choose a region)
   - **Products** (choose category, artisan, region)
   - **Cultural Stories** (choose region)
   - **Gallery Images** (optional, link to artisans/products)

---

## ✅ Corrected Files

The following issues have been **fixed** in this project:

1. ✅ **Removed duplicate ALLOWED_HOSTS** in settings.py
2. ✅ **Added python-decouple** to requirements.txt for better configuration
3. ✅ **Verified admin.py** - All models properly registered with custom interfaces
4. ✅ **Verified models.py** - All 9 models correctly defined with proper relationships
5. ✅ **Verified views.py** - All view functions present and properly decorated
6. ✅ **Verified urls.py** - All routes properly configured

---

## 🎓 Learning Resources

- **Django Docs**: https://docs.djangoproject.com/
- **Django Models**: https://docs.djangoproject.com/en/6.0/topics/db/models/
- **Django Views**: https://docs.djangoproject.com/en/6.0/topics/http/views/
- **Django Admin**: https://docs.djangoproject.com/en/6.0/ref/contrib/admin/

---

## 🎉 Success!

If you can see the homepage at http://127.0.0.1:8000/ and login to admin at http://127.0.0.1:8000/admin/, **you're all set!** 

Now you can start adding regions, artisans, and products through the admin panel.

---

## 📞 Need Help?

If you encounter issues:
1. Check that virtual environment is activated `(myenv)` in terminal
2. Make sure all requirements are installed: `pip list`
3. Check that port 8000 is not in use
4. Try creating migrations: `python manage.py makemigrations && python manage.py migrate`

**Happy coding! 🚀**
