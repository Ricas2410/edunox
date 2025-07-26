"""
SEO Audit Management Command
Analyzes the site's SEO performance and provides recommendations
"""

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from django.contrib.sites.models import Site
from core.seo_utils import AdvancedSEOManager
from services.models import Service
from resources.models import Resource
from core.models import FAQ
import requests
from urllib.parse import urljoin


class Command(BaseCommand):
    help = 'Perform SEO audit of the website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Specific URL to audit (optional)',
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full site audit',
        )

    def handle(self, *args, **options):
        self.seo_manager = AdvancedSEOManager()
        self.client = Client()
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting SEO Audit for EduBridge Ghana')
        )
        
        if options['url']:
            self.audit_single_url(options['url'])
        elif options['full']:
            self.audit_full_site()
        else:
            self.audit_key_pages()
        
        self.stdout.write(
            self.style.SUCCESS('✅ SEO Audit completed!')
        )

    def audit_single_url(self, url):
        """Audit a single URL"""
        self.stdout.write(f"\n📄 Auditing URL: {url}")
        
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                self.analyze_page(url, response.content.decode('utf-8'))
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error: HTTP {response.status_code}")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error accessing URL: {str(e)}")
            )

    def audit_key_pages(self):
        """Audit key pages of the site"""
        key_urls = [
            '/',
            '/about/',
            '/services/',
            '/resources/',
            '/contact/',
            '/faq/',
        ]
        
        self.stdout.write("\n📋 Auditing key pages...")
        
        for url in key_urls:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.analyze_page(url, response.content.decode('utf-8'))
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {url}: HTTP {response.status_code}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {url}: {str(e)}")
                )

    def audit_full_site(self):
        """Perform full site audit"""
        self.stdout.write("\n🌐 Performing full site audit...")
        
        # Audit key pages
        self.audit_key_pages()
        
        # Audit services
        self.stdout.write("\n🛠️  Auditing service pages...")
        services = Service.objects.filter(is_active=True)[:10]  # Limit for demo
        for service in services:
            url = reverse('services:detail', args=[service.pk])
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.analyze_page(url, response.content.decode('utf-8'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Service {service.name}: {str(e)}")
                )
        
        # Audit resources
        self.stdout.write("\n📚 Auditing resource pages...")
        resources = Resource.objects.filter(is_published=True)[:10]  # Limit for demo
        for resource in resources:
            url = reverse('resources:detail', args=[resource.pk])
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.analyze_page(url, response.content.decode('utf-8'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Resource {resource.title}: {str(e)}")
                )

    def analyze_page(self, url, content):
        """Analyze a single page for SEO"""
        import re
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
        except:
            self.stdout.write(
                self.style.ERROR(f"❌ Could not parse HTML for {url}")
            )
            return
        
        # Extract basic elements
        title = soup.find('title')
        title_text = title.text.strip() if title else "No title"
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
        
        h1_tags = soup.find_all('h1')
        h1_count = len(h1_tags)
        
        # Extract text content
        text_content = soup.get_text()
        
        # Analyze with SEO manager
        seo_analysis = self.seo_manager.optimize_content_for_seo(
            text_content, 
            target_keyword="university application Ghana"
        )
        
        # Display results
        self.stdout.write(f"\n📄 {url}")
        self.stdout.write(f"   Title: {title_text[:60]}{'...' if len(title_text) > 60 else ''}")
        self.stdout.write(f"   Title Length: {len(title_text)} chars")
        
        if meta_desc_text:
            self.stdout.write(f"   Meta Description: {meta_desc_text[:60]}{'...' if len(meta_desc_text) > 60 else ''}")
            self.stdout.write(f"   Meta Desc Length: {len(meta_desc_text)} chars")
        else:
            self.stdout.write("   ❌ Missing meta description")
        
        self.stdout.write(f"   H1 Tags: {h1_count}")
        self.stdout.write(f"   Word Count: {seo_analysis['word_count']}")
        self.stdout.write(f"   SEO Score: {seo_analysis['seo_score']}/100")
        
        # Recommendations
        if seo_analysis['recommendations']:
            self.stdout.write("   📝 Recommendations:")
            for rec in seo_analysis['recommendations']:
                self.stdout.write(f"      • {rec}")
        
        # Check for common SEO issues
        issues = []
        if len(title_text) > 60:
            issues.append("Title too long (>60 chars)")
        if len(title_text) < 30:
            issues.append("Title too short (<30 chars)")
        if len(meta_desc_text) > 160:
            issues.append("Meta description too long (>160 chars)")
        if len(meta_desc_text) < 120:
            issues.append("Meta description too short (<120 chars)")
        if h1_count == 0:
            issues.append("Missing H1 tag")
        if h1_count > 1:
            issues.append("Multiple H1 tags")
        
        if issues:
            self.stdout.write("   ⚠️  Issues:")
            for issue in issues:
                self.stdout.write(f"      • {issue}")
        
        # Check for images without alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            self.stdout.write(f"   ⚠️  {len(images_without_alt)} images missing alt text")
