# 🆘 Troubleshooting Guide

## Common Issues & Solutions

---

## ❌ Issue 1: "Python is not installed"

### ❓ Error Message:
```
'python' is not recognized as an internal or external command
```

### ✅ Solution:
1. **Check if Python is installed:**
   ```powershell
   python --version
   ```

2. **If not installed:**
   - Download from https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation
   - Restart PowerShell after installation
   - Test: `python --version`

3. **Still not working?**
   - Open PowerShell as **Administrator**
   - Try full path: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\python.exe --version`

---

## ❌ Issue 2: "pip install failed"

### ❓ Error Message:
```
ERROR: Could not find a version that satisfies the requirement
```

### ✅ Solution:

**Step 1: Upgrade pip**
```powershell
python -m pip install --upgrade pip
```

**Step 2: Try again**
```powershell
pip install -r ..\requirements.txt
```

**Step 3: If still fails, install packages individually**
```powershell
pip install Django==6.0.2
pip install Pillow==10.0.0
pip install sqlparse==0.5.5
pip install asgiref==3.11.1
pip install tzdata==2025.3
pip install python-decouple==3.8
```

---

## ❌ Issue 3: Virtual environment won't activate

### ❓ Error Message:
```
Cannot be loaded because running scripts is disabled on this system
```

### ✅ Solution:

**For PowerShell (Fix 1 - Recommended):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try:
```powershell
.\myenv\Scripts\Activate.ps1
```

**For PowerShell (Fix 2 - Alternative):**
```powershell
.\myenv\Scripts\Activate.ps1 -ExecutionPolicy Bypass
```

**For Command Prompt (Use this instead):**
```cmd
.\myenv\Scripts\activate.bat
```

---

## ❌ Issue 4: "No module named 'django'"

### ❓ Error Message:
```
ModuleNotFoundError: No module named 'django'
```

### ✅ Solution:

**This means virtual environment isn't activated!**

1. **Make sure you see `(myenv)` in terminal:**
   ```
   (myenv) PS C:\Users\kunal saini\OneDrive\Desktop\kala\kala>
   ```

2. **If you don't see it, activate it:**
   ```powershell
   .\myenv\Scripts\Activate.ps1
   ```

3. **Then reinstall:**
   ```powershell
   pip install -r ..\requirements.txt
   ```

4. **Test:**
   ```powershell
   python -c "import django; print(django.__version__)"
   ```
   Should print: `6.0.2`

---

## ❌ Issue 5: "Port 8000 is already in use"

### ❓ Error Message:
```
Address already in use: ('127.0.0.1', 8000)
```

### ✅ Solution:

**Option 1: Use a different port**
```powershell
python manage.py runserver 8001
```
Then visit: http://127.0.0.1:8001/

**Option 2: Find and kill the process using port 8000**

For PowerShell:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID from above)
taskkill /PID XXXX /F
```

For Command Prompt:
```cmd
netstat -ano | findstr :8000
taskkill /PID XXXX /F
```

---

## ❌ Issue 6: Migrations won't run

### ❓ Error Message:
```
No changes detected in app 'kalakriti'
```
or
```
django.db.utils.OperationalError: no such table
```

### ✅ Solution:

**Step 1: Create fresh migrations**
```powershell
python manage.py makemigrations kalakriti
```

**Step 2: Apply them**
```powershell
python manage.py migrate
```

