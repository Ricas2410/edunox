from django.urls import path
from django.views.generic import TemplateView
from .views import HomeView, AboutView, FAQView, health_check

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('terms/', TemplateView.as_view(template_name='core/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='core/privacy.html'), name='privacy'),
    path('health/', health_check, name='health_check'),
]
