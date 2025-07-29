"""
SEO template tags for EduBridge Ghana
Provides template tags for meta tags, structured data, and SEO optimization
"""

from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
from django.forms.widgets import Widget
from ..seo_utils import SEOManager

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_meta_tags(context, title, description, **kwargs):
    """
    Generate comprehensive SEO meta tags
    
    Usage:
    {% seo_meta_tags "Page Title" "Page description" keywords="keyword1,keyword2" image="/path/to/image.jpg" %}
    """
    request = context.get('request')
    seo_manager = SEOManager()
    
    # Process keywords
    keywords = kwargs.get('keywords', '')
    if keywords:
        keywords = [k.strip() for k in keywords.split(',')]
    else:
        keywords = None
    
    # Get current URL
    if request:
        current_url = request.build_absolute_uri()
    else:
        current_url = kwargs.get('url', '')
    
    return seo_manager.generate_meta_tags(
        title=title,
        description=description,
        keywords=keywords,
        image=kwargs.get('image'),
        url=current_url,
        article_data=kwargs.get('article_data'),
        breadcrumbs=kwargs.get('breadcrumbs')
    )


@register.simple_tag
def service_structured_data(service):
    """Generate structured data for a service"""
    seo_manager = SEOManager()
    return mark_safe(seo_manager.generate_service_structured_data(service))


@register.simple_tag
def resource_structured_data(resource):
    """Generate structured data for a resource/article"""
    seo_manager = SEOManager()
    return mark_safe(seo_manager.generate_article_structured_data(resource))


@register.simple_tag(takes_context=True)
def breadcrumbs_structured_data(context, breadcrumbs):
    """
    Generate structured data for breadcrumbs
    
    Usage:
    {% breadcrumbs_structured_data breadcrumbs %}
    
    Where breadcrumbs is a list of dicts: [{"name": "Home", "url": "/"}, ...]
    """
    seo_manager = SEOManager()
    return mark_safe(seo_manager.generate_structured_data(
        title="",
        description="",
        url="",
        image="",
        breadcrumbs=breadcrumbs
    ))


