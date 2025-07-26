"""
Performance optimization settings and utilities for EduBridge Ghana
"""

# Cache settings for different content types
CACHE_TIMEOUTS = {
    'static_pages': 60 * 60,  # 1 hour for static pages like About, FAQ
    'home_page': 60 * 15,     # 15 minutes for home page (dynamic content)
    'service_list': 60 * 10,  # 10 minutes for service listings
    'service_detail': 60 * 20, # 20 minutes for individual services
    'user_dashboard': 60 * 5,  # 5 minutes for user dashboard
    'admin_data': 60 * 2,     # 2 minutes for admin data
}

# Database optimization settings
DATABASE_OPTIMIZATIONS = {
    'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
    'CONN_HEALTH_CHECKS': True,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'MIN_CONNS': 5,
    }
}

# Static file optimization
STATIC_FILE_OPTIMIZATIONS = {
    'STATICFILES_STORAGE': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    'WHITENOISE_USE_FINDERS': True,
    'WHITENOISE_AUTOREFRESH': False,  # Disable in production
    'WHITENOISE_MAX_AGE': 31536000,  # 1 year cache
}

# Media file optimization
MEDIA_FILE_OPTIMIZATIONS = {
    'IMAGE_QUALITY': 85,
    'IMAGE_MAX_WIDTH': 1920,
    'IMAGE_MAX_HEIGHT': 1080,
    'THUMBNAIL_SIZES': {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (600, 600),
    }
}

# Security optimizations
SECURITY_OPTIMIZATIONS = {
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'X_FRAME_OPTIONS': 'DENY',
    'SECURE_HSTS_SECONDS': 31536000,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
}

# Session optimization
SESSION_OPTIMIZATIONS = {
    'SESSION_COOKIE_AGE': 86400,  # 24 hours
    'SESSION_SAVE_EVERY_REQUEST': False,
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
}

# Email optimization
EMAIL_OPTIMIZATIONS = {
    'EMAIL_TIMEOUT': 30,
    'EMAIL_USE_LOCALTIME': True,
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
}

# Logging optimization
LOGGING_OPTIMIZATIONS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Template optimization
TEMPLATE_OPTIMIZATIONS = {
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'core.context_processors.site_config',
        ],
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
    },
}

# Middleware optimization (order matters for performance)
OPTIMIZED_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.PerformanceMiddleware',
]

# File upload optimization
FILE_UPLOAD_OPTIMIZATIONS = {
    'FILE_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'DATA_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'FILE_UPLOAD_PERMISSIONS': 0o644,
    'FILE_UPLOAD_DIRECTORY_PERMISSIONS': 0o755,
}

# URL optimization
URL_OPTIMIZATIONS = {
    'APPEND_SLASH': True,
    'PREPEND_WWW': False,
}

def apply_optimizations(settings_module):
    """Apply all optimizations to Django settings"""
    
    # Apply cache settings
    if hasattr(settings_module, 'CACHES'):
        settings_module.CACHES['default']['TIMEOUT'] = CACHE_TIMEOUTS['static_pages']
    
    # Apply database optimizations
    if hasattr(settings_module, 'DATABASES'):
        for db_config in settings_module.DATABASES.values():
            db_config.update(DATABASE_OPTIMIZATIONS)
    
    # Apply static file optimizations
    for key, value in STATIC_FILE_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply security optimizations
    for key, value in SECURITY_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply session optimizations
    for key, value in SESSION_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply email optimizations
    for key, value in EMAIL_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply file upload optimizations
    for key, value in FILE_UPLOAD_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply URL optimizations
    for key, value in URL_OPTIMIZATIONS.items():
        setattr(settings_module, key, value)
    
    # Apply middleware optimization
    settings_module.MIDDLEWARE = OPTIMIZED_MIDDLEWARE
    
    # Apply template optimization
    if hasattr(settings_module, 'TEMPLATES'):
        settings_module.TEMPLATES[0].update(TEMPLATE_OPTIMIZATIONS)
    
    # Apply logging optimization
    settings_module.LOGGING = LOGGING_OPTIMIZATIONS

# Performance monitoring utilities
def get_performance_metrics():
    """Get current performance metrics"""
    from django.db import connection
    from django.core.cache import cache
    import psutil
    import os
    
    metrics = {
        'database_queries': len(connection.queries),
        'cache_hits': getattr(cache, '_cache_hits', 0),
        'cache_misses': getattr(cache, '_cache_misses', 0),
        'memory_usage': psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024,  # MB
        'cpu_usage': psutil.cpu_percent(),
    }
    
    return metrics

def clear_all_caches():
    """Clear all application caches"""
    from django.core.cache import cache
    from django.core.management import call_command
    
    # Clear Django cache
    cache.clear()
    
    # Clear template cache
    call_command('clearcache')
    
    return True
