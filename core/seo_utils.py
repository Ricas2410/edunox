"""
SEO utilities for EduBridge Ghana
Provides tools for meta tags, structured data, and SEO optimization
"""

import json
import re
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.sites.models import Site
from django.utils import timezone


class SEOManager:
    """Manages SEO meta tags and structured data"""
    
    def __init__(self):
        self.site_name = getattr(settings, 'SITE_NAME', 'Edunox GH')
        self.site_description = getattr(settings, 'SITE_DESCRIPTION', 
                                      'Empowering Ghanaian students with educational support, university applications, and digital literacy training.')
        self.default_image = getattr(settings, 'DEFAULT_OG_IMAGE', '/static/images/og-default.jpg')
        self.site_url = self._get_site_url()
    
    def _get_site_url(self) -> str:
        """Get the current site URL"""
        try:
            site = Site.objects.get_current()
            protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
            return f"{protocol}://{site.domain}"
        except:
            return getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    def generate_meta_tags(
        self,
        title: str,
        description: str,
        keywords: Optional[List[str]] = None,
        image: Optional[str] = None,
        url: Optional[str] = None,
        article_data: Optional[Dict] = None,
        breadcrumbs: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate comprehensive meta tags for SEO
        
        Args:
            title: Page title
            description: Page description
            keywords: List of keywords
            image: Open Graph image URL
            url: Canonical URL
            article_data: Article-specific data (author, published_time, etc.)
            breadcrumbs: Breadcrumb navigation data
        
        Returns:
            HTML string with meta tags
        """
        
        # Prepare data
        full_title = f"{title} | {self.site_name}" if title != self.site_name else title
        image_url = image or self.default_image
        if image_url and not image_url.startswith('http'):
            image_url = f"{self.site_url}{image_url}"
        
        canonical_url = url or self.site_url
        if canonical_url and not canonical_url.startswith('http'):
            canonical_url = f"{self.site_url}{canonical_url}"
        
        # Basic meta tags
        meta_tags = [
            f'<title>{full_title}</title>',
            f'<meta name="description" content="{description}">',
            f'<link rel="canonical" href="{canonical_url}">',
        ]
        
        # Keywords
        if keywords:
            keywords_str = ', '.join(keywords)
            meta_tags.append(f'<meta name="keywords" content="{keywords_str}">')
        
        # Open Graph tags
        og_tags = [
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{description}">',
            f'<meta property="og:image" content="{image_url}">',
            f'<meta property="og:url" content="{canonical_url}">',
            f'<meta property="og:site_name" content="{self.site_name}">',
            '<meta property="og:type" content="website">',
        ]
        
        # Article-specific Open Graph tags
        if article_data:
            og_tags.append('<meta property="og:type" content="article">')
            if article_data.get('author'):
                og_tags.append(f'<meta property="article:author" content="{article_data["author"]}">')
            if article_data.get('published_time'):
                og_tags.append(f'<meta property="article:published_time" content="{article_data["published_time"]}">')
            if article_data.get('section'):
                og_tags.append(f'<meta property="article:section" content="{article_data["section"]}">')
        
        # Twitter Card tags
        twitter_tags = [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{description}">',
            f'<meta name="twitter:image" content="{image_url}">',
        ]
        
        # Twitter site handle if configured
        twitter_handle = getattr(settings, 'TWITTER_HANDLE', None)
        if twitter_handle:
            twitter_tags.append(f'<meta name="twitter:site" content="@{twitter_handle}">')
        
        # Combine all tags
        all_tags = meta_tags + og_tags + twitter_tags
        
        # Add structured data
        structured_data = self.generate_structured_data(
            title=title,
            description=description,
            url=canonical_url,
            image=image_url,
            breadcrumbs=breadcrumbs
        )
        
        if structured_data:
            all_tags.append(structured_data)
        
        return mark_safe('\n'.join(all_tags))
    
    def generate_structured_data(
        self,
        title: str,
        description: str,
        url: str,
        image: str,
        breadcrumbs: Optional[List[Dict]] = None,
        organization_data: Optional[Dict] = None
    ) -> str:
        """Generate JSON-LD structured data"""
        
        # Base structured data
        structured_data = {
            "@context": "https://schema.org",
            "@graph": []
        }
        
        # Website data
        website_data = {
            "@type": "WebSite",
            "@id": f"{self.site_url}/#website",
            "url": self.site_url,
            "name": self.site_name,
            "description": self.site_description,
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{self.site_url}/search?q={{search_term_string}}",
                "query-input": "required name=search_term_string"
            }
        }
        structured_data["@graph"].append(website_data)
        
        # Organization data
        org_data = organization_data or {
            "@type": "EducationalOrganization",
            "@id": f"{self.site_url}/#organization",
            "name": self.site_name,
            "url": self.site_url,
            "description": self.site_description,
            "logo": {
                "@type": "ImageObject",
                "url": f"{self.site_url}/static/images/logo.png"
            },
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "Ghana",
                "addressLocality": "Accra"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+233-XX-XXX-XXXX",
                "contactType": "customer service",
                "email": "info@edubridge.com"
            },
            "sameAs": [
                "https://facebook.com/edubridgeghana",
                "https://twitter.com/edubridgeghana",
                "https://linkedin.com/company/edubridgeghana"
            ]
        }
        structured_data["@graph"].append(org_data)
        
        # WebPage data
        webpage_data = {
            "@type": "WebPage",
            "@id": f"{url}/#webpage",
            "url": url,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{self.site_url}/#website"},
            "about": {"@id": f"{self.site_url}/#organization"},
            "primaryImageOfPage": {
                "@type": "ImageObject",
                "url": image
            }
        }
        structured_data["@graph"].append(webpage_data)
        
        # Breadcrumbs
        if breadcrumbs:
            breadcrumb_data = {
                "@type": "BreadcrumbList",
                "itemListElement": []
            }
            
            for i, crumb in enumerate(breadcrumbs, 1):
                breadcrumb_data["itemListElement"].append({
                    "@type": "ListItem",
                    "position": i,
                    "name": crumb["name"],
                    "item": crumb["url"] if crumb.get("url") else None
                })
            
            structured_data["@graph"].append(breadcrumb_data)
        
        return f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'
    
    def generate_service_structured_data(self, service) -> str:
        """Generate structured data for services"""
        service_data = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service.name,
            "description": service.description,
            "provider": {
                "@type": "EducationalOrganization",
                "name": self.site_name,
                "url": self.site_url
            },
            "serviceType": service.category.name,
            "offers": {
                "@type": "Offer",
                "price": str(service.price),
                "priceCurrency": "GHS",
                "availability": "https://schema.org/InStock"
            }
        }
        
        if service.image:
            service_data["image"] = f"{self.site_url}{service.image.url}"
        
        return f'<script type="application/ld+json">{json.dumps(service_data, indent=2)}</script>'
    
    def generate_article_structured_data(self, resource) -> str:
        """Generate structured data for educational resources"""
        article_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": resource.title,
            "description": resource.description,
            "author": {
                "@type": "Organization",
                "name": self.site_name
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.site_url}/static/images/logo.png"
                }
            },
            "datePublished": resource.created_at.isoformat(),
            "dateModified": resource.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.site_url}{reverse('resources:detail', args=[resource.pk])}"
            }
        }
        
        if resource.image:
            article_data["image"] = f"{self.site_url}{resource.image.url}"
        
        return f'<script type="application/ld+json">{json.dumps(article_data, indent=2)}</script>'


# Template tags for easy use in templates
def get_seo_manager():
    """Get SEO manager instance"""
    return SEOManager()


def generate_page_meta(title, description, **kwargs):
    """Template function to generate meta tags"""
    seo_manager = SEOManager()
    return seo_manager.generate_meta_tags(title, description, **kwargs)


def generate_breadcrumbs_data(breadcrumbs):
    """Generate breadcrumbs structured data"""
    seo_manager = SEOManager()
    return seo_manager.generate_structured_data(
        title="",
        description="",
        url="",
        image="",
        breadcrumbs=breadcrumbs
    )


class AdvancedSEOManager(SEOManager):
    """Advanced SEO manager with additional features for global market competition"""

    def __init__(self):
        super().__init__()
        self.target_keywords = [
            'university application Ghana',
            'free university education',
            'University of the People Ghana',
            'scholarship application Ghana',
            'digital literacy training',
            'online education Ghana',
            'educational consultancy Ghana',
            'affordable higher education',
            'UoPeople application help',
            'Ghana education support'
        ]

    def optimize_content_for_seo(self, content: str, target_keyword: str = None) -> Dict[str, Any]:
        """
        Analyze and optimize content for SEO

        Args:
            content: The content to analyze
            target_keyword: Primary keyword to optimize for

        Returns:
            Dictionary with SEO analysis and recommendations
        """
        if not content:
            return {'error': 'No content provided'}

        # Basic content analysis
        word_count = len(content.split())
        char_count = len(content)

        # Keyword density analysis
        keyword_analysis = {}
        if target_keyword:
            keyword_count = content.lower().count(target_keyword.lower())
            keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            keyword_analysis = {
                'keyword': target_keyword,
                'count': keyword_count,
                'density': round(keyword_density, 2),
                'optimal_density': keyword_density >= 1 and keyword_density <= 3
            }

        # Readability analysis (simplified)
        sentences = len(re.split(r'[.!?]+', content))
        avg_words_per_sentence = word_count / sentences if sentences > 0 else 0

        # SEO recommendations
        recommendations = []
        if word_count < 300:
            recommendations.append("Consider adding more content (aim for 300+ words)")
        if target_keyword and keyword_analysis['density'] < 1:
            recommendations.append(f"Increase usage of target keyword '{target_keyword}'")
        if target_keyword and keyword_analysis['density'] > 3:
            recommendations.append(f"Reduce keyword density for '{target_keyword}' to avoid over-optimization")
        if avg_words_per_sentence > 20:
            recommendations.append("Consider shorter sentences for better readability")

        return {
            'word_count': word_count,
            'character_count': char_count,
            'sentence_count': sentences,
            'avg_words_per_sentence': round(avg_words_per_sentence, 1),
            'keyword_analysis': keyword_analysis,
            'recommendations': recommendations,
            'seo_score': self._calculate_seo_score(word_count, keyword_analysis, avg_words_per_sentence)
        }

    def _calculate_seo_score(self, word_count: int, keyword_analysis: Dict, avg_words_per_sentence: float) -> int:
        """Calculate a simple SEO score out of 100"""
        score = 0

        # Word count score (30 points)
        if word_count >= 300:
            score += 30
        elif word_count >= 150:
            score += 20
        elif word_count >= 50:
            score += 10

        # Keyword optimization score (40 points)
        if keyword_analysis and keyword_analysis.get('optimal_density'):
            score += 40
        elif keyword_analysis and keyword_analysis.get('density', 0) > 0:
            score += 20

        # Readability score (30 points)
        if avg_words_per_sentence <= 15:
            score += 30
        elif avg_words_per_sentence <= 20:
            score += 20
        elif avg_words_per_sentence <= 25:
            score += 10

        return min(score, 100)

    def generate_meta_description(self, content: str, max_length: int = 160) -> str:
        """
        Generate an optimized meta description from content

        Args:
            content: Source content
            max_length: Maximum length for meta description

        Returns:
            Optimized meta description
        """
        if not content:
            return self.site_description[:max_length]

        # Clean content
        clean_content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()  # Normalize whitespace

        # Find the first sentence or paragraph
        sentences = re.split(r'[.!?]+', clean_content)
        if sentences and len(sentences[0]) <= max_length:
            return sentences[0].strip()

        # Truncate at word boundary
        if len(clean_content) <= max_length:
            return clean_content

        truncated = clean_content[:max_length].rsplit(' ', 1)[0]
        return f"{truncated}..."

    def generate_schema_faq(self, faqs: List[Dict[str, str]]) -> str:
        """
        Generate FAQ schema markup

        Args:
            faqs: List of FAQ items with 'question' and 'answer' keys

        Returns:
            JSON-LD schema markup for FAQs
        """
        if not faqs:
            return ""

        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }

        for faq in faqs:
            if 'question' in faq and 'answer' in faq:
                faq_item = {
                    "@type": "Question",
                    "name": faq['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq['answer']
                    }
                }
                faq_schema["mainEntity"].append(faq_item)

        return f'<script type="application/ld+json">{json.dumps(faq_schema, indent=2)}</script>'

    def generate_local_business_schema(self) -> str:
        """Generate local business schema for Ghana location"""
        business_schema = {
            "@context": "https://schema.org",
            "@type": "EducationalOrganization",
            "name": self.site_name,
            "description": self.site_description,
            "url": self.site_url,
            "logo": f"{self.site_url}/static/images/Edunox-logo.png",
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "Ghana",
                "addressLocality": "Accra",
                "addressRegion": "Greater Accra"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "5.6037",
                "longitude": "-0.1870"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+233-XX-XXX-XXXX",
                "contactType": "customer service",
                "email": "info@Edunox.com",
                "availableLanguage": ["English", "Twi"]
            },
            "areaServed": {
                "@type": "Country",
                "name": "Ghana"
            },
            "serviceType": [
                "University Application Support",
                "Scholarship Guidance",
                "Digital Literacy Training",
                "Educational Consultancy"
            ]
        }

        return f'<script type="application/ld+json">{json.dumps(business_schema, indent=2)}</script>'
