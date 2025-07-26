"""
SEO Sitemaps for EduBridge Ghana
Generates XML sitemaps for better search engine indexing
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:about',
            'core:faq',
            'services:list',
            'resources:list',
            'contact:contact',
            'accounts:register_steps',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()


class ServiceSitemap(Sitemap):
    """Sitemap for services"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        from services.models import Service
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('services:detail', args=[obj.pk])


class ServiceCategorySitemap(Sitemap):
    """Sitemap for service categories"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        from services.models import ServiceCategory
        return ServiceCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('services:category', args=[obj.pk])


class ResourceSitemap(Sitemap):
    """Sitemap for educational resources"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        from resources.models import Resource
        return Resource.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('resources:detail', args=[obj.pk])


class ResourceCategorySitemap(Sitemap):
    """Sitemap for resource categories"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        from resources.models import ResourceCategory
        return ResourceCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('resources:category', args=[obj.pk])


# Enhanced sitemap with better organization
class NewsSitemap(Sitemap):
    """Sitemap for news/blog articles (if implemented)"""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        from resources.models import Resource
        # Get recent articles/news (last 30 days)
        from datetime import timedelta
        from django.utils import timezone
        recent_date = timezone.now() - timedelta(days=30)
        return Resource.objects.filter(
            is_published=True,
            resource_type='ARTICLE',
            published_at__gte=recent_date
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('resources:detail', args=[obj.pk])


class ImageSitemap(Sitemap):
    """Sitemap for images"""
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        from services.models import Service
        from resources.models import Resource

        items = []
        # Add service images
        for service in Service.objects.filter(is_active=True, image__isnull=False):
            items.append(('service', service))

        # Add resource images
        for resource in Resource.objects.filter(is_published=True, featured_image__isnull=False):
            items.append(('resource', resource))

        return items

    def location(self, item):
        item_type, obj = item
        if item_type == 'service':
            return reverse('services:detail', args=[obj.pk])
        elif item_type == 'resource':
            return reverse('resources:detail', args=[obj.pk])
        return '/'

    def lastmod(self, item):
        item_type, obj = item
        return obj.updated_at


# Sitemap index with enhanced organization
sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'service_categories': ServiceCategorySitemap,
    'resources': ResourceSitemap,
    'resource_categories': ResourceCategorySitemap,
    'news': NewsSitemap,
    'images': ImageSitemap,
}
