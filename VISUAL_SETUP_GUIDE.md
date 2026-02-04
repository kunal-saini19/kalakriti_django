# 🎓 Step-by-Step Visual Guide

## ⏱️ Total Time: ~10 minutes

---

## 📍 Step 1: Open Terminal/PowerShell
**Location**: `C:\Users\kunal saini\OneDrive\Desktop\kala\kala`

- Right-click in the folder
- Select "Open in Terminal" or "Open PowerShell here"
- OR manually navigate:
```powershell
cd "C:\Users\kunal saini\OneDrive\Desktop\kala\kala"
```

**What you should see:**
```
PS C:\Users\kunal saini\OneDrive\Desktop\kala\kala>
```

---

## 📍 Step 2: Activate Virtual Environment
**Command:**
```powershell
.\myenv\Scripts\Activate.ps1
```

**What you should see BEFORE:**
```
PS C:\Users\kunal saini\OneDrive\Desktop\kala\kala>
```

**What you should see AFTER:**
```
(myenv) PS C:\Users\kunal saini\OneDrive\Desktop\kala\kala>
```

⚠️ **If you see an error about execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
```

---

## 📍 Step 3: Install Dependencies
**Command:**
```powershell
pip install -r ..\requirements.txt
```

**What you should see:**
```
Successfully installed Django-6.0.2 Pillow-10.0.0 sqlparse-0.5.5 ...
```

⏳ **This takes 2-3 minutes** (packages are downloading)

---

## 📍 Step 4: Create Database Migrations
**Command:**
```powershell
python manage.py makemigrations
```

**What you should see:**
```
Migrations for 'kalakriti':
  kalakriti/migrations/0001_initial.py
    - Create model Category
    - Create model Region
    - Create model Artisan
    - Create model Product
    - Create model CulturalStory
    - Create model GalleryImage
    - Create model Order
    - Create model OrderItem
    - Create model Newsletter
```

---

## 📍 Step 5: Apply Migrations
**Command:**
```powershell
python manage.py migrate
```

**What you should see:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, kalakriti, sessions
Running migrations:
  Applying migrations... OK
```

✅ **Your database is now created!**

---

## 📍 Step 6: Create Admin User
**Command:**
```powershell
python manage.py createsuperuser
```

**Interactive prompts:**

```
Username: admin
Email: admin@kalakriti.com
Password: ••••••••
Password (again): ••••••••
Superuser created successfully.
```

💡 **Remember this username and password!**

---

## 📍 Step 7: Start Development Server
**Command:**
```powershell
python manage.py runserver
```

**What you should see:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

✅ **Server is now running!**

---

## 🌐 Step 8: Open Your Application

### Open in Web Browser:

| Click This | Goes Here |
|-----------|-----------|
| Home Page | http://127.0.0.1:8000/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |
| Products | http://127.0.0.1:8000/products/ |
| Gallery | http://127.0.0.1:8000/gallery/ |

### Admin Login:
- URL: http://127.0.0.1:8000/admin/
- Username: `admin` (from Step 6)
- Password: (password you set in Step 6)

---

## 🎯 First Thing to Do: Add Initial Data

1. Go to http://127.0.0.1:8000/admin/
2. Login with admin user
3. Click "Regions" → "Add Region"
4. Fill in:
   - **Name**: "Rajasthan"
   - **Slug**: "rajasthan"
   - **Description**: "A description here"
   - **Image**: Upload an image
   - Click "Save"

5. Repeat for more regions, then add:
   - Categories
   - Artisans (pick a region)
   - Products (pick category, artisan, region)
   - Stories (pick a region)

Now your website will have content! 🎉

---

## 📱 Test These Features

### Public Features:
- [ ] Home page loads
- [ ] Products page shows products
- [ ] Artisans page shows artisans
- [ ] Gallery page shows images
- [ ] Click on a product - detail page works
- [ ] Search functionality works
- [ ] Filter by category works
- [ ] Filter by region works

### Auth Features:
- [ ] Register a new account
- [ ] Login with new account
- [ ] Visit private page (login required)
- [ ] Logout works

### Admin Features:
- [ ] Login to admin
- [ ] Add a region
- [ ] Add a category
- [ ] Add a product
- [ ] Add an artisan
- [ ] Search/filter in admin works

---

## 🛑 How to Stop the Server

Press in terminal:
```
CTRL + C
```

You'll see:
```
Keyboard interrupt received: Quitting.
```

---

## ⚡ To Run Again Later

```powershell
# Navigate to project
cd "C:\Users\kunal saini\OneDrive\Desktop\kala\kala"

# Activate environment (IMPORTANT!)
.\myenv\Scripts\Activate.ps1

# Start server
python manage.py runserver
```

✅ That's it! The database already exists.

---

## 🆘 Troubleshooting Quick Fixes

### **"Module not found" Error**
```powershell
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r ..\requirements.txt
```

### **"Port 8000 in use" Error**
```powershell
# Use different port
python manage.py runserver 8001
# Then visit http://127.0.0.1:8001/
```

### **"No tables found" Error**
```powershell
# Run migrations
python manage.py migrate
```

### **Forgot admin password**
```powershell
# Create new admin user
python manage.py createsuperuser
```

### **Want to delete everything and start fresh**
```powershell
# Delete database
Remove-Item db.sqlite3

# Recreate everything
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ✨ Success Checklist

- [x] Virtual environment activated (see `(myenv)` in terminal)
- [x] Dependencies installed (no errors)
- [x] Migrations created and applied
- [x] Admin user created
- [x] Server running (see the URL message)
- [x] Can access http://127.0.0.1:8000/
- [x] Can access http://127.0.0.1:8000/admin/
- [x] Can login to admin
- [x] Can add content in admin
- [x] Can see content on website

**If all checked ✅ - YOU'RE DONE!** 🎉

---

## 📞 Common Questions

**Q: Do I need to activate the environment every time?**
A: Yes! If you close the terminal, activate it again: `.\myenv\Scripts\Activate.ps1`

**Q: Can I use the database from the repo?**
A: Yes! The `db.sqlite3` file in the project is a working database. You can use it directly.

**Q: How do I add static files like CSS?**
A: Put them in `kalakriti/static/` folder. Then run: `python manage.py collectstatic`

**Q: Can I change the website name/title?**
A: Yes! Edit `kala/settings.py` and modify the `INSTALLED_APPS` and admin site names.

**Q: How do I deploy this?**
A: See Django deployment docs. Key steps: set `DEBUG = False`, add domain to `ALLOWED_HOSTS`, collect static files.

---

## 🎉 You're All Set!

Your KalaKriti Django application is ready to go. Start adding content through the admin panel and watch your website come alive!

**Next time you need to run it:**
1. Open PowerShell in the project folder
2. `.\myenv\Scripts\Activate.ps1`
3. `python manage.py runserver`
4. Visit http://127.0.0.1:8000/

**Happy coding! 🚀**