**Step 3: If still error, reset database**
```powershell
# Delete old database
Remove-Item db.sqlite3

# Create new one
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

---

## ❌ Issue 7: Can't login to admin

### ❓ Error Message:
```
Invalid credentials
```

### ✅ Solution:

**Create a new admin user:**
```powershell
python manage.py createsuperuser
```

**When prompted, enter:**
- Username: `admin`
- Email: `admin@example.com`
- Password: Create a password you'll remember
- Confirm password: Re-enter the password

**Then try logging in again at:** http://127.0.0.1:8000/admin/

---

## ❌ Issue 8: "No static files collected"

### ❓ Error Message:
```
CSS/images not loading on website
```

### ✅ Solution:

```powershell
python manage.py collectstatic --noinput
```

This gathers all static files into one folder for the server.

---

## ❌ Issue 9: Template not found

### ❓ Error Message:
```
TemplateDoesNotExist at /
Could not find 'home.html'
```

### ✅ Solution:

**Check template location:**
- Templates should be in: `kalakriti/templates/`
- Verify the file exists: `kalakriti/templates/home.html`

**Restart server:**
```powershell
# Press CTRL+C to stop
# Then start again:
python manage.py runserver
```

---

## ❌ Issue 10: Database file missing

### ❓ Error Message:
```
Error creating tables: db.sqlite3 not found
```

### ✅ Solution:

```powershell
# Create it by running migrations
python manage.py migrate
```

This creates a fresh `db.sqlite3` file.

---

## ❌ Issue 11: Image upload errors

### ❓ Error Message:
```
Cannot find Pillow library
AttributeError: module 'PIL' has no attribute...
```

### ✅ Solution:

```powershell
# Reinstall Pillow
pip uninstall Pillow -y
pip install Pillow==10.0.0
```

Then restart the server.

---

## ❌ Issue 12: "manage.py not found"

### ❓ Error Message:
```
'python' is not recognized as a command or the file could not be found
```

### ✅ Solution:

**You're in the wrong directory!**

1. **Navigate to the correct folder:**
   ```powershell
   cd "C:\Users\kunal saini\OneDrive\Desktop\kala\kala"
   ```
   (Note: There are TWO `kala` folders - need the inner one with manage.py)

2. **Verify you're in the right place:**
   ```powershell
   # Should list manage.py
   dir
   ```

3. **Then run:**
   ```powershell
   python manage.py runserver
   ```

---

## ❌ Issue 13: "CSRF token missing"

### ❓ Error Message:
```
Forbidden (403) CSRF verification failed
```

### ✅ Solution:

This usually happens with forms. The template might be missing `{% csrf_token %}`.

Check your template files contain:
```html
<form method="POST">
  {% csrf_token %}
  <!-- form fields here -->
</form>
```

---

## ❌ Issue 14: Settings error - "SECRET_KEY not found"

### ❓ Error Message:
```
EnvironmentError: SECRET_KEY not set
```

### ✅ Solution:

**This is already configured in your settings.py**

If you still get this error:
```powershell
# Check settings.py exists
dir kala\settings.py

# Restart server
python manage.py runserver
```

---

## ❌ Issue 15: PostgreSQL/MySQL connection errors

### ❓ Error Message:
```
No module named 'psycopg2' or 'mysql'
```

### ✅ Solution:

**You're using SQLite3 (included with Python)**

This error shouldn't happen! If it does:

1. **Check your settings.py DATABASES configuration:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',  # Should be this
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. **If it's set to PostgreSQL, change it to SQLite3 above**

3. **Restart server:**
   ```powershell
   python manage.py runserver
   ```

---

## ✅ Diagnostic Commands

**Check everything is working:**

```powershell
# Check Python version
python --version

# Check Django version
python -c "import django; print(django.__version__)"

# List all installed packages
pip list

# Check if you're in virtual environment
echo $env:VIRTUAL_ENV

# Test database connectivity
python manage.py dbshell

# Validate all models
python manage.py check

# Show migrations status
python manage.py showmigrations
```

---

## 🔄 Fresh Start (Nuclear Option)

If nothing works, start completely fresh:

```powershell
# 1. Navigate to project
cd "C:\Users\kunal saini\OneDrive\Desktop\kala\kala"

# 2. Deactivate current environment
deactivate

# 3. Delete virtual environment
Remove-Item -Recurse -Force myenv

# 4. Delete database
Remove-Item db.sqlite3

# 5. Create new virtual environment
python -m venv myenv

# 6. Activate it
.\myenv\Scripts\Activate.ps1

# 7. Install requirements
pip install -r ..\requirements.txt

# 8. Run migrations
python manage.py makemigrations
python manage.py migrate

# 9. Create admin user
python manage.py createsuperuser

# 10. Start server
python manage.py runserver
```

---

## 📞 Still Stuck?

1. **Check the error message carefully** - it usually tells you what's wrong
2. **Google the exact error** - someone else likely had it
3. **Check Django documentation** - https://docs.djangoproject.com/
4. **Look at Stack Overflow** - tag: [django]
5. **Check the logs** - terminal output usually has clues

---

## ✅ Quick Verification

Before each run, verify:

1. **Virtual environment is activated:**
   ```powershell
   # Should show (myenv)
   echo $env:VIRTUAL_ENV
   ```

2. **You're in the right directory:**
   ```powershell
   # Should list manage.py
   dir
   ```

3. **Database exists:**
   ```powershell
   # Should list db.sqlite3
   dir db.sqlite3
   ```

4. **All packages installed:**
   ```powershell
   pip list | findstr Django
   ```

If all above are OK, your server should run! 🚀

---

**Need help?** The SETUP_INSTRUCTIONS.md and VISUAL_SETUP_GUIDE.md files have more details!
