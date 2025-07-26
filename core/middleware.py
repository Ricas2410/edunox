"""
Middleware for Edunox GH
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import SiteConfiguration


class DynamicEmailSettingsMiddleware(MiddlewareMixin):
    """
    Middleware to apply email settings from SiteConfiguration
    This ensures email settings are always up-to-date from admin panel
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Apply email settings from database configuration"""
        try:
            config = SiteConfiguration.get_config()
            if config and self._is_email_config_complete(config):
                # Only apply if not using console backend from environment
                from django.conf import settings
                env_backend = getattr(settings, 'EMAIL_BACKEND', '')
                if 'console' not in env_backend.lower():
                    config.apply_email_settings()
        except Exception:
            # If there's any error, continue with default settings
            pass

        return None

    def _is_email_config_complete(self, config):
        """Check if email configuration is complete and valid"""
        if not config.email_backend:
            return False

        # For SMTP backend, require all necessary fields
        if config.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            return (config.email_host and
                   config.email_host_user and
                   config.email_host_password and
                   config.default_from_email)

        # For other backends, allow them through
        return True


class ProfilePictureMiddleware(MiddlewareMixin):
    """
    Middleware to ensure user profile picture is available in all templates
    """
    
    def process_request(self, request):
        """Add user profile picture to request context"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                request.user.profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
            except:
                request.user.profile_picture_url = None
        
        return None
