# 🚀 PythonAnywhere Deployment Guide for Edunox GH

Complete step-by-step guide to deploy Edunox GH educational platform on PythonAnywhere with ImageKit media storage.

## 📋 Prerequisites

- PythonAnywhere account (username: `edunox`)
- GitHub repository: `https://github.com/Ricas2410/edunox.git`
- ImageKit account configured
- Domain name (optional)

## 🔧 Step 1: Initial Setup on PythonAnywhere

### 1.1 Login to PythonAnywhere
- Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- Login with username: `edunox`

### 1.2 Open Bash Console
- Go to **Tasks** → **Consoles**
- Click **Bash** to open a new console

### 1.3 Clone Repository
```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/Ricas2410/edunox.git

# Navigate to project directory
cd edunox
```

## 🐍 Step 2: Python Environment Setup

### 2.1 Create Virtual Environment
```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2.2 Install Dependencies
```bash
# Install requirements
pip install -r requirements.txt

# Install additional packages for PythonAnywhere
pip install mysqlclient
pip install imagekitio
```

## 🗄️ Step 3: Database Setup

### 3.1 Create MySQL Database
- Go to **Databases** tab in PythonAnywhere dashboard
- Create a new database: `edunox$edunox_db`
- Note the database details:
  - Host: `edunox.mysql.pythonanywhere-services.com`
  - Database: `edunox$edunox_db`
  - Username: `edunox`
  - Password: [your database password]

### 3.2 Configure Database Settings
```bash
# Create production environment file
nano .env.production
```

Add the following content:
```env
# Database Configuration
DATABASE_URL=mysql://edunox:[YOUR_DB_PASSWORD]@edunox.mysql.pythonanywhere-services.com/edunox$edunox_db

# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=edunox.pythonanywhere.com,www.edunox.pythonanywhere.com

# ImageKit Configuration
IMAGEKIT_PRIVATE_KEY=private_GUCDIbBYRlVFHVL/kEyJM0EZY9s=
IMAGEKIT_PUBLIC_KEY=public_/xl3626TiK+x0ATTk3n5A1pGdl4=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/edunox

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Edunox GH <your-email@gmail.com>

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## ⚙️ Step 4: Django Configuration Updates

### 4.1 Update Settings for Production
```bash
# Edit settings.py
nano edubridge/settings.py
```

Add ImageKit configuration at the end:
```python
# ImageKit Configuration
if not DEBUG:
    # ImageKit settings
    IMAGEKIT_PRIVATE_KEY = config('IMAGEKIT_PRIVATE_KEY')
    IMAGEKIT_PUBLIC_KEY = config('IMAGEKIT_PUBLIC_KEY') 
    IMAGEKIT_URL_ENDPOINT = config('IMAGEKIT_URL_ENDPOINT')
    
    # Use ImageKit for media files
    DEFAULT_FILE_STORAGE = 'core.storage.ImageKitStorage'
    MEDIA_URL = 'https://ik.imagekit.io/edunox/'
```

### 4.2 Create ImageKit Storage Backend
```bash
# Create storage backend
nano core/storage.py
```

Add the following content:
```python
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from imagekitio import ImageKit
from django.conf import settings
import uuid

class ImageKitStorage(Storage):
    def __init__(self):
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def _save(self, name, content):
        # Generate unique filename
        file_id = str(uuid.uuid4())
        
        # Upload to ImageKit
        upload = self.imagekit.upload_file(
            file=content.read(),
            file_name=file_id,
            options={
                "folder": "/edunox/",
                "use_unique_file_name": True
            }
        )
        
        return upload.response_metadata.raw['name']
    
    def exists(self, name):
        return False
    
    def url(self, name):
        return f"{settings.IMAGEKIT_URL_ENDPOINT}/{name}"
```

## 🌐 Step 5: Web App Configuration

### 5.1 Create Web App
- Go to **Web** tab in PythonAnywhere dashboard
- Click **Add a new web app**
- Choose **Manual configuration**
- Select **Python 3.10**

