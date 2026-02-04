# 🗄️ Database Migration Guide

## What Migrations Are

Migrations are Django's way of tracking changes to your models and applying them to the database. Think of them as version control for your database schema.

## First-Time Setup (What You Need to Do)

### Step 1: Navigate to Project
```bash
cd c:\Users\kunal saini\OneDrive\Desktop\kala\kala
```

### Step 2: Create the Database Tables

```bash
python manage.py migrate
```

This command:
- Creates the SQLite database (`db.sqlite3`)
- Runs all existing migrations
- Sets up database tables for Django built-in apps and kalakriti app

**Output will look like:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, kalakriti
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying kalakriti.0001_initial... OK
```

### Step 3: Verify Database Creation

Check that `db.sqlite3` was created in the kala folder:
```bash
ls -la db.sqlite3    # On Mac/Linux
dir db.sqlite3       # On Windows
```

---

## Available Models in Database

After migration, you'll have tables for:

1. **Core Models** (in kalakriti app)
   - kalakriti_category
   - kalakriti_region
   - kalakriti_artisan
   - kalakriti_product
   - kalakriti_culturalstory
   - kalakriti_galleryimage
   - kalakriti_order
   - kalakriti_orderitem
   - kalakriti_newsletter

2. **Django Built-in Models**
   - auth_user
   - auth_group
   - django_session
   - django_admin_log
   - django_content_type
   - etc.

---

## Making Changes to Models

If you modify models (add/remove/change fields):

### Step 1: Create Migration

```bash
python manage.py makemigrations
```

**Example output:**
```
Migrations for 'kalakriti':
  kalakriti/migrations/0002_product_new_field.py
    - Add field new_field to product
```

### Step 2: Review Migration File

Open the generated migration file to understand the changes:
```bash
# Windows
notepad kalakriti/migrations/0002_product_new_field.py

# Mac/Linux
nano kalakriti/migrations/0002_product_new_field.py
```

### Step 3: Apply Migration

```bash
python manage.py migrate
```

---

## Common Migration Scenarios

### Scenario 1: Adding a New Field

1. Add field to model in `models.py`:
```python
class Product(models.Model):
    # ... existing fields ...
    new_field = models.CharField(max_length=100, default='')
```

2. Create and apply migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Scenario 2: Adding a New Model

1. Create model in `models.py`:
```python
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
```

2. Create and apply migration:
```bash
python manage.py makemigrations kalakriti
python manage.py migrate
```

### Scenario 3: Changing Field Type

1. Modify field in `models.py`:
```python
# Before
price = models.IntegerField()

# After
price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

2. Create and apply migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Scenario 4: Removing a Field

1. Remove field from `models.py`

2. Create and apply migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Scenario 5: Renaming a Field

1. Rename field in `models.py`

2. Create migration:
```bash
python manage.py makemigrations
```

3. Django might ask if you want to rename. Choose that option for cleaner migration.

4. Apply migration:
```bash
python manage.py migrate
```

---

## Viewing Migration History

### See All Migrations
```bash
python manage.py showmigrations
```

**Output:**
```
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
auth
 [X] 0001_initial
 [X] 0002_alter_user_options
...
kalakriti
 [X] 0001_initial
 [X] 0002_product_new_field
```

The `[X]` means migration is applied.

### See Migration Details
```bash
python manage.py sqlmigrate kalakriti 0001
```

Shows the SQL that will be executed.

---

## Undoing Migrations (⚠️ Use Carefully)

### Undo Last Migration
```bash
python manage.py migrate kalakriti 0001
```

This reverts to migration 0001, removing all changes from migration 0002.

### Undo All Migrations
```bash
python manage.py migrate kalakriti zero
```

This removes all migrations (⚠️ Deletes all data!).

### Delete a Migration File
```bash
# Remove the .py file from migrations folder
rm kalakriti/migrations/0002_product_new_field.py
```

---

## Checking Errors

### If Migration Fails

1. **Check for syntax errors** in `models.py`
2. **Verify model references** (ForeignKeys point to existing models)
3. **Check field definitions** (valid field types, required arguments)

### Reset Everything (⚠️ Dangerous)

If migrations are broken:

```bash
# Delete database
rm db.sqlite3

# Delete all migration files except __init__.py
# Keep: kalakriti/migrations/__init__.py
# Delete: kalakriti/migrations/000*.py

# Recreate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Recreate superuser
python manage.py createsuperuser
```

---

## Best Practices

### DO ✅
- Always create migrations after model changes
- Review migration files before applying
- Use descriptive model field names
- Keep migrations in version control
- Test migrations on a copy of data first

### DON'T ❌
- Don't edit migration files manually (usually)
- Don't delete migration files without a reason
- Don't skip `makemigrations` step
- Don't `migrate` without reviewing changes first

---

## Migration File Structure

Example migration file:

```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('kalakriti', '0001_initial'),  # Previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='new_field',
            field=models.CharField(default='', max_length=100),
        ),
    ]
```

- **dependencies**: Previous migrations this depends on
- **operations**: What changes to make
  - AddField: Add new column
  - RemoveField: Delete column
  - AlterField: Modify column
  - CreateModel: New table
  - DeleteModel: Remove table
  - RenameField: Rename column
  - RenameModel: Rename table

---

## Troubleshooting

### Error: "No changes detected"
- Make sure you actually changed the model
- Check file is saved
- Verify syntax is correct

### Error: "Conflicting migrations"
- You have two migrations trying to modify the same thing
- Manually resolve by combining operations

### Error: "model doesn't have a field named..."
- Field name doesn't exist in model
- Add the field definition to the model class

### Database is locked
- Close all Django shells/servers
- Delete `db.sqlite3`
- Run `python manage.py migrate` again

---

## Quick Reference

```bash
# Check model changes
python manage.py makemigrations

# See all migrations
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# See SQL for migration
python manage.py sqlmigrate kalakriti 0001

# Undo last migration
python manage.py migrate kalakriti 0001

# Check for issues
python manage.py check

# Open Django shell
python manage.py shell

# Backup database
cp db.sqlite3 db.sqlite3.backup
```

---

## Migration Philosophy

Migrations allow you to:
1. **Track changes** - See what changed and when
2. **Collaborate** - Share model changes with team via migrations
3. **Deploy safely** - Apply changes to production systematically
4. **Rollback** - Revert changes if needed

---

## Next Steps

After initial migration:

1. ✅ Run `python manage.py migrate`
2. ✅ Create superuser with `python manage.py createsuperuser`
3. ✅ Add content via admin panel
4. ✅ Test application
5. ✅ Make model changes as needed
6. ✅ Create/apply migrations for changes
7. ✅ Deploy to production

---

**For more details**: https://docs.djangoproject.com/en/6.0/topics/migrations/
