"""
Performance optimization utilities for EduBridge Ghana
Includes caching, image optimization, and performance monitoring
"""

import time
import logging
from functools import wraps
from typing import Any, Callable, Optional
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.gzip import gzip_page
from django.db import connection
from django.core.files.storage import default_storage
from PIL import Image
import io

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.start_time = None
        self.queries_start = None
    
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.queries_start = len(connection.queries)
    
    def end(self, operation_name: str = "Operation"):
        """End monitoring and log results"""
        if self.start_time is None:
            return
        
        duration = time.time() - self.start_time
        query_count = len(connection.queries) - self.queries_start
        
        logger.info(f"{operation_name} completed in {duration:.3f}s with {query_count} queries")
        
        # Log slow operations
        if duration > 1.0:
            logger.warning(f"Slow operation detected: {operation_name} took {duration:.3f}s")
        
        # Log excessive queries
        if query_count > 10:
            logger.warning(f"High query count: {operation_name} executed {query_count} queries")
        
        return {
            'duration': duration,
            'query_count': query_count
        }


def performance_monitor(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                name = operation_name or f"{func.__module__}.{func.__name__}"
                monitor.end(name)
        
        return wrapper
    return decorator


def smart_cache(timeout: int = 300, key_prefix: str = '', vary_on: list = None):
    """
    Smart caching decorator with automatic cache invalidation
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
        vary_on: List of parameters to vary cache on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix, func.__name__]
            
            if vary_on:
                for param in vary_on:
                    if param in kwargs:
                        cache_key_parts.append(str(kwargs[param]))
            
            cache_key = ':'.join(filter(None, cache_key_parts))
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


class ImageOptimizer:
    """Optimize images for web delivery"""
    
    def __init__(self):
        self.quality = getattr(settings, 'IMAGE_QUALITY', 85)
        self.max_width = getattr(settings, 'IMAGE_MAX_WIDTH', 1920)
        self.max_height = getattr(settings, 'IMAGE_MAX_HEIGHT', 1080)
    
    def optimize_image(self, image_file, format='JPEG', quality=None):
        """
        Optimize an image file
        
        Args:
            image_file: Image file object
            format: Output format (JPEG, PNG, WebP)
            quality: Image quality (1-100)
        
        Returns:
            Optimized image file
        """
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if too large
            if image.width > self.max_width or image.height > self.max_height:
                image.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            save_kwargs = {'format': format, 'optimize': True}
            
            if format in ('JPEG', 'WebP'):
                save_kwargs['quality'] = quality or self.quality
            
            image.save(output, **save_kwargs)
            output.seek(0)
            
            return output
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return image_file
    
    def generate_responsive_images(self, image_file, sizes=[480, 768, 1024, 1920]):
        """
        Generate responsive image variants
        
        Args:
            image_file: Original image file
            sizes: List of widths to generate
        
        Returns:
            Dict of size -> optimized image
        """
        variants = {}
        
        try:
            image = Image.open(image_file)
            original_width = image.width
            
            for size in sizes:
                if size >= original_width:
                    continue
                
                # Calculate proportional height
                ratio = size / original_width
                height = int(image.height * ratio)
                
                # Resize image
                resized = image.copy()
                resized.thumbnail((size, height), Image.Resampling.LANCZOS)
                
                # Save variant
                output = io.BytesIO()
                resized.save(output, format='JPEG', quality=self.quality, optimize=True)
                output.seek(0)
                
                variants[size] = output
            
            return variants
            
        except Exception as e:
            logger.error(f"Responsive image generation failed: {e}")
            return {}


class CacheManager:
    """Manage application caching"""
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalidate cache keys matching a pattern"""
        try:
            # This is a simplified version - in production, use Redis with pattern matching
            cache.clear()
            logger.info(f"Cache invalidated for pattern: {pattern}")
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
    
    @staticmethod
    def warm_cache(cache_keys: list):
        """Pre-warm cache with common data"""
        for key, func in cache_keys:
            try:
                if not cache.get(key):
                    result = func()
                    cache.set(key, result, 3600)  # 1 hour default
                    logger.info(f"Cache warmed for key: {key}")
            except Exception as e:
                logger.error(f"Cache warming failed for {key}: {e}")
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics"""
        try:
            # This would need to be implemented based on your cache backend
            return {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# View decorators for performance
def cached_view(timeout=300, cache_key=None, vary_on_headers=None):
    """
    Decorator for caching views with custom options
    
    Usage:
    @cached_view(timeout=600, vary_on_headers=['Accept-Language'])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        # Apply gzip compression
        view_func = gzip_page(view_func)
        
        # Apply caching
        if cache_key:
            view_func = cache_page(timeout, key_prefix=cache_key)(view_func)
        else:
            view_func = cache_page(timeout)(view_func)
        
        # Apply vary headers
        if vary_on_headers:
            view_func = vary_on_headers(*vary_on_headers)(view_func)
        
        return view_func
    
    return decorator


def no_cache_view(view_func):
    """Decorator to prevent caching of a view"""
    return never_cache(gzip_page(view_func))


# Database optimization utilities
class QueryOptimizer:
    """Optimize database queries"""
    
    @staticmethod
    def prefetch_related_optimized(queryset, *lookups):
        """Optimized prefetch_related with select_related where appropriate"""
        return queryset.prefetch_related(*lookups)
    
    @staticmethod
    def select_related_optimized(queryset, *fields):
        """Optimized select_related"""
        return queryset.select_related(*fields)
    
    @staticmethod
    def bulk_create_optimized(model, objects, batch_size=1000):
        """Optimized bulk create with batching"""
        created_objects = []
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            created_objects.extend(model.objects.bulk_create(batch))
        return created_objects


# Performance middleware
class PerformanceMiddleware:
    """Middleware to monitor request performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start monitoring
        start_time = time.time()
        queries_start = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        query_count = len(connection.queries) - queries_start
        
        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-Response-Time'] = f"{duration:.3f}s"
            response['X-Query-Count'] = str(query_count)
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {duration:.3f}s with {query_count} queries"
            )
        
        return response


# Utility functions
def compress_response(content: str, compression_level: int = 6) -> bytes:
    """Compress response content"""
    import gzip
    return gzip.compress(content.encode('utf-8'), compresslevel=compression_level)


def minify_html(html: str) -> str:
    """Basic HTML minification"""
    import re
    
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove extra whitespace
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'>\s+<', '><', html)
    
    return html.strip()


def preload_critical_resources():
    """Generate preload links for critical resources"""
    critical_resources = [
        {'href': '/static/css/main.css', 'as': 'style'},
        {'href': '/static/js/main.js', 'as': 'script'},
        {'href': '/static/fonts/main.woff2', 'as': 'font', 'crossorigin': 'anonymous'},
    ]
    
    preload_links = []
    for resource in critical_resources:
        attrs = [f'{k}="{v}"' for k, v in resource.items()]
        preload_links.append(f'<link rel="preload" {" ".join(attrs)}>')
    
    return '\n'.join(preload_links)
