"""
Comprehensive SEO Check Management Command
Quick SEO health check and recommendations for EduLink GH
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import Client
from core.models import SiteConfiguration
from services.models import Service, ServiceCategory
from resources.models import Resource, ResourceCategory


class Command(BaseCommand):
    help = 'Quick SEO health check with actionable recommendations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 SEO Health Check for EduLink GH\n'))
        
        # Core checks
        self.check_basic_config()
        self.check_sitemap()
        self.check_robots()
        self.check_content()
        self.provide_recommendations()

    def check_basic_config(self):
        self.stdout.write(self.style.WARNING('📋 Basic Configuration:'))
        
        # Site framework
        try:
            site = Site.objects.get_current()
            self.stdout.write(f"✅ Site: {site.domain}")
        except:
            self.stdout.write("❌ Site framework not configured")
        
        # Site configuration
        try:
            config = SiteConfiguration.get_config()
            self.stdout.write(f"✅ Site name: {config.site_name}")
            
            if config.logo:
                self.stdout.write("✅ Logo uploaded")
            else:
                self.stdout.write("⚠️  No logo uploaded")
                
            if config.favicon:
                self.stdout.write("✅ Favicon uploaded")
            else:
                self.stdout.write("⚠️  No favicon uploaded")
                
        except Exception as e:
            self.stdout.write(f"❌ Site config error: {e}")
        
        # Settings check
        if hasattr(settings, 'SITE_NAME'):
            self.stdout.write(f"✅ SITE_NAME: {settings.SITE_NAME}")
        else:
            self.stdout.write("⚠️  SITE_NAME not set")
            
        if hasattr(settings, 'SITE_URL'):
            self.stdout.write(f"✅ SITE_URL: {settings.SITE_URL}")
        else:
            self.stdout.write("⚠️  SITE_URL not set")
        
        self.stdout.write("")

    def check_sitemap(self):
        self.stdout.write(self.style.WARNING('🗺️  Sitemap:'))
        
        try:
            from core.sitemaps import sitemaps
            total_urls = 0
            
            for name, sitemap_class in sitemaps.items():
                try:
                    sitemap = sitemap_class()
                    items = list(sitemap.items())
                    count = len(items)
                    total_urls += count
                    self.stdout.write(f"   {name}: {count} URLs")
                except Exception as e:
                    self.stdout.write(f"   {name}: Error - {str(e)}")
            
            self.stdout.write(f"✅ Total URLs: {total_urls}")
            
            # Test accessibility
            client = Client()
            response = client.get('/sitemap.xml')
            if response.status_code == 200:
                self.stdout.write("✅ Sitemap accessible")
            else:
                self.stdout.write(f"❌ Sitemap returns {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"❌ Sitemap error: {e}")
        
        self.stdout.write("")

    def check_robots(self):
        self.stdout.write(self.style.WARNING('🤖 Robots.txt:'))
        
        try:
            client = Client()
            response = client.get('/robots.txt')
            
            if response.status_code == 200:
                content = response.content.decode()
                self.stdout.write("✅ Robots.txt accessible")
                
                if 'Sitemap:' in content:
                    self.stdout.write("✅ Sitemap reference found")
                else:
                    self.stdout.write("⚠️  No sitemap reference")
                    
            else:
                self.stdout.write(f"❌ Robots.txt returns {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"❌ Robots.txt error: {e}")
        
        self.stdout.write("")

    def check_content(self):
        self.stdout.write(self.style.WARNING('📝 Content Analysis:'))
        
        # Services
        services = Service.objects.filter(is_active=True)
        services_with_desc = services.exclude(description='').exclude(description__isnull=True)

        self.stdout.write(f"📊 Services: {services.count()} total")
        self.stdout.write(f"   With descriptions: {services_with_desc.count()}")

        # Resources
        resources = Resource.objects.filter(is_published=True)
        resources_with_content = resources.exclude(content='').exclude(content__isnull=True)

        self.stdout.write(f"📊 Resources: {resources.count()} total")
        self.stdout.write(f"   With content: {resources_with_content.count()}")
        
        # Categories
        service_cats = ServiceCategory.objects.filter(is_active=True).count()
        resource_cats = ResourceCategory.objects.filter(is_active=True).count()
        
        self.stdout.write(f"📊 Categories: {service_cats} services, {resource_cats} resources")
        
        self.stdout.write("")

    def provide_recommendations(self):
        self.stdout.write(self.style.SUCCESS('💡 Priority Recommendations:'))
        
        recommendations = [
            "1. 🔥 Upload logo and favicon (Django admin)",
            "2. 🔥 Add meta descriptions to all content",
            "3. 🔥 Submit sitemap to Google Search Console",
            "4. 🔶 Set up Google Analytics tracking",
            "5. 🔶 Optimize images with alt text",
            "6. 🔶 Add internal links between content",
            "7. 🔷 Create regular blog content",
            "8. 🔷 Add schema markup for services",
        ]
        
        for rec in recommendations:
            self.stdout.write(f"   {rec}")
        
        self.stdout.write(f"\n🎯 Quick Actions:")
        self.stdout.write("   • Visit /sitemap.xml")
        self.stdout.write("   • Visit /robots.txt") 
        self.stdout.write("   • Test at PageSpeed Insights")
        self.stdout.write("   • Submit to Google Search Console")
        
        self.stdout.write(self.style.SUCCESS(f"\n✨ Run 'python manage.py seo_audit --full' for detailed analysis"))
