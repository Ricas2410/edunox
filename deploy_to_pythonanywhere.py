#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
Run this script on PythonAnywhere after pulling changes from Git
"""
import os
import sys
import django
import subprocess

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False
    return True

def main():
    print("🚀 Starting PythonAnywhere Deployment...")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')
    django.setup()
    
    # Commands to run
    commands = [
        ("pip install -r requirements.txt", "Installing Python packages"),
        ("python manage.py collectstatic --noinput", "Collecting static files"),
        ("python manage.py migrate", "Running database migrations"),
        ("python manage.py clear_cache", "Clearing Django cache"),
        ("python manage.py test_database", "Testing database connection"),
        ("python manage.py seo_check", "Running SEO health check"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n⚠️  Warning: {description} failed but continuing...")
    
    print(f"\n📊 Deployment Summary:")
    print(f"✅ {success_count}/{len(commands)} commands completed successfully")
    
    if success_count == len(commands):
        print("\n🎉 Deployment completed successfully!")
        print("\n📝 Next steps:")
        print("1. Reload your web app in the PythonAnywhere Web tab")
        print("2. Check your website to ensure everything is working")
        print("3. Upload logo/favicon through Django admin if needed")
        print("4. Submit sitemap to Google Search Console")
        print("5. Set up Google Analytics tracking")
    else:
        print("\n⚠️  Some commands failed. Please check the errors above.")
    
    print("\n🔗 Useful links:")
    print("- Web app: https://edunox.pythonanywhere.com")
    print("- Admin: https://edunox.pythonanywhere.com/admin/")
    print("- Sitemap: https://edunox.pythonanywhere.com/sitemap.xml")
    print("- Robots.txt: https://edunox.pythonanywhere.com/robots.txt")
    print("- Google Search Console: https://search.google.com/search-console")
    print("- PageSpeed Insights: https://pagespeed.web.dev")

if __name__ == "__main__":
    main()