### 5.2 Configure WSGI File
- Click on **WSGI configuration file** link
- Replace content with:

```python
import os
import sys

# Add your project directory to sys.path
path = '/home/edunox/edunox'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'edubridge.settings'
os.environ.setdefault('DJANGO_CONFIGURATION', 'Production')

# Activate virtual environment
activate_this = '/home/edunox/edunox/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5.3 Configure Static Files
- In **Web** tab, set:
  - **Source code**: `/home/edunox/edunox`
  - **Working directory**: `/home/edunox/edunox`

- Add static files mapping:
  - **URL**: `/static/`
  - **Directory**: `/home/edunox/edunox/staticfiles/`

- Add media files mapping:
  - **URL**: `/media/`
  - **Directory**: `/home/edunox/edunox/media/`

## 🔄 Step 6: Database Migration and Setup

### 6.1 Run Migrations
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment
export DJANGO_SETTINGS_MODULE=edubridge.settings

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Populate initial data
python manage.py populate_initial_data
```

## 🚀 Step 7: Final Deployment Steps

### 7.1 Reload Web App
- Go to **Web** tab
- Click **Reload edunox.pythonanywhere.com**

### 7.2 Test Deployment
- Visit: `https://edunox.pythonanywhere.com`
- Test key functionality:
  - Homepage loads
  - User registration/login
  - Admin panel access
  - File uploads (should go to ImageKit)
  - Email notifications

### 7.3 Configure Domain (Optional)
If you have a custom domain:
- Go to **Web** tab
- Add your domain in **Domain** section
- Update DNS records to point to PythonAnywhere

## 🔧 Step 8: Environment Management

### 8.1 Create Management Script
```bash
# Create deployment script
nano deploy_update.sh
```

Add content:
```bash
#!/bin/bash
cd /home/edunox/edunox
source venv/bin/activate

# Pull latest changes
git pull origin main

# Install any new requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Reload web app (you'll need to do this manually in dashboard)
echo "Please reload the web app in PythonAnywhere dashboard"
```

Make it executable:
```bash
chmod +x deploy_update.sh
```

## 📊 Step 9: Monitoring and Maintenance

### 9.1 Check Logs
- **Error logs**: Web tab → Error log
- **Server logs**: Web tab → Server log
- **Access logs**: Web tab → Access log

### 9.2 Regular Maintenance
```bash
# Weekly maintenance script
nano weekly_maintenance.sh
```

Add content:
```bash
#!/bin/bash
cd /home/edunox/edunox
source venv/bin/activate

# Update packages
pip install --upgrade -r requirements.txt

# Clean up old sessions
python manage.py clearsessions

# Check for issues
python manage.py check --deploy
```

## 🎯 Production URLs

- **Main Site**: https://edunox.pythonanywhere.com
- **Admin Panel**: https://edunox.pythonanywhere.com/admin/
- **Health Check**: https://edunox.pythonanywhere.com/health/

## 🔒 Security Checklist

- [ ] Database password is secure
- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] HTTPS redirect enabled
- [ ] ImageKit credentials secured
- [ ] Email credentials secured

## 🆘 Troubleshooting

### Common Issues:

1. **Import Errors**: Check virtual environment activation
2. **Database Connection**: Verify database credentials
3. **Static Files**: Run `collectstatic` and check mappings
4. **ImageKit Upload**: Check API credentials and permissions
5. **Email Issues**: Verify SMTP settings and app passwords

### Debug Commands:
```bash
# Check Django configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell

# View logs
tail -f /var/log/edunox.pythonanywhere.com.error.log
```

## 🎉 Deployment Complete!

Your Edunox GH platform is now live on PythonAnywhere with:
- ✅ Production-ready Django application
- ✅ MySQL database
- ✅ ImageKit media storage
- ✅ SSL/HTTPS enabled
- ✅ Email notifications configured
- ✅ Admin dashboard accessible

**Next Steps**: Test all functionality and configure any additional features as needed.
