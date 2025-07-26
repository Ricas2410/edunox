from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db import connection
from .models import SiteConfiguration, FAQ
from services.models import Service


@method_decorator(cache_page(60 * 15), name='dispatch')  # Cache for 15 minutes
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
