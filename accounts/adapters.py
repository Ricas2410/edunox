"""
Custom allauth adapters for Edunox GH
Provides safe email handling to prevent authentication errors from breaking login
"""

import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
from core.email_utils import safe_send_mail
from core.models import SiteConfiguration

logger = logging.getLogger(__name__)


class SafeAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter that handles email sending safely
    Prevents email authentication errors from breaking the login process
    """
    
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to use our safe email sending mechanism
        """
        try:
            # Check if email is configured
            config = SiteConfiguration.get_config()
            if not self._is_email_configured(config):
                logger.warning(f"Email not configured, skipping email: {template_prefix}")
                return
            
            # Get email subject and message
            subject = self.render_mail(template_prefix, email, context)['subject']
            message = self.render_mail(template_prefix, email, context)['body']
            
            # Send email safely
            safe_send_mail(
                subject=subject,
                message=message,
                recipient_list=[email],
                fail_silently=True  # Don't break login if email fails
            )
            
        except Exception as e:
            logger.error(f"Failed to send email {template_prefix} to {email}: {str(e)}")
            # Don't raise exception - just log and continue
    
    def _is_email_configured(self, config):
        """Check if email configuration is complete"""
        if not config:
            return False
        
        # Console backend is always "configured" for development
        if config.email_backend == 'django.core.mail.backends.console.EmailBackend':
            return True
        
        # For SMTP, check required fields
        if config.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            return (config.email_host and 
                   config.email_host_user and 
                   config.email_host_password and
                   config.default_from_email)
        
        return True
    
    def is_open_for_signup(self, request):
        """
        Check if signup is allowed
        """
        config = SiteConfiguration.get_config()
        if config and hasattr(config, 'allow_user_registration'):
            return config.allow_user_registration
        return True  # Default to allowing registration
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user and handle any post-save operations safely
        """
        user = super().save_user(request, user, form, commit)
        
        if commit:
            try:
                # Send welcome email safely (won't break if email fails)
                from core.email_utils import send_welcome_email
                send_welcome_email(user)
            except Exception as e:
                logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
                # Don't raise - user creation should succeed even if email fails
        
        return user
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation safely
        """
        try:
            # Check if email verification is required
            config = SiteConfiguration.get_config()
            if config and hasattr(config, 'require_email_verification') and not config.require_email_verification:
                logger.info("Email verification disabled, skipping confirmation email")
                return
            
            # Use parent method but catch any exceptions
            super().send_confirmation_mail(request, emailconfirmation, signup)
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")
            # Don't raise - allow user to continue without email verification
    
    def get_login_redirect_url(self, request):
        """
        Get login redirect URL
        """
        # Check if user needs to complete profile
        if hasattr(request.user, 'profile') and not request.user.profile.is_verified:
            # Redirect to profile completion instead of dashboard
            return '/dashboard/profile/'
        
        return super().get_login_redirect_url(request)
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """
        Add message with better error handling
        """
        try:
            super().add_message(request, level, message_template, message_context, extra_tags)
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            # Don't break the flow if message adding fails
