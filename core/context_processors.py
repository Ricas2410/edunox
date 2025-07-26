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
    except Exception:
        # Return empty config if there's an error
        return {
            'site_config': None
        }
