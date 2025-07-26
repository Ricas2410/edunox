"""
Core functionality tests for EduBridge Ghana
Tests for views, models, and utilities
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from unittest.mock import patch, Mock
from core.email_service import EmailService
from core.seo_utils import SEOManager
from core.performance import PerformanceMonitor, ImageOptimizer

User = get_user_model()


class CoreViewsTestCase(TestCase):
    """Test core views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EduBridge Ghana')
    
    def test_about_page_loads(self):
        """Test that about page loads successfully"""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')
    
    def test_faq_page_loads(self):
        """Test that FAQ page loads successfully"""
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FAQ')
    
    def test_home_page_context(self):
        """Test home page context data"""
        response = self.client.get(reverse('core:home'))
        self.assertIn('featured_services', response.context)
        self.assertIn('recent_resources', response.context)
        self.assertIn('testimonials', response.context)
    
    def test_home_page_seo(self):
        """Test home page SEO elements"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, '<title>')
        self.assertContains(response, 'meta name="description"')
        self.assertContains(response, 'meta property="og:')
    
    def test_404_page(self):
        """Test 404 error page"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_sitemap_loads(self):
        """Test that sitemap loads successfully"""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
    
    def test_robots_txt_loads(self):
        """Test that robots.txt loads successfully"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')


class EmailServiceTestCase(TestCase):
    """Test email service functionality"""
    
    def setUp(self):
        self.email_service = EmailService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('core.email_service.EmailMultiAlternatives')
    def test_send_email_success(self, mock_email):
        """Test successful email sending"""
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance
        
        result = self.email_service.send_email(
            template_name='welcome',
            context={'user': self.user},
            to_emails=['test@example.com'],
            subject='Test Email'
        )
        
        self.assertTrue(result)
        mock_email_instance.send.assert_called_once()
    
    @patch('core.email_service.EmailMultiAlternatives')
    def test_send_email_failure(self, mock_email):
        """Test email sending failure"""
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception('SMTP Error')
        mock_email.return_value = mock_email_instance
        
        result = self.email_service.send_email(
            template_name='welcome',
            context={'user': self.user},
            to_emails=['test@example.com'],
            subject='Test Email'
        )
        
        self.assertFalse(result)
    
    def test_welcome_email_context(self):
        """Test welcome email context preparation"""
        with patch.object(self.email_service, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = self.email_service.send_welcome_email(self.user)
            
            self.assertTrue(result)
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            self.assertEqual(kwargs['template_name'], 'welcome')
            self.assertEqual(kwargs['to_emails'], [self.user.email])
            self.assertIn('user', kwargs['context'])


class SEOManagerTestCase(TestCase):
    """Test SEO utilities"""
    
    def setUp(self):
        self.seo_manager = SEOManager()
    
    def test_generate_meta_tags(self):
        """Test meta tags generation"""
        meta_tags = self.seo_manager.generate_meta_tags(
            title='Test Page',
            description='Test description',
            keywords=['test', 'seo'],
            url='/test-page/'
        )
        
        self.assertIn('<title>Test Page | EduBridge Ghana</title>', meta_tags)
        self.assertIn('meta name="description"', meta_tags)
        self.assertIn('meta name="keywords"', meta_tags)
        self.assertIn('meta property="og:', meta_tags)
        self.assertIn('meta name="twitter:', meta_tags)
    
    def test_generate_structured_data(self):
        """Test structured data generation"""
        structured_data = self.seo_manager.generate_structured_data(
            title='Test Page',
            description='Test description',
            url='http://example.com/test',
            image='http://example.com/image.jpg'
        )
        
        self.assertIn('application/ld+json', structured_data)
        self.assertIn('@context', structured_data)
        self.assertIn('schema.org', structured_data)
    
    def test_breadcrumbs_structured_data(self):
        """Test breadcrumbs structured data"""
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Services', 'url': '/services/'},
            {'name': 'Current Page', 'url': None}
        ]
        
        structured_data = self.seo_manager.generate_structured_data(
            title='Test',
            description='Test',
            url='/',
            image='',
            breadcrumbs=breadcrumbs
        )
        
        self.assertIn('BreadcrumbList', structured_data)
        self.assertIn('ListItem', structured_data)


class PerformanceTestCase(TestCase):
    """Test performance monitoring utilities"""
    
    def test_performance_monitor(self):
        """Test performance monitoring"""
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Simulate some work
        import time
        time.sleep(0.1)
        
        result = monitor.end('Test Operation')
        
        self.assertIsInstance(result, dict)
        self.assertIn('duration', result)
        self.assertIn('query_count', result)
        self.assertGreater(result['duration'], 0.1)
    
    def test_image_optimizer_initialization(self):
        """Test image optimizer initialization"""
        optimizer = ImageOptimizer()
        
        self.assertIsInstance(optimizer.quality, int)
        self.assertIsInstance(optimizer.max_width, int)
        self.assertIsInstance(optimizer.max_height, int)
    
    def test_cache_manager_methods(self):
        """Test cache manager methods"""
        from core.performance import CacheManager
        
        # Test cache stats (should not raise exception)
        stats = CacheManager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        
        # Test cache invalidation (should not raise exception)
        CacheManager.invalidate_pattern('test:*')


class UtilityFunctionsTestCase(TestCase):
    """Test utility functions"""
    
    def test_minify_html(self):
        """Test HTML minification"""
        from core.performance import minify_html
        
        html = """
        <html>
            <head>
                <title>Test</title>
            </head>
            <body>
                <p>Hello World</p>
            </body>
        </html>
        """
        
        minified = minify_html(html)
        self.assertLess(len(minified), len(html))
        self.assertNotIn('\n', minified)
    
    def test_compress_response(self):
        """Test response compression"""
        from core.performance import compress_response
        
        content = "This is a test content that should be compressed."
        compressed = compress_response(content)
        
        self.assertIsInstance(compressed, bytes)
        self.assertLess(len(compressed), len(content.encode('utf-8')))
    
    def test_preload_critical_resources(self):
        """Test critical resource preloading"""
        from core.performance import preload_critical_resources
        
        preload_links = preload_critical_resources()
        
        self.assertIn('rel="preload"', preload_links)
        self.assertIn('as="style"', preload_links)
        self.assertIn('as="script"', preload_links)


class CacheTestCase(TestCase):
    """Test caching functionality"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_smart_cache_decorator(self):
        """Test smart cache decorator"""
        from core.performance import smart_cache
        
        call_count = 0
        
        @smart_cache(timeout=60, key_prefix='test')
        def test_function(value):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"
        
        # First call should execute function
        result1 = test_function('test')
        self.assertEqual(call_count, 1)
        self.assertEqual(result1, 'result_test')
        
        # Second call should use cache
        result2 = test_function('test')
        self.assertEqual(call_count, 1)  # Should not increment
        self.assertEqual(result2, 'result_test')
    
    def test_cache_invalidation(self):
        """Test cache invalidation"""
        cache.set('test_key', 'test_value', 60)
        self.assertEqual(cache.get('test_key'), 'test_value')
        
        cache.delete('test_key')
        self.assertIsNone(cache.get('test_key'))


@pytest.mark.django_db
class IntegrationTestCase(TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        # Test registration page loads
        response = self.client.get(reverse('accounts:register_steps'))
        self.assertEqual(response.status_code, 200)
        
        # Test registration form submission
        response = self.client.post(reverse('accounts:register_steps'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
    
    def test_service_booking_flow(self):
        """Test service booking flow"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Test services page loads
        response = self.client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_form_submission(self):
        """Test contact form submission"""
        response = self.client.post(reverse('contact:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)


class SecurityTestCase(TestCase):
    """Test security features"""
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        response = self.client.post(reverse('contact:contact'), {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Test'
        })
        
        # Should fail without CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_login_required_views(self):
        """Test that protected views require login"""
        protected_urls = [
            reverse('dashboard:home'),
            reverse('dashboard:profile'),
            reverse('dashboard:bookings'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])  # Redirect to login or forbidden
    
    def test_admin_required_views(self):
        """Test that admin views require admin access"""
        # Create regular user
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        
        self.client.login(username='regular', password='testpass123')
        
        # Try to access admin dashboard
        response = self.client.get(reverse('dashboard:admin_home'))
        self.assertIn(response.status_code, [302, 403])  # Should be denied
