#!/usr/bin/env python3
"""
Quick fix script for logo/favicon issues on PythonAnywhere
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')
django.setup()

from django.core.cache import cache
from core.models import SiteConfiguration
from django.conf import settings

def main():
    print("🔧 Fixing logo/favicon issues on production...")
    
    # Clear cache
    print("\n1. Clearing cache...")
    try:
        cache.clear()
        print("✅ Cache cleared successfully")
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
    
    # Check site configuration
    print("\n2. Checking site configuration...")
    try:
        config = SiteConfiguration.get_config()
        print(f"✅ Site config loaded: {config.site_name}")
        
        if config.logo:
            print(f"✅ Logo found: {config.logo.url}")
        else:
            print("⚠️  No logo uploaded in admin")
            
        if config.favicon:
            print(f"✅ Favicon found: {config.favicon.url}")
        else:
            print("⚠️  No favicon uploaded in admin")
            
    except Exception as e:
        print(f"❌ Error checking site config: {e}")
    
    # Check ImageKit settings
    print("\n3. Checking ImageKit configuration...")
    try:
        if hasattr(settings, 'IMAGEKIT_URL_ENDPOINT'):
            print(f"✅ ImageKit endpoint: {settings.IMAGEKIT_URL_ENDPOINT}")
        else:
            print("❌ ImageKit endpoint not configured")
            
        if hasattr(settings, 'USE_IMAGEKIT'):
            print(f"✅ Use ImageKit: {getattr(settings, 'USE_IMAGEKIT', False)}")
        else:
            print("⚠️  USE_IMAGEKIT setting not found")
            
    except Exception as e:
        print(f"❌ Error checking ImageKit: {e}")
    
    # Check DEBUG mode
    print(f"\n4. Debug mode: {settings.DEBUG}")
    if settings.DEBUG:
        print("⚠️  WARNING: DEBUG=True in production!")
    else:
        print("✅ Production mode (DEBUG=False)")
    
    print("\n🎯 Recommendations:")
    print("1. Upload logo and favicon through Django admin")
    print("2. Clear browser cache and hard refresh (Ctrl+F5)")
    print("3. Reload your PythonAnywhere web app")
    print("4. Check browser developer tools for any 404 errors")

if __name__ == "__main__":
    main()
