from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import os


class BaseModel(models.Model):
    """Base model with common fields for all models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EncryptedCharField(models.CharField):
    """Custom field for encrypting sensitive data like passwords"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_encryption_key(self):
        """Get or create encryption key"""
        key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
        if not key:
            # Generate a key if not exists (for development)
            key = Fernet.generate_key()
            # In production, this should be set in environment variables
        return key

    def encrypt_value(self, value):
        """Encrypt the value"""
        if not value:
            return value

        try:
            key = self.get_encryption_key()
            f = Fernet(key)
            encrypted_value = f.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_value).decode()
        except Exception:
            # If encryption fails, return original value (for backward compatibility)
            return value

    def decrypt_value(self, value):
        """Decrypt the value"""
        if not value:
            return value

        try:
            key = self.get_encryption_key()
            f = Fernet(key)
            decoded_value = base64.urlsafe_b64decode(value.encode())
            decrypted_value = f.decrypt(decoded_value)
            return decrypted_value.decode()
        except Exception:
            # If decryption fails, assume it's not encrypted (backward compatibility)
            return value

    def from_db_value(self, value, expression, connection):
        """Decrypt when loading from database"""
        return self.decrypt_value(value)

    def to_python(self, value):
        """Convert to Python value"""
        return self.decrypt_value(value)

    def get_prep_value(self, value):
        """Encrypt before saving to database"""
        return self.encrypt_value(value)


class SiteConfiguration(BaseModel):
    """Site-wide configuration settings"""
    site_name = models.CharField(max_length=100, default="Edunox GH")
    site_description = models.TextField(default="Your gateway to affordable higher education and digital empowerment.")
    contact_email = models.EmailField(default="info@edubridge.com")
    contact_phone = models.CharField(max_length=20, default="+233 XX XXX XXXX")
    address = models.TextField(default="Accra, Ghana")

    # Logo and Branding
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, help_text="Main site logo")
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True, help_text="Site favicon (.ico or .png)")
    banner_image = models.ImageField(upload_to='branding/', blank=True, null=True, help_text="Hero section banner image")
    hero_image = models.ImageField(upload_to='branding/', blank=True, null=True, help_text="Main hero section image")

    # Default Service Category Images (fallbacks when services don't have images)
    university_default_image = models.ImageField(upload_to='defaults/', blank=True, null=True, help_text="Default image for University services")
    scholarship_default_image = models.ImageField(upload_to='defaults/', blank=True, null=True, help_text="Default image for Scholarship services")
    digital_default_image = models.ImageField(upload_to='defaults/', blank=True, null=True, help_text="Default image for Digital Skills services")
    consultancy_default_image = models.ImageField(upload_to='defaults/', blank=True, null=True, help_text="Default image for Consultancy services")
    general_default_image = models.ImageField(upload_to='defaults/', blank=True, null=True, help_text="General default image for services")

    # Page Background Images
    about_page_image = models.ImageField(upload_to='pages/', blank=True, null=True, help_text="About page hero image")
    services_page_image = models.ImageField(upload_to='pages/', blank=True, null=True, help_text="Services page hero image")
    resources_page_image = models.ImageField(upload_to='pages/', blank=True, null=True, help_text="Resources page hero image")
    contact_page_image = models.ImageField(upload_to='pages/', blank=True, null=True, help_text="Contact page hero image")

    # About Page Section Images
    about_mission_image = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Our Mission section image")
    about_approach_image = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Our Approach section image")

    # External Links
    library_url = models.URLField(blank=True, help_text="External library/resources URL (optional)")
    library_opens_new_tab = models.BooleanField(default=True, help_text="Open library link in new tab")
    jobs_url = models.URLField(blank=True, help_text="External jobs/careers URL (optional)")
    jobs_opens_new_tab = models.BooleanField(default=True, help_text="Open jobs link in new tab")

    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Advanced Settings
    maintenance_mode = models.BooleanField(default=False, help_text="Put site in maintenance mode")
    allow_user_registration = models.BooleanField(default=True, help_text="Allow new user registration")
    require_email_verification = models.BooleanField(default=True, help_text="Require email verification for new users")
    google_analytics_id = models.CharField(max_length=50, blank=True, help_text="Google Analytics tracking ID")
    custom_header_scripts = models.TextField(blank=True, help_text="Custom scripts to include in <head>")
    custom_footer_scripts = models.TextField(blank=True, help_text="Custom scripts to include before </body>")

    # Branding Settings
    primary_color = models.CharField(max_length=7, default="#3B82F6", help_text="Primary brand color (hex)")
    secondary_color = models.CharField(max_length=7, default="#10B981", help_text="Secondary brand color (hex)")
    accent_color = models.CharField(max_length=7, default="#F59E0B", help_text="Accent brand color (hex)")
    custom_css = models.TextField(blank=True, help_text="Custom CSS styles")

    # Email Settings
    EMAIL_BACKEND_CHOICES = [
        ('django.core.mail.backends.smtp.EmailBackend', 'SMTP'),
        ('django.core.mail.backends.console.EmailBackend', 'Console (Development)'),
        ('django.core.mail.backends.dummy.EmailBackend', 'Dummy (No Email)'),
    ]

    email_backend = models.CharField(max_length=100, choices=EMAIL_BACKEND_CHOICES,
                                   default='django.core.mail.backends.console.EmailBackend',
                                   help_text="Email backend to use")
    email_host = models.CharField(max_length=100, blank=True, help_text="SMTP server host (e.g., smtp.gmail.com)")
    email_port = models.IntegerField(default=587, help_text="SMTP server port")
    email_use_tls = models.BooleanField(default=True, help_text="Use TLS encryption")
    email_use_ssl = models.BooleanField(default=False, help_text="Use SSL encryption")
    email_host_user = models.CharField(max_length=100, blank=True, help_text="SMTP username/email")
    email_host_password = EncryptedCharField(max_length=255, blank=True, help_text="SMTP password/app password (encrypted)")
    default_from_email = models.EmailField(blank=True, help_text="Default 'from' email address")

    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configurations"
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_config(cls):
        """Get the active site configuration"""
        return cls.objects.filter(is_active=True).first() or cls.objects.create()

    def apply_email_settings(self):
        """Apply email settings to Django settings"""
        from django.conf import settings

        # Only apply if we have a complete SMTP configuration
        if self.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            if not (self.email_host and self.email_host_user and self.email_host_password):
                return  # Don't apply incomplete SMTP settings

        # Apply settings
        if self.email_backend:
            settings.EMAIL_BACKEND = self.email_backend
        if self.email_host:
            settings.EMAIL_HOST = self.email_host
        if self.email_port:
            settings.EMAIL_PORT = self.email_port
        if self.email_use_tls is not None:
            settings.EMAIL_USE_TLS = self.email_use_tls
        if self.email_use_ssl is not None:
            settings.EMAIL_USE_SSL = self.email_use_ssl
        if self.email_host_user:
            settings.EMAIL_HOST_USER = self.email_host_user
        if self.email_host_password:
            settings.EMAIL_HOST_PASSWORD = self.email_host_password
        if self.default_from_email:
            settings.DEFAULT_FROM_EMAIL = self.default_from_email
            settings.SERVER_EMAIL = self.default_from_email

        # Add timeout and other settings for better reliability
        settings.EMAIL_TIMEOUT = 30
        settings.EMAIL_USE_LOCALTIME = True

        # Apply provider-specific optimizations
        if self.email_host and 'zoho.com' in self.email_host.lower():
            self._apply_zoho_optimizations()

    def _apply_zoho_optimizations(self):
        """Apply Zoho-specific email optimizations"""
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)

        # Zoho-specific timeout settings
        settings.EMAIL_TIMEOUT = 60  # Longer timeout for Zoho

        # Ensure proper authentication
        if not self.email_host_user or not self.email_host_password:
            logger.warning("Zoho requires both username and password")

        # Ensure TLS is enabled for Zoho
        if not self.email_use_tls:
            logger.warning("Zoho strongly recommends TLS encryption")

        # Verify port configuration
        if self.email_port not in [587, 465]:
            logger.warning(f"Zoho typically uses port 587 (TLS) or 465 (SSL), current: {self.email_port}")

        # Ensure from email matches authenticated user for better deliverability
        if self.email_host_user and self.default_from_email:
            if self.email_host_user != self.default_from_email:
                logger.warning("For better deliverability, from_email should match authenticated user")

        logger.debug("Applied Zoho-specific optimizations")


