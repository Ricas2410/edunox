"""
Context processors for Edunox GH
Makes site configuration available to all templates
"""

from .models import SiteConfiguration


def site_config(request):
    """
    Add site configuration to all template contexts

    Usage in templates:
    {{ site_config.contact_email }}
    {{ site_config.contact_phone }}
    {{ site_config.logo.url }}
    """
    try:
        config = SiteConfiguration.get_config()
        return {
            'site_config': config
        }
    except Exception as e:
        # Log the error for debugging but don't break the template
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load site configuration: {e}")

        # Return a minimal config object to prevent template errors
        class MinimalConfig:
            def __init__(self):
                self.site_name = "EduLink GH"
                self.contact_email = "info@edulink.com"
                self.contact_phone = "+233 XX XXX XXXX"
                self.logo = None
                self.favicon = None

            def __getattr__(self, name):
                # Return None for any missing attributes
                return None

        return {
            'site_config': MinimalConfig()
        }
