import logging
from django.core.mail import send_mail as django_send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import SiteConfiguration

logger = logging.getLogger(__name__)


def get_email_headers(config=None):
    """Get email headers to improve deliverability and prevent spam"""
    if not config:
        config = SiteConfiguration.get_config()

    headers = {
        'X-Mailer': 'Edunox GH v1.0',
        'X-Priority': '3',
        'X-MSMail-Priority': 'Normal',
        'Importance': 'Normal',
        'List-Unsubscribe': '<mailto:unsubscribe@deigratiams.edu.gh>',
        'Return-Path': config.default_from_email if config else 'info@deigratiams.edu.gh',
    }

    # Add authentication headers for better deliverability
    if config and config.default_from_email:
        domain = config.default_from_email.split('@')[1] if '@' in config.default_from_email else 'deigratiams.edu.gh'
        headers.update({
            'Message-ID': f'<{hash(str(headers))}@{domain}>',
            'Sender': config.default_from_email,
            'Reply-To': config.default_from_email,
        })

    return headers


def safe_send_mail(subject, message, from_email=None, recipient_list=None,
                   fail_silently=True, auth_user=None, auth_password=None,
                   connection=None, html_message=None):
    """
    Safe wrapper around Django's send_mail that prevents authentication errors
    from breaking the application flow.
    """
    try:
        # Get site configuration
        config = SiteConfiguration.get_config()
        
        # Check if email is properly configured
        if not _is_email_configured(config):
            logger.warning("Email not configured properly, skipping email send")
            if not fail_silently:
                logger.error(f"Failed to send email: {subject} - Email not configured")
            return False
        
        # Apply email settings
        config.apply_email_settings()
        
        # Use configured from_email if not provided
        if not from_email:
            from_email = config.default_from_email or settings.DEFAULT_FROM_EMAIL

        # Add headers to improve deliverability
        headers = get_email_headers(config)

        # Send email
        result = django_send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list or [],
            fail_silently=fail_silently,
            auth_user=auth_user,
            auth_password=auth_password,
            connection=connection,
            html_message=html_message,
            headers=headers
        )
        
        logger.info(f"Email sent successfully: {subject}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send email '{subject}': {str(e)}")
        
        if fail_silently:
            return False
        else:
            raise


def _is_email_configured(config):
    """Check if email configuration is complete"""
    if not config:
        return False
    
    # If using console backend, it's always "configured"
    if config.email_backend == 'django.core.mail.backends.console.EmailBackend':
        return True
    
    # For SMTP, check required fields
    if config.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
        return (config.email_host and 
               config.email_host_user and 
               config.email_host_password and
               config.default_from_email)
    
    # For other backends, assume they're configured
    return True


def send_html_email(subject, template_name, context, recipient_list, from_email=None, fail_silently=True):
    """
    Send HTML email with proper headers and fallback text version

    Args:
        subject (str): Email subject
        template_name (str): Template name (without .html extension)
        context (dict): Template context
        recipient_list (list): List of recipient emails
        from_email (str): Sender email (optional)
        fail_silently (bool): Whether to suppress exceptions

    Returns:
        bool: True if email was sent successfully
    """
    try:
        # Get email configuration
        config = SiteConfiguration.get_config()

        # Check if email is properly configured
        if not _is_email_configured(config):
            logger.warning("Email not configured properly, skipping email send")
            if not fail_silently:
                logger.error(f"Failed to send email: {subject} - Email not configured")
            return False

        # Apply email settings
        config.apply_email_settings()

        # Use configured from_email if not provided
        if not from_email:
            from_email = config.default_from_email or settings.DEFAULT_FROM_EMAIL

        # Add site configuration to context
        context['site_config'] = config
        context['site_url'] = getattr(settings, 'SITE_URL', 'https://deigratiams.edu.gh')

        # Render HTML content
        html_content = render_to_string(f'emails/{template_name}.html', context)

        # Create plain text version
        text_content = strip_tags(html_content)

        # Get headers for better deliverability
        headers = get_email_headers(config)

        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
            headers=headers
        )

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")

        # Send email
        result = email.send()

        if result:
            logger.info(f"HTML email sent successfully to {', '.join(recipient_list)}")
            return True
        else:
            logger.warning(f"HTML email sending returned 0 for recipients: {', '.join(recipient_list)}")
            return False

    except Exception as e:
        logger.error(f"Failed to send HTML email: {str(e)}")
        if not fail_silently:
            raise
        return False


def send_welcome_email(user):
    """Send welcome email safely using HTML template"""
    try:
        context = {
            'user': user,
        }

        return send_html_email(
            subject=f'Welcome to Edunox GH - {user.get_full_name() or user.username}',
            template_name='welcome',
            context=context,
            recipient_list=[user.email],
            fail_silently=True
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_verification_email_safe(user, verification_url):
    """Send email verification safely using HTML template"""
    try:
        context = {
            'user': user,
            'verification_url': verification_url,
        }

        return send_html_email(
            subject='Verify Your Email - Edunox GH',
            template_name='email_verification',
            context=context,
            recipient_list=[user.email],
            fail_silently=True
        )
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def test_email_configuration():
    """Test email configuration without sending actual email"""
    try:
        config = SiteConfiguration.get_config()
        
        if not config:
            return False, "Site configuration not found"
        
        if not _is_email_configured(config):
            return False, "Email configuration incomplete"
        
        # Test connection without sending email
        if config.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            import smtplib
            
            try:
                server = smtplib.SMTP(config.email_host, config.email_port)
                if config.email_use_tls:
                    server.starttls()
                server.login(config.email_host_user, config.email_host_password)
                server.quit()
                return True, "Email configuration is valid"
            except Exception as e:
                return False, f"SMTP connection failed: {str(e)}"
        
        return True, "Email configuration appears valid"
        
    except Exception as e:
        return False, f"Configuration test failed: {str(e)}"


class EmailConfigurationError(Exception):
    """Custom exception for email configuration errors"""
    pass
