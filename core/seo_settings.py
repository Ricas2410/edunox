"""
SEO Configuration Settings for Edunox GH
Professional SEO settings for global market competition
"""

# Core SEO Settings
SEO_SETTINGS = {
    # Site Information
    'SITE_NAME': 'Edunox GH',
    'SITE_TAGLINE': 'Your Gateway to Affordable Higher Education',
    'SITE_DESCRIPTION': 'Empowering underserved students in Ghana with access to free and affordable university education through outreach, digital literacy support, and educational consultancy.',
    
    # Primary Keywords (for global competition)
    'PRIMARY_KEYWORDS': [
        'university application Ghana',
        'University of the People Ghana',
        'free university education',
        'scholarship application Ghana',
        'digital literacy training Ghana',
        'educational consultancy Ghana',
        'UoPeople application help',
        'online education Ghana',
        'affordable higher education Ghana',
        'Ghana education support'
    ],
    
    # Long-tail Keywords
    'LONG_TAIL_KEYWORDS': [
        'how to apply to University of the People from Ghana',
        'free university education opportunities in Ghana',
        'scholarship opportunities for Ghanaian students',
        'digital literacy training programs Ghana',
        'educational consultancy services Accra',
        'online university application help Ghana',
        'affordable higher education options Ghana',
        'university application assistance Ghana',
        'free online degree programs Ghana',
        'educational support services Ghana'
    ],
    
    # Geographic Targeting
    'TARGET_LOCATIONS': [
        'Ghana',
        'Accra',
        'Kumasi',
        'Tamale',
        'Cape Coast',
        'Takoradi',
        'Ho',
        'Koforidua',
        'Sunyani',
        'Wa'
    ],
    
    # Competitor Analysis Keywords
    'COMPETITOR_KEYWORDS': [
        'Ghana education portal',
        'university admission Ghana',
        'scholarship portal Ghana',
        'education consultancy Ghana',
        'online learning Ghana',
        'higher education Ghana',
        'university guidance Ghana',
        'education support Ghana'
    ],
    
    # Content Categories for SEO
    'CONTENT_CATEGORIES': {
        'university_applications': {
            'title': 'University Applications',
            'keywords': ['university application', 'admission process', 'application requirements'],
            'description': 'Complete guide to university applications in Ghana and abroad'
        },
        'scholarships': {
            'title': 'Scholarships & Financial Aid',
            'keywords': ['scholarship', 'financial aid', 'education funding'],
            'description': 'Find and apply for scholarships and financial aid opportunities'
        },
        'digital_literacy': {
            'title': 'Digital Literacy Training',
            'keywords': ['digital skills', 'computer training', 'online learning'],
            'description': 'Essential digital skills for modern education and career success'
        },
        'career_guidance': {
            'title': 'Career Guidance',
            'keywords': ['career advice', 'job opportunities', 'professional development'],
            'description': 'Professional career guidance and development resources'
        }
    },
    
    # Social Media Settings
    'SOCIAL_MEDIA': {
        'facebook': {
            'page_id': 'edubridgeghana',
            'app_id': 'YOUR_FACEBOOK_APP_ID'
        },
        'twitter': {
            'handle': '@edubridgeghana',
            'site': '@edubridgeghana'
        },
        'linkedin': {
            'company': 'edubridge-ghana'
        },
        'instagram': {
            'handle': '@edubridgeghana'
        }
    },
    
    # Technical SEO Settings
    'TECHNICAL_SEO': {
        'enable_amp': False,  # Accelerated Mobile Pages
        'enable_pwa': True,   # Progressive Web App
        'enable_schema': True,  # Schema.org markup
        'enable_breadcrumbs': True,
        'enable_sitemap': True,
        'enable_robots_txt': True,
        'canonical_urls': True,
        'meta_robots': 'index, follow',
        'crawl_delay': 1
    },
    
    # Performance Settings
    'PERFORMANCE': {
        'enable_compression': True,
        'enable_caching': True,
        'optimize_images': True,
        'minify_css': True,
        'minify_js': True,
        'lazy_load_images': True,
        'preload_critical_resources': True
    },
    
    # Analytics & Tracking
    'ANALYTICS': {
        'google_analytics_id': 'GA_MEASUREMENT_ID',
        'google_tag_manager_id': 'GTM_CONTAINER_ID',
        'facebook_pixel_id': 'FB_PIXEL_ID',
        'microsoft_clarity_id': 'CLARITY_PROJECT_ID',
        'hotjar_id': 'HOTJAR_SITE_ID'
    },
    
    # Local SEO Settings
    'LOCAL_SEO': {
        'business_name': 'Edunox GH',
        'business_type': 'Educational Organization',
        'address': {
            'street': 'TBD',
            'city': 'Accra',
            'region': 'Greater Accra',
            'postal_code': 'TBD',
            'country': 'Ghana'
        },
        'coordinates': {
            'latitude': '5.6037',
            'longitude': '-0.1870'
        },
        'phone': '+233-XX-XXX-XXXX',
        'email': 'info@Edunox.com',
        'hours': {
            'monday': '09:00-17:00',
            'tuesday': '09:00-17:00',
            'wednesday': '09:00-17:00',
            'thursday': '09:00-17:00',
            'friday': '09:00-17:00',
            'saturday': '09:00-13:00',
            'sunday': 'closed'
        }
    },
    
    # Content Strategy
    'CONTENT_STRATEGY': {
        'blog_posting_frequency': 'weekly',
        'target_word_count': 800,
        'keyword_density_target': 2.5,  # percentage
        'internal_links_per_post': 3,
        'external_links_per_post': 2,
        'images_per_post': 2,
        'meta_description_length': 155,
        'title_length': 60
    },
    
    # International SEO
    'INTERNATIONAL_SEO': {
        'default_language': 'en',
        'supported_languages': ['en'],  # Can expand to include local languages
        'hreflang_enabled': False,  # Enable when adding multiple languages
        'geo_targeting': 'GH'  # Ghana
    }
}

