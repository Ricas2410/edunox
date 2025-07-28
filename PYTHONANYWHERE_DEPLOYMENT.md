# 🚀 EduLink GH - PythonAnywhere Deployment Guide

## ✅ Codebase Cleanup Completed

Your codebase has been cleaned and optimized for PythonAnywhere deployment:

### 🧹 What Was Cleaned:
- ✅ Fixed corrupted `requirements.txt` with clean package list
- ✅ Removed duplicate deployment guides and unnecessary files
- ✅ Cleaned up Python cache files (`__pycache__` directories)
- ✅ Removed Docker files, nginx configs, and other non-PythonAnywhere files
- ✅ Updated `.env` for production with `DEBUG=False`
- ✅ Configured MySQL database settings for PythonAnywhere
- ✅ Verified ImageKit integration with your credentials

### 📦 Current Configuration:
- **Database**: MySQL (`edunox$edunox_db`)
- **Username**: `edunox`
- **Password**: `Asare@2017`
- **ImageKit**: Properly configured with your credentials
- **Debug**: `False` (production ready)

## 🚀 Quick Deployment Steps

### 1. Clone Repository on PythonAnywhere
```bash
cd ~
git clone https://github.com/Ricas2410/edunox.git
cd edunox
```

### 2. Setup Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create cache table for production
python manage.py createcachetable

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Test ImageKit
```bash
python manage.py test_imagekit
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Configure Web App
In your PythonAnywhere Web tab:

- **Source code**: `/home/edunox/edunox`
- **Working directory**: `/home/edunox/` (keep the default)
- **Virtualenv**: `/home/edunox/edunox/venv`
- **WSGI file**: Edit to point to your Django app
- **Static files**: URL `/static/` → Directory `/home/edunox/edunox/staticfiles/`

### 7. WSGI Configuration
Edit your WSGI file (click the link in the Web tab):

```python
import os
import sys

# Add your project directory to sys.path
path = '/home/edunox/edunox'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 🔧 Environment Variables
Your `.env` file is already configured with:
- `DEBUG=False`
- MySQL database settings
- ImageKit credentials
- Production-ready configuration

## 🧪 Testing Commands
```bash
# Test the system
python manage.py check

# Test ImageKit integration
python manage.py test_imagekit --upload-test

# Test database connection
python manage.py dbshell
```

## 📝 Important Notes
1. **Database**: Uses MySQL in production (`DEBUG=False`)
2. **Media Storage**: Uses ImageKit for all media files
3. **Static Files**: Served by WhiteNoise
4. **Security**: Production security settings enabled
5. **Caching**: Database cache configured for production

## 🆘 Troubleshooting
- **Database errors**: Check MySQL credentials in `.env`
- **ImageKit issues**: Run `python manage.py test_imagekit`
- **Static files**: Run `python manage.py collectstatic --noinput`
- **Permissions**: Ensure proper file permissions on PythonAnywhere

Your codebase is now clean, optimized, and ready for PythonAnywhere deployment! 🎉
