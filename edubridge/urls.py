"""
URL configuration for edubridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap, index
from core.sitemaps import sitemaps
from core.views import robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('my-admin/', include(('dashboard.urls', 'dashboard'), namespace='admin_dashboard')),
    path('accounts/', include('allauth.urls')),
    path('auth/', include('accounts.urls')),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('resources/', include('resources.urls')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='user_dashboard')),
    path('contact/', include('contact.urls')),
    # SEO URLs
    path('sitemap.xml', index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
