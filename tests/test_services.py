"""
Services app tests for EduBridge Ghana
Tests for service models, views, forms, and booking functionality
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from services.models import Service, ServiceCategory, Booking
from services.forms import BookingForm

User = get_user_model()


class ServiceModelTestCase(TestCase):
    """Test Service model"""
    
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='University Applications',
            description='Help with university applications',
            icon='graduation-cap',
            color='#3B82F6'
        )
        
        self.service = Service.objects.create(
            name='University Application Support',
            short_description='Get help with your university applications',
            description='Comprehensive support for university applications including essay writing, document preparation, and interview coaching.',
            category=self.category,
            price=150.00,
            duration='2 hours',
            is_active=True,
            is_featured=True
        )
    
    def test_service_creation(self):
        """Test service creation"""
        self.assertEqual(self.service.name, 'University Application Support')
        self.assertEqual(self.service.category, self.category)
        self.assertEqual(self.service.price, 150.00)
        self.assertTrue(self.service.is_active)
        self.assertTrue(self.service.is_featured)
    
    def test_service_str_method(self):
        """Test service string representation"""
        self.assertEqual(str(self.service), 'University Application Support')
    
    def test_service_get_absolute_url(self):
        """Test service get_absolute_url method"""
        expected_url = reverse('services:detail', args=[self.service.pk])
        self.assertEqual(self.service.get_absolute_url(), expected_url)
    
    def test_service_features_list_property(self):
        """Test features_list property"""
        self.service.features = 'Feature 1\nFeature 2\nFeature 3'
        self.service.save()
        
        features = self.service.features_list
        self.assertEqual(len(features), 3)
        self.assertIn('Feature 1', features)
    
    def test_service_requirements_list_property(self):
        """Test requirements_list property"""
        self.service.requirements = 'Requirement 1\nRequirement 2'
        self.service.save()
        
        requirements = self.service.requirements_list
        self.assertEqual(len(requirements), 2)
        self.assertIn('Requirement 1', requirements)
    
    def test_service_ordering(self):
        """Test service ordering"""
        service2 = Service.objects.create(
            name='Second Service',
            category=self.category,
            price=100.00,
            order=1
        )
        
        self.service.order = 2
        self.service.save()
        
        services = Service.objects.all()
        self.assertEqual(services[0], service2)
        self.assertEqual(services[1], self.service)


class ServiceCategoryModelTestCase(TestCase):
    """Test ServiceCategory model"""
    
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Digital Literacy',
            description='Digital skills training',
            icon='laptop',
            color='#10B981'
        )
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'Digital Literacy')
        self.assertEqual(self.category.icon, 'laptop')
        self.assertEqual(self.category.color, '#10B981')
        self.assertTrue(self.category.is_active)
    
    def test_category_str_method(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Digital Literacy')
    
    def test_category_ordering(self):
        """Test category ordering"""
        category2 = ServiceCategory.objects.create(
            name='Second Category',
            order=1
        )
        
        self.category.order = 2
        self.category.save()
        
        categories = ServiceCategory.objects.all()
        self.assertEqual(categories[0], category2)
        self.assertEqual(categories[1], self.category)


class BookingModelTestCase(TestCase):
    """Test Booking model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            description='Test category'
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            category=self.category,
            price=100.00
        )
        
        self.booking = Booking.objects.create(
            user=self.user,
            service=self.service,
            preferred_date=timezone.now().date() + timedelta(days=1),
            preferred_time=time(14, 0),
            message='Test booking message'
        )
    
    def test_booking_creation(self):
        """Test booking creation"""
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.service, self.service)
        self.assertEqual(self.booking.status, 'PENDING')
        self.assertEqual(self.booking.message, 'Test booking message')
    
    def test_booking_str_method(self):
        """Test booking string representation"""
        expected = f"Test Service - {self.user.username}"
        self.assertEqual(str(self.booking), expected)
    
    def test_booking_status_choices(self):
        """Test booking status choices"""
        valid_statuses = ['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        
        for status in valid_statuses:
            self.booking.status = status
            self.booking.save()
            self.assertEqual(self.booking.status, status)
    
    def test_booking_get_absolute_url(self):
        """Test booking get_absolute_url method"""
        expected_url = reverse('dashboard:booking_detail', args=[self.booking.pk])
        self.assertEqual(self.booking.get_absolute_url(), expected_url)


class BookingFormTestCase(TestCase):
    """Test BookingForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            description='Test category'
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            category=self.category,
            price=100.00
        )
    
    def test_valid_booking_form(self):
        """Test valid booking form"""
        future_date = timezone.now().date() + timedelta(days=1)
        
        form_data = {
            'preferred_date': future_date,
            'preferred_time': time(14, 0),
            'message': 'Test message',
            'contact_method': 'EMAIL',
            'terms': True
        }
        
        form = BookingForm(data=form_data, service=self.service, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_booking_form_past_date_validation(self):
        """Test booking form validation for past dates"""
        past_date = timezone.now().date() - timedelta(days=1)
        
        form_data = {
            'preferred_date': past_date,
            'preferred_time': time(14, 0),
            'message': 'Test message',
            'contact_method': 'EMAIL',
            'terms': True
        }
        
        form = BookingForm(data=form_data, service=self.service, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('preferred_date', form.errors)
    
    def test_booking_form_business_hours_validation(self):
        """Test booking form validation for business hours"""
        future_date = timezone.now().date() + timedelta(days=1)
        
        # Test time outside business hours
        form_data = {
            'preferred_date': future_date,
            'preferred_time': time(8, 0),  # Before 9 AM
            'message': 'Test message',
            'contact_method': 'EMAIL',
            'terms': True
        }
        
        form = BookingForm(data=form_data, service=self.service, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('preferred_time', form.errors)
    
    def test_booking_form_sunday_validation(self):
        """Test booking form validation for Sundays"""
        # Find next Sunday
        today = timezone.now().date()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        next_sunday = today + timedelta(days=days_ahead)
        
        form_data = {
            'preferred_date': next_sunday,
            'preferred_time': time(14, 0),
            'message': 'Test message',
            'contact_method': 'EMAIL',
            'terms': True
        }
        
        form = BookingForm(data=form_data, service=self.service, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('preferred_date', form.errors)
    
    def test_booking_form_terms_required(self):
        """Test that terms acceptance is required"""
        future_date = timezone.now().date() + timedelta(days=1)
        
        form_data = {
            'preferred_date': future_date,
            'preferred_time': time(14, 0),
            'message': 'Test message',
            'contact_method': 'EMAIL',
            'terms': False  # Not accepting terms
        }
        
        form = BookingForm(data=form_data, service=self.service, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('terms', form.errors)


class ServiceViewsTestCase(TestCase):
    """Test service views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            description='Test category',
            is_active=True
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            short_description='Test short description',
            description='Test description',
            category=self.category,
            price=100.00,
            is_active=True
        )
    
    def test_service_list_view(self):
        """Test service list view"""
        response = self.client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')
        self.assertIn('services', response.context)
        self.assertIn('categories', response.context)
    
    def test_service_detail_view(self):
        """Test service detail view"""
        response = self.client.get(reverse('services:detail', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')
        self.assertEqual(response.context['service'], self.service)
    
    def test_service_detail_view_inactive_service(self):
        """Test service detail view for inactive service"""
        self.service.is_active = False
        self.service.save()
        
        response = self.client.get(reverse('services:detail', args=[self.service.pk]))
        self.assertEqual(response.status_code, 404)
    
    def test_service_booking_view_anonymous(self):
        """Test service booking view for anonymous user"""
        response = self.client.get(reverse('services:book', args=[self.service.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_service_booking_view_authenticated(self):
        """Test service booking view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('services:book', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')
        self.assertIn('form', response.context)
    
    def test_service_booking_post_valid(self):
        """Test valid service booking submission"""
        self.client.login(username='testuser', password='testpass123')
        
        future_date = timezone.now().date() + timedelta(days=1)
        
        response = self.client.post(reverse('services:book', args=[self.service.pk]), {
            'preferred_date': future_date,
            'preferred_time': '14:00',
            'message': 'Test booking',
            'contact_method': 'EMAIL',
            'terms': True
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        
        # Check that booking was created
        booking = Booking.objects.filter(user=self.user, service=self.service).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.message, 'Test booking')
    
    def test_service_category_view(self):
        """Test service category view"""
        response = self.client.get(reverse('services:category', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertIn('services', response.context)
        self.assertIn('category', response.context)
    
    def test_service_search_functionality(self):
        """Test service search functionality"""
        response = self.client.get(reverse('services:list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')
    
    def test_service_category_filter(self):
        """Test service category filtering"""
        response = self.client.get(reverse('services:list'), {'category': self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')
    
    def test_service_price_filter(self):
        """Test service price filtering"""
        response = self.client.get(reverse('services:list'), {'price_range': '51-100'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Service')


class ServiceAPITestCase(TestCase):
    """Test service API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Test Category',
            description='Test category'
        )
        
        self.service = Service.objects.create(
            name='Test Service',
            category=self.category,
            price=100.00,
            is_active=True
        )
    
    def test_time_slots_api(self):
        """Test time slots API endpoint"""
        future_date = (timezone.now().date() + timedelta(days=1)).isoformat()
        
        response = self.client.get(
            reverse('services:time_slots', args=[self.service.pk, future_date])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('slots', data)
        self.assertIsInstance(data['slots'], list)
    
    def test_time_slots_api_invalid_date(self):
        """Test time slots API with invalid date"""
        response = self.client.get(
            reverse('services:time_slots', args=[self.service.pk, 'invalid-date'])
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)


@pytest.mark.django_db
class ServiceIntegrationTestCase(TestCase):
    """Integration tests for services"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ServiceCategory.objects.create(
            name='University Applications',
            description='University application support'
        )
        
        self.service = Service.objects.create(
            name='Application Review',
            category=self.category,
            price=200.00,
            is_active=True
        )
    
    def test_complete_booking_flow(self):
        """Test complete booking flow from service list to confirmation"""
        # 1. Visit service list
        response = self.client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)
        
        # 2. View service details
        response = self.client.get(reverse('services:detail', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        
        # 3. Login
        self.client.login(username='testuser', password='testpass123')
        
        # 4. Access booking form
        response = self.client.get(reverse('services:book', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        
        # 5. Submit booking
        future_date = timezone.now().date() + timedelta(days=1)
        response = self.client.post(reverse('services:book', args=[self.service.pk]), {
            'preferred_date': future_date,
            'preferred_time': '14:00',
            'message': 'Please help with my application',
            'contact_method': 'EMAIL',
            'terms': True
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify booking was created
        booking = Booking.objects.filter(user=self.user, service=self.service).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'PENDING')
    
    def test_service_filtering_and_search(self):
        """Test service filtering and search functionality"""
        # Create additional services for testing
        category2 = ServiceCategory.objects.create(
            name='Digital Literacy',
            description='Digital skills training'
        )
        
        service2 = Service.objects.create(
            name='Computer Basics',
            category=category2,
            price=50.00,
            is_active=True
        )
        
        # Test search
        response = self.client.get(reverse('services:list'), {'search': 'Application'})
        self.assertContains(response, 'Application Review')
        self.assertNotContains(response, 'Computer Basics')
        
        # Test category filter
        response = self.client.get(reverse('services:list'), {'category': category2.pk})
        self.assertContains(response, 'Computer Basics')
        self.assertNotContains(response, 'Application Review')
        
        # Test price filter
        response = self.client.get(reverse('services:list'), {'price_range': '0-50'})
        self.assertContains(response, 'Computer Basics')
        self.assertNotContains(response, 'Application Review')
