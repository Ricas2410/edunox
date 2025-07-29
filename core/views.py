from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.db import connection
from .models import SiteConfiguration, FAQ
from services.models import Service


# Cache for 5 minutes instead of 15 to allow faster updates
@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache for 5 minutes
class HomeView(TemplateView):
    """Home page view"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_config'] = SiteConfiguration.get_config()
        context['faqs'] = FAQ.objects.filter(is_active=True)[:6]
        context['featured_services'] = Service.objects.filter(is_active=True, is_featured=True)[:3]
        return context


@method_decorator(cache_page(60 * 30), name='dispatch')  # Cache for 30 minutes
class AboutView(TemplateView):
    """About page view"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_config'] = SiteConfiguration.get_config()
        return context


@method_decorator(cache_page(60 * 60), name='dispatch')  # Cache for 1 hour
class FAQView(TemplateView):
    """FAQ page view"""
    template_name = 'core/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_config'] = SiteConfiguration.get_config()
        context['faqs'] = FAQ.objects.filter(is_active=True)
        return context


def health_check(request):
    """Health check endpoint for deployment monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': '2024-01-15T10:30:00Z'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': '2024-01-15T10:30:00Z'
        }, status=500)


def robots_txt(request):
    """Generate robots.txt file"""
    from django.conf import settings

    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Sitemaps",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        "",
        "# Disallow admin areas",
        "Disallow: /admin/",
        "Disallow: /my-admin/",
        "Disallow: /dashboard/",
        "",
        "# Allow important pages",
        "Allow: /services/",
        "Allow: /resources/",
        "Allow: /about/",
        "Allow: /contact/",
        "",
        "# Crawl delay",
        "Crawl-delay: 1",
    ]

    return HttpResponse('\n'.join(lines), content_type='text/plain')