@register.inclusion_tag('seo/breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context, breadcrumbs):
    """
    Render breadcrumbs navigation
    
    Usage:
    {% render_breadcrumbs breadcrumbs %}
    """
    return {
        'breadcrumbs': breadcrumbs,
        'request': context.get('request')
    }


@register.simple_tag
def canonical_url(url_name, *args, **kwargs):
    """
    Generate canonical URL for a view
    
    Usage:
    {% canonical_url 'services:detail' service.pk %}
    """
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except:
        return ''


@register.simple_tag(takes_context=True)
def current_absolute_url(context):
    """Get the current absolute URL"""
    request = context.get('request')
    if request:
        return request.build_absolute_uri()
    return ''


@register.simple_tag
def meta_keywords(*keywords):
    """
    Generate meta keywords tag
    
    Usage:
    {% meta_keywords "education" "ghana" "university" %}
    """
    if keywords:
        keywords_str = ', '.join(keywords)
        return mark_safe(f'<meta name="keywords" content="{keywords_str}">')
    return ''


@register.simple_tag
def og_image(image_url, default=None):
    """
    Generate Open Graph image meta tag
    
    Usage:
    {% og_image service.image.url %}
    """
    if not image_url and default:
        image_url = default
    
    if image_url:
        # Ensure absolute URL
        if not image_url.startswith('http'):
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            image_url = f"{site_url}{image_url}"
        
        return mark_safe(f'<meta property="og:image" content="{image_url}">')
    return ''


@register.simple_tag
def twitter_card(card_type='summary_large_image'):
    """
    Generate Twitter Card meta tag
    
    Usage:
    {% twitter_card "summary" %}
    """
    return mark_safe(f'<meta name="twitter:card" content="{card_type}">')


@register.simple_tag
def robots_meta(index=True, follow=True, archive=True, snippet=True):
    """
    Generate robots meta tag
    
    Usage:
    {% robots_meta index=False follow=True %}
    """
    directives = []
    
    directives.append('index' if index else 'noindex')
    directives.append('follow' if follow else 'nofollow')
    
    if not archive:
        directives.append('noarchive')
    
    if not snippet:
        directives.append('nosnippet')
    
    content = ', '.join(directives)
    return mark_safe(f'<meta name="robots" content="{content}">')


@register.simple_tag
def hreflang_tags(alternate_urls):
    """
    Generate hreflang tags for international SEO
    
    Usage:
    {% hreflang_tags alternate_urls %}
    
    Where alternate_urls is a dict: {"en": "https://example.com/en/", "fr": "https://example.com/fr/"}
    """
    if not alternate_urls:
        return ''
    
    tags = []
    for lang, url in alternate_urls.items():
        tags.append(f'<link rel="alternate" hreflang="{lang}" href="{url}">')
    
    return mark_safe('\n'.join(tags))


@register.filter
def truncate_meta_description(text, length=160):
    """
    Truncate text for meta description (optimal length: 150-160 characters)
    
    Usage:
    {{ description|truncate_meta_description:150 }}
    """
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    # Truncate at word boundary
    truncated = text[:length].rsplit(' ', 1)[0]
    return f"{truncated}..."


@register.filter
def seo_title(text, max_length=60):
    """
    Optimize title for SEO (optimal length: 50-60 characters)
    
    Usage:
    {{ title|seo_title:55 }}
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return f"{truncated}..."


@register.simple_tag
def preload_resource(href, resource_type='style', crossorigin=None):
    """
    Generate resource preload link
    
    Usage:
    {% preload_resource "/static/css/main.css" "style" %}
    {% preload_resource "/static/fonts/font.woff2" "font" "anonymous" %}
    """
    attrs = [
        'rel="preload"',
        f'href="{href}"',
        f'as="{resource_type}"'
    ]
    
    if crossorigin:
        attrs.append(f'crossorigin="{crossorigin}"')
    
    return mark_safe(f'<link {" ".join(attrs)}>')


@register.simple_tag
def dns_prefetch(domain):
    """
    Generate DNS prefetch link
    
    Usage:
    {% dns_prefetch "https://fonts.googleapis.com" %}
    """
    return mark_safe(f'<link rel="dns-prefetch" href="{domain}">')


@register.simple_tag
def preconnect(domain, crossorigin=False):
    """
    Generate preconnect link
    
    Usage:
    {% preconnect "https://fonts.gstatic.com" True %}
    """
    attrs = ['rel="preconnect"', f'href="{domain}"']
    
    if crossorigin:
        attrs.append('crossorigin')
    
    return mark_safe(f'<link {" ".join(attrs)}>')


@register.simple_tag(takes_context=True)
def json_ld_website(context):
    """Generate JSON-LD for website"""
    request = context.get('request')
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    if request:
        site_url = f"{request.scheme}://{request.get_host()}"
    
    website_data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": getattr(settings, 'SITE_NAME', 'Edunox GH'),
        "url": site_url,
        "description": getattr(settings, 'SITE_DESCRIPTION', 'Educational support services in Ghana'),
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{site_url}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    
    import json
    return mark_safe(f'<script type="application/ld+json">{json.dumps(website_data, indent=2)}</script>')


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field widget

    Usage:
    {{ form.field|add_class:"form-control" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    elif hasattr(field, 'field') and hasattr(field.field, 'widget'):
        # Handle bound field
        attrs = field.field.widget.attrs.copy()
        if 'class' in attrs:
            attrs['class'] += f' {css_class}'
        else:
            attrs['class'] = css_class
        return field.as_widget(attrs=attrs)
    else:
        # Fallback for other field types
        return field


@register.simple_tag
def site_logo():
    """
    Get the site logo URL

    Usage:
    {% site_logo %}
    """
    from ..models import SiteConfiguration
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)

    try:
        config = SiteConfiguration.get_config()
        if config and config.logo:
            logger.debug(f"Using admin uploaded logo: {config.logo.url}")
            return config.logo.url

        # Use ImageKit URL as fallback if available
        if hasattr(settings, 'IMAGEKIT_URL_ENDPOINT'):
            fallback_url = f"{settings.IMAGEKIT_URL_ENDPOINT}/default-logo.png"
            logger.debug(f"Using ImageKit fallback: {fallback_url}")
            return fallback_url

        # Safe fallback - use a data URL for a simple logo
        logger.debug("Using SVG data URL fallback")
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iIzM5ODNGNiIvPgo8dGV4dCB4PSIyMCIgeT0iMjYiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5FRzwvdGV4dD4KPHN2Zz4K"
    except Exception as e:
        logger.error(f"Error in site_logo template tag: {e}")
        # Return a safe fallback even if there's an error
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iIzM5ODNGNiIvPgo8dGV4dCB4PSIyMCIgeT0iMjYiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5FRzwvdGV4dD4KPHN2Zz4K"


@register.simple_tag
def site_favicon():
    """
    Get the site favicon URL

    Usage:
    {% site_favicon %}
    """
    from ..models import SiteConfiguration
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)

    try:
        config = SiteConfiguration.get_config()
        if config and config.favicon:
            logger.debug(f"Using admin uploaded favicon: {config.favicon.url}")
            return config.favicon.url

        # Use ImageKit URL as fallback if available
        if hasattr(settings, 'IMAGEKIT_URL_ENDPOINT'):
            fallback_url = f"{settings.IMAGEKIT_URL_ENDPOINT}/favicon.ico"
            logger.debug(f"Using ImageKit favicon fallback: {fallback_url}")
            return fallback_url

        # Safe fallback - use a data URL for a simple favicon
        logger.debug("Using SVG data URL favicon fallback")
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNCIgZmlsbD0iIzM5ODNGNiIvPgo8dGV4dCB4PSIxNiIgeT0iMjEiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5FRzwvdGV4dD4KPHN2Zz4K"
    except Exception as e:
        logger.error(f"Error in site_favicon template tag: {e}")
        # Return a safe fallback even if there's an error
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNCIgZmlsbD0iIzM5ODNGNiIvPgo8dGV4dCB4PSIxNiIgeT0iMjEiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5FRzwvdGV4dD4KPHN2Zz4K"


@register.simple_tag(takes_context=True)
def comprehensive_seo_tags(context, title=None, description=None, keywords=None, image=None, **kwargs):
    """
    Generate comprehensive SEO meta tags for any page

    Usage:
    {% comprehensive_seo_tags title="Page Title" description="Page description" keywords="keyword1,keyword2" %}
    """
    from django.conf import settings
    from ..models import SiteConfiguration

    request = context.get('request')
    config = SiteConfiguration.get_config()

    # Build title
    if not title:
        title = getattr(settings, 'SITE_NAME', 'EduLink GH')
    else:
        site_name = config.site_name if config else getattr(settings, 'SITE_NAME', 'EduLink GH')
        title = f"{title} | {site_name}"

    # Build description
    if not description:
        description = config.site_description if config else getattr(settings, 'DEFAULT_META_DESCRIPTION', '')

    # Build keywords
    if not keywords:
        keywords = getattr(settings, 'DEFAULT_META_KEYWORDS', '')

    # Build image
    if not image:
        if config and config.logo:
            image = config.logo.url
        else:
            image = site_logo()

    # Build canonical URL
    canonical_url = request.build_absolute_uri() if request else ''

    # Generate meta tags
    meta_tags = []

    # Basic meta tags
    meta_tags.append(f'<title>{title}</title>')
    meta_tags.append(f'<meta name="description" content="{description}">')
    if keywords:
        meta_tags.append(f'<meta name="keywords" content="{keywords}">')

    # Open Graph tags
    meta_tags.append(f'<meta property="og:title" content="{title}">')
    meta_tags.append(f'<meta property="og:description" content="{description}">')
    meta_tags.append(f'<meta property="og:type" content="website">')
    if canonical_url:
        meta_tags.append(f'<meta property="og:url" content="{canonical_url}">')
    if image:
        meta_tags.append(f'<meta property="og:image" content="{image}">')

    # Twitter Card tags
    meta_tags.append(f'<meta name="twitter:card" content="summary_large_image">')
    meta_tags.append(f'<meta name="twitter:title" content="{title}">')
    meta_tags.append(f'<meta name="twitter:description" content="{description}">')
    if image:
        meta_tags.append(f'<meta name="twitter:image" content="{image}">')

    # Canonical URL
    if canonical_url:
        meta_tags.append(f'<link rel="canonical" href="{canonical_url}">')

    return mark_safe('\n'.join(meta_tags))


@register.filter
def first_name_only(user):
    """
    Extract only the first name from user, handling cases where first_name might contain multiple words

    Usage:
    {{ user|first_name_only }}
    """
    if hasattr(user, 'first_name') and user.first_name:
        # Split by space and take only the first word
        first_word = user.first_name.split()[0] if user.first_name.split() else user.first_name
        return first_word
    elif hasattr(user, 'username') and user.username:
        # If no first name, use first word of username
        return user.username.split()[0] if user.username.split() else user.username
    else:
        return "User"


@register.simple_tag
def site_banner():
    """
    Get the site banner image URL

    Usage:
    {% site_banner %}
    """
    from ..models import SiteConfiguration
    config = SiteConfiguration.get_config()
    if config and config.banner_image:
        return config.banner_image.url
    return None  # No fallback for banner


@register.simple_tag
def site_config():
    """
    Get the complete site configuration object

    Usage:
    {% site_config as config %}
    """
    from ..models import SiteConfiguration
    return SiteConfiguration.get_config()


@register.simple_tag
def site_hero_image():
    """
    Get the site hero image URL

    Usage:
    {% site_hero_image %}
    """
    from ..models import SiteConfiguration
    config = SiteConfiguration.get_config()
    if config and config.hero_image:
        return config.hero_image.url
    return "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"  # Fallback


@register.simple_tag
def default_service_image(category_name):
    """
    Get default image for service category

    Usage:
    {% default_service_image "University" %}
    """
    from ..models import SiteConfiguration
    config = SiteConfiguration.get_config()

    if not config:
        # Return online fallbacks
        if 'University' in category_name:
            return "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        elif 'Scholarship' in category_name:
            return "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        elif 'Digital' in category_name:
            return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        elif 'Consultancy' in category_name:
            return "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        else:
            return "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"

    # Check for admin-uploaded images first
    if 'University' in category_name and config.university_default_image:
        return config.university_default_image.url
    elif 'Scholarship' in category_name and config.scholarship_default_image:
        return config.scholarship_default_image.url
    elif 'Digital' in category_name and config.digital_default_image:
        return config.digital_default_image.url
    elif 'Consultancy' in category_name and config.consultancy_default_image:
        return config.consultancy_default_image.url
    elif config.general_default_image:
        return config.general_default_image.url

    # Fallback to online images
    if 'University' in category_name:
        return "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    elif 'Scholarship' in category_name:
        return "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    elif 'Digital' in category_name:
        return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    elif 'Consultancy' in category_name:
        return "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    else:
        return "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
