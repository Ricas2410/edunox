# Simple PythonAnywhere Deployment Guide

## 🎯 Overview
Your Django app now works with the same files for both development and production. The system automatically:
- Uses SQLite when `DEBUG=True` (development)
- Uses MySQL when `DEBUG=False` (production)
- Handles caching, logging, and security settings automatically

## 🚀 Quick Deployment Steps

### 1. Upload Your Code
```bash
# On PythonAnywhere console
cd ~
git clone https://github.com/your-username/EDU_BRIDGE.git edunox
cd edunox
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy and edit your environment file
cp .env.example .env
nano .env
```

**Required settings in .env:**
```env
SECRET_KEY=your-50-character-secret-key
DEBUG=False
DB_PASSWORD=your-mysql-password
IMAGEKIT_PRIVATE_KEY=private_GUCDIbBYRlVFHVL/kEyJM0EZY9s=
IMAGEKIT_PUBLIC_KEY=public_/xl3626TiK+x0ATTk3n5A1pGdl4=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/edunox
```

### 4. Setup Database
```bash
# Create cache table for production
python manage.py createcachetable

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Configure PythonAnywhere Web App

#### A. WSGI Configuration
In your PythonAnywhere Web tab, edit the WSGI file:
```python
import os
import sys

# Add your project directory to sys.path
path = '/home/edunox/edunox'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')

# Activate virtual environment
activate_this = '/home/edunox/edunox/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### B. Static Files Mapping
In the Web tab, add:
- **URL**: `/static/`
- **Directory**: `/home/edunox/edunox/staticfiles/`

### 7. Reload and Test
1. Click "Reload" in PythonAnywhere Web tab
2. Visit: `https://edunox.pythonanywhere.com`

## 🔧 Testing Commands

```bash
# Test the system
python manage.py check

# Test ImageKit
python manage.py test_imagekit

# Test database
python manage.py dbshell
```

## 🐛 Common Issues

### Issue 1: Site shows error with DEBUG=False
**Solution:** Check your .env file has `DEBUG=False` and proper `DB_PASSWORD`

### Issue 2: Media uploads not working
**Solution:** Test ImageKit: `python manage.py test_imagekit`

### Issue 3: Static files not loading
**Solution:** Run `python manage.py collectstatic --noinput` and check static files mapping

### Issue 4: Database errors
**Solution:** Verify MySQL credentials in .env file

## 📝 Environment Variables Reference

### Required for Production
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DB_PASSWORD=your-mysql-password
```

### Optional (with defaults)
```env
DB_NAME=edunox$edunox_db
DB_USER=edunox
DB_HOST=edunox.mysql.pythonanywhere-services.com
DB_PORT=3306
```

## 🔄 Updating Your Site

```bash
cd ~/edunox
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Reload web app in PythonAnywhere dashboard
```

## 💡 How It Works

Your `settings.py` now automatically:

1. **Database**: 
   - SQLite when `DEBUG=True`
   - MySQL when `DEBUG=False`

2. **Caching**:
   - Dummy cache when `DEBUG=True`
   - Database cache when `DEBUG=False`

3. **Security**:
   - Relaxed when `DEBUG=True`
   - Strict when `DEBUG=False`

4. **Logging**:
   - Console only when `DEBUG=True`
   - File + console when `DEBUG=False`

This means you use the same files everywhere - just change `DEBUG=True/False`!

## 🆘 Getting Help

- Check error logs in PythonAnywhere Web tab
- View application logs: `tail -f logs/django.log`
- Test locally first with `DEBUG=False` to catch issues early

Remember: Always test with `DEBUG=False` locally before deploying!