# SEO URL Patterns for better structure
SEO_URL_PATTERNS = {
    'services': '/services/{category}/{service-name}/',
    'resources': '/resources/{category}/{resource-title}/',
    'blog': '/blog/{year}/{month}/{post-slug}/',
    'pages': '/{page-slug}/',
    'categories': '/{category-type}/{category-slug}/'
}

# Meta Templates for Dynamic Pages
META_TEMPLATES = {
    'service_detail': {
        'title': '{service_name} - Educational Services | Edunox GH',
        'description': 'Get professional help with {service_name}. {service_description} Contact Edunox GH for expert educational support.',
        'keywords': '{service_keywords}, educational services Ghana, {service_category}'
    },
    'resource_detail': {
        'title': '{resource_title} | Educational Resources - Edunox GH',
        'description': '{resource_description} Free educational resource from Edunox GH.',
        'keywords': '{resource_keywords}, educational resources, Ghana education'
    },
    'category_page': {
        'title': '{category_name} Services & Resources | Edunox GH',
        'description': 'Explore our {category_name} services and resources. {category_description}',
        'keywords': '{category_keywords}, {category_name} Ghana, educational services'
    }
}

# Rich Snippets Configuration
RICH_SNIPPETS = {
    'organization': True,
    'local_business': True,
    'educational_organization': True,
    'service': True,
    'article': True,
    'faq': True,
    'breadcrumbs': True,
    'review': True,
    'course': True
}

# Content Optimization Rules
CONTENT_OPTIMIZATION = {
    'min_word_count': 300,
    'max_word_count': 2000,
    'keyword_density_min': 1.0,
    'keyword_density_max': 3.0,
    'heading_structure': True,  # Enforce proper H1-H6 structure
    'alt_text_required': True,
    'internal_links_min': 2,
    'external_links_max': 5,
    'meta_description_required': True,
    'focus_keyword_required': True
}