class NavigationMenuItem(BaseModel):
    """Admin-controlled navigation menu items"""
    MENU_TYPE_CHOICES = [
        ('services', 'Services Dropdown'),
        ('main', 'Main Navigation'),
    ]

    LINK_TYPE_CHOICES = [
        ('internal', 'Internal Page'),
        ('external', 'External URL'),
        ('service', 'Service Page'),
    ]

    menu_type = models.CharField(max_length=20, choices=MENU_TYPE_CHOICES, default='services')
    name = models.CharField(max_length=100, help_text="Display name for the menu item")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fas fa-university)")
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='internal')

    # Link options
    internal_url_name = models.CharField(max_length=100, blank=True, help_text="Django URL name (e.g., services:list)")
    external_url = models.URLField(blank=True, help_text="External URL (for external links)")
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, blank=True, null=True, help_text="Link to specific service")

    # Display options
    opens_new_tab = models.BooleanField(default=False, help_text="Open link in new tab")
    order = models.PositiveIntegerField(default=0, help_text="Order for display (lower numbers first)")
    is_active = models.BooleanField(default=True)

    # Grouping for services dropdown
    group_name = models.CharField(max_length=100, blank=True, help_text="Group name for services dropdown (e.g., 'University Applications')")

    class Meta:
        ordering = ['menu_type', 'order', 'name']
        verbose_name = "Navigation Menu Item"
        verbose_name_plural = "Navigation Menu Items"

    def __str__(self):
        return f"{self.get_menu_type_display()}: {self.name}"

    def get_url(self):
        """Get the URL for this menu item"""
        if self.link_type == 'external':
            return self.external_url
        elif self.link_type == 'service' and self.service:
            return self.service.get_absolute_url()
        elif self.link_type == 'internal' and self.internal_url_name:
            try:
                from django.urls import reverse
                return reverse(self.internal_url_name)
            except:
                return '#'
        return '#'


class FAQ(BaseModel):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question
