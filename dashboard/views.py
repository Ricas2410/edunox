from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.views import View
from datetime import timedelta
import json

from accounts.models import UserProfile, UserDocument
from services.models import Booking, Service
from contact.models import ContactMessage
from resources.models import Resource
from accounts.forms import UserProfileForm, UserDocumentForm


class DashboardContextMixin:
    """Mixin to provide common dashboard context variables"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user = self.request.user
            # Add navigation badge counts
            context['pending_bookings'] = user.bookings.filter(status='PENDING').count()
            context['unverified_documents'] = user.documents.filter(is_verified=False).count()

        return context


class UserDashboardView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    """User dashboard home"""
    template_name = 'dashboard/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User stats
        context['total_bookings'] = user.bookings.count()
        context['pending_bookings'] = user.bookings.filter(status='PENDING').count()
        context['completed_bookings'] = user.bookings.filter(status='COMPLETED').count()
        context['total_documents'] = user.documents.count()
        context['verified_documents'] = user.documents.filter(is_verified=True).count()
        
        # Recent bookings
        context['recent_bookings'] = user.bookings.select_related('service').order_by('-created_at')[:5]
        
        # Recent documents
        context['recent_documents'] = user.documents.order_by('-created_at')[:5]
        
        # Profile completion
        profile = getattr(user, 'profile', None)
        if profile:
            completion_fields = [
                profile.phone_number, profile.date_of_birth, profile.address,
                profile.education_level, profile.bio
            ]
            completed_fields = sum(1 for field in completion_fields if field)
            context['profile_completion'] = (completed_fields / len(completion_fields)) * 100
        else:
            context['profile_completion'] = 0
        
        return context


class UserBookingsView(LoginRequiredMixin, DashboardContextMixin, ListView):
    """User bookings list"""
    template_name = 'dashboard/user_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return self.request.user.bookings.select_related('service').order_by('-created_at')


class UserDocumentsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    """User documents management"""
    template_name = 'dashboard/user_documents.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = self.request.user.documents.order_by('-created_at')
        context['documents'] = documents
        context['verified_count'] = documents.filter(is_verified=True).count()
        context['pending_count'] = documents.filter(is_verified=False).count()
        context['form'] = UserDocumentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = UserDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('user_dashboard:documents')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class UserProfileView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    """User profile management"""
    template_name = 'dashboard/user_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['form'] = UserProfileForm(instance=profile)
        return context
    
    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_dashboard:profile')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


# Admin Dashboard Views
def is_staff_user(user):
    """Check if user is staff"""
    return user.is_staff


class AdminDashboardView(UserPassesTestMixin, TemplateView):
    """Admin dashboard home"""
    template_name = 'dashboard/admin_dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Statistics
        context['total_users'] = UserProfile.objects.count()
        context['new_users_this_week'] = UserProfile.objects.filter(created_at__gte=week_ago).count()
        context['verified_users'] = UserProfile.objects.filter(is_verified=True).count()
        context['pending_users'] = UserProfile.objects.filter(is_verified=False).count()

        context['total_bookings'] = Booking.objects.count()
        context['pending_bookings'] = Booking.objects.filter(status='PENDING').count()
        context['completed_bookings'] = Booking.objects.filter(status='COMPLETED').count()
        context['cancelled_bookings'] = Booking.objects.filter(status='CANCELLED').count()

        context['total_contacts'] = ContactMessage.objects.count()
        context['new_contacts'] = ContactMessage.objects.filter(status='NEW').count()
        context['total_resources'] = Resource.objects.filter(is_published=True).count()
        
        # Recent activities
        context['recent_bookings'] = Booking.objects.select_related('user', 'service').order_by('-created_at')[:5]
        context['recent_contacts'] = ContactMessage.objects.order_by('-created_at')[:5]
        context['recent_users'] = UserProfile.objects.select_related('user').order_by('-created_at')[:5]
        
        # Charts data
        context['booking_stats'] = Booking.objects.values('status').annotate(count=Count('id'))
        context['service_stats'] = Service.objects.annotate(booking_count=Count('bookings')).order_by('-booking_count')[:5]
        
        return context


class AdminBookingsView(UserPassesTestMixin, ListView):
    """Admin bookings management"""
    template_name = 'dashboard/admin_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Booking.objects.select_related('user', 'service', 'assigned_to').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(service__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AdminContactsView(UserPassesTestMixin, ListView):
    """Admin contacts management"""
    template_name = 'dashboard/admin_contacts.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = ContactMessage.objects.select_related('user', 'assigned_to').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ContactMessage.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AdminUsersView(UserPassesTestMixin, ListView):
    """Admin users management"""
    template_name = 'dashboard/admin_users.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        from django.contrib.auth.models import User
        queryset = User.objects.select_related('profile').order_by('-date_joined')

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        # User stats for dashboard cards
        users_qs = self.get_queryset()
        context['total_users'] = users_qs.count()
        context['verified_users'] = users_qs.filter(profile__is_verified=True).count()
        context['pending_users'] = users_qs.filter(profile__is_verified=False, is_active=True).count()
        today = timezone.now().date()
        context['new_users_today'] = users_qs.filter(date_joined__date=today).count()
        return context


class AdminDocumentsView(UserPassesTestMixin, ListView):
    """Admin documents management"""
    template_name = 'dashboard/admin_documents.html'
    context_object_name = 'documents'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = UserDocument.objects.select_related('user').order_by('-created_at')

        # Filter by verification status
        status = self.request.GET.get('status')
        if status == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif status == 'unverified':
            queryset = queryset.filter(is_verified=False)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(document_type__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')

        # Document stats
        documents_qs = UserDocument.objects.all()
        context['total_documents'] = documents_qs.count()
        context['verified_documents'] = documents_qs.filter(is_verified=True).count()
        context['unverified_documents'] = documents_qs.filter(is_verified=False).count()

        return context


class AdminServicesView(UserPassesTestMixin, ListView):
    """Admin view for managing services"""
    template_name = 'dashboard/admin_services.html'
    context_object_name = 'services'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # Import here to avoid circular imports
        from services.models import Service
        queryset = Service.objects.select_related('category').order_by('name')

        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import here to avoid circular imports
        from services.models import Service
        # Add service statistics
        services = Service.objects.all()
        context['total_services'] = services.count()
        context['active_services'] = services.filter(is_active=True).count()
        return context


class AdminConsultancyView(UserPassesTestMixin, ListView):
    """Admin view for managing consultancy packages"""
    template_name = 'dashboard/admin_consultancy.html'
    context_object_name = 'packages'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # Import here to avoid circular imports
        from services.models import OneTimeConsultancy
        queryset = OneTimeConsultancy.objects.order_by('name')

        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import here to avoid circular imports
        from services.models import OneTimeConsultancy, ConsultancyPurchase
        # Add consultancy statistics
        packages = OneTimeConsultancy.objects.all()
        context['total_packages'] = packages.count()
        context['active_packages'] = packages.filter(is_active=True).count()
        context['total_purchases'] = ConsultancyPurchase.objects.count()
        context['recent_purchases'] = ConsultancyPurchase.objects.select_related('user', 'package').order_by('-created_at')[:5]
        return context


class AdminSettingsView(UserPassesTestMixin, TemplateView):
    """Admin view for site settings"""
    template_name = 'dashboard/admin_settings.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add current site configuration
        from core.models import SiteConfiguration
        context['config'] = SiteConfiguration.get_config()
        return context


# API Views for Admin Operations
class AdminServiceAPIView(UserPassesTestMixin, View):
    """API view for service management operations"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, service_id):
        """Get service details"""
        try:
            from services.models import Service
            service = get_object_or_404(Service, id=service_id)

            # Get service bookings
            bookings = service.bookings.select_related('user').order_by('-created_at')[:10]

            service_data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category.name if service.category else 'No Category',
                'price': str(service.price),
                'duration': service.duration,
                'is_active': service.is_active,
                'created_at': service.created_at.strftime('%Y-%m-%d %H:%M'),
                'bookings': [
                    {
                        'id': booking.id,
                        'user': booking.user.get_full_name() or booking.user.username,
                        'user_email': booking.user.email,
                        'status': booking.status,
                        'preferred_date': booking.preferred_date.strftime('%Y-%m-%d') if booking.preferred_date else None,
                        'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M'),
                        'quoted_price': str(booking.quoted_price) if booking.quoted_price else None,
                    }
                    for booking in bookings
                ],
                'total_bookings': service.bookings.count(),
                'pending_bookings': service.bookings.filter(status='PENDING').count(),
                'completed_bookings': service.bookings.filter(status='COMPLETED').count(),
            }

            return JsonResponse({'success': True, 'service': service_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, service_id):
        """Update service (POST method)"""
        return self._update_service(request, service_id)
    
    def put(self, request, service_id):
        """Update service (PUT method)"""
        return self._update_service(request, service_id)
    
    def _update_service(self, request, service_id):
        """Common method to handle service updates"""
        try:
            from services.models import Service
            service = get_object_or_404(Service, id=service_id)

            # Parse JSON data
            import json
            data = json.loads(request.body)

            # Update service fields
            if 'name' in data:
                service.name = data['name']
            if 'description' in data:
                service.description = data['description']
            if 'price' in data:
                service.price = data['price']
            if 'duration' in data:
                service.duration = data['duration']
            if 'is_active' in data:
                service.is_active = data['is_active']

            service.save()

            return JsonResponse({'success': True, 'message': 'Service updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def delete(self, request, service_id):
        """Delete service"""
        try:
            from services.models import Service
            service = get_object_or_404(Service, id=service_id)

            # Check if service has bookings
            if service.bookings.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete service with existing bookings. Please handle bookings first.'
                })

            service_name = service.name
            service.delete()

            return JsonResponse({'success': True, 'message': f'Service "{service_name}" deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminUserAPIView(UserPassesTestMixin, View):
    """API view for user management operations"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, user_id):
        """Get user details"""
        try:
            user = get_object_or_404(User, id=user_id)
            profile = getattr(user, 'profile', None)

            data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M'),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'profile': {
                    'phone_number': profile.phone_number if profile else '',
                    'education_level': profile.get_education_level_display() if profile else '',
                    'is_verified': profile.is_verified if profile else False,
                    'bio': profile.bio if profile else '',
                } if profile else None
            }

            return JsonResponse({'success': True, 'user': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, user_id):
        """Update user or perform actions"""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            user = get_object_or_404(User, id=user_id)

            if action == 'verify':
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.is_verified = True
                    profile.verification_date = timezone.now()
                    profile.save()
                    return JsonResponse({'success': True, 'message': 'User verified successfully'})
                else:
                    return JsonResponse({'success': False, 'error': 'User profile not found'})

            elif action == 'toggle_active':
                user.is_active = not user.is_active
                user.save()
                status = 'activated' if user.is_active else 'deactivated'
                return JsonResponse({'success': True, 'message': f'User {status} successfully'})

            elif action == 'update':
                # Update user fields
                user.first_name = data.get('first_name', user.first_name)
                user.last_name = data.get('last_name', user.last_name)
                user.email = data.get('email', user.email)
                user.save()

                # Update profile fields if profile exists
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.phone_number = data.get('phone_number', profile.phone_number)
                    profile.education_level = data.get('education_level', profile.education_level)
                    profile.bio = data.get('bio', profile.bio)
                    profile.save()

                return JsonResponse({'success': True, 'message': 'User updated successfully'})

            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def delete(self, request, user_id):
        """Delete user"""
        try:
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return JsonResponse({'success': False, 'error': 'Cannot delete superuser'})

            username = user.username
            user.delete()
            return JsonResponse({'success': True, 'message': f'User {username} deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminUserCreateAPIView(UserPassesTestMixin, View):
    """API view for creating new users"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        """Create new user"""
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'success': False, 'error': f'{field} is required'})

            # Check if username already exists
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'})

            # Check if email already exists
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'success': False, 'error': 'Email already exists'})

            # Create user
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                is_active=data.get('is_active', True),
                is_staff=data.get('is_staff', False)
            )

            # Create or update profile if additional data provided
            if any(key in data for key in ['phone_number', 'education_level']):
                from accounts.models import UserProfile
                profile, created = UserProfile.objects.get_or_create(user=user)

                if data.get('phone_number'):
                    profile.phone_number = data['phone_number']
                if data.get('education_level'):
                    profile.education_level = data['education_level']

                profile.save()

            return JsonResponse({
                'success': True,
                'message': f'User "{user.username}" created successfully',
                'user_id': user.id
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminConsultancyAPIView(UserPassesTestMixin, View):
    """API view for consultancy package management operations"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, package_id):
        """Get consultancy package details"""
        try:
            from services.models import OneTimeConsultancy
            package = get_object_or_404(OneTimeConsultancy, id=package_id)

            # Get package purchases
            purchases = package.consultancypurchase_set.select_related('user').order_by('-created_at')[:10]

            package_data = {
                'id': package.id,
                'name': package.name,
                'description': package.description,
                'price': str(package.price),
                'duration_months': package.duration_months,
                'is_active': package.is_active,
                'features': package.features,
                'features_list': package.features_list,
                'created_at': package.created_at.strftime('%Y-%m-%d %H:%M'),
                'included_services': [
                    {
                        'id': service.id,
                        'name': service.name,
                        'price': str(service.price) if service.price else 'Free'
                    }
                    for service in package.included_services.all()
                ],
                'purchases': [
                    {
                        'id': purchase.id,
                        'user': purchase.user.get_full_name() or purchase.user.username,
                        'user_email': purchase.user.email,
                        'purchase_date': purchase.purchase_date.strftime('%Y-%m-%d %H:%M'),
                        'expiry_date': purchase.expiry_date.strftime('%Y-%m-%d'),
                        'amount_paid': str(purchase.amount_paid),
                        'is_active': purchase.is_active,
                        'is_valid': purchase.is_valid(),
                    }
                    for purchase in purchases
                ],
                'total_purchases': package.consultancypurchase_set.count(),
                'active_purchases': package.consultancypurchase_set.filter(is_active=True).count(),
                'total_revenue': sum(p.amount_paid for p in package.consultancypurchase_set.all()),
            }

            return JsonResponse({'success': True, 'package': package_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, package_id):
        """Update consultancy package"""
        try:
            from services.models import OneTimeConsultancy
            package = get_object_or_404(OneTimeConsultancy, id=package_id)

            # Parse JSON data
            data = json.loads(request.body)

            # Update package fields
            if 'name' in data:
                package.name = data['name']
            if 'description' in data:
                package.description = data['description']
            if 'price' in data:
                package.price = data['price']
            if 'duration_months' in data:
                package.duration_months = data['duration_months']
            if 'features' in data:
                package.features = data['features']
            if 'is_active' in data:
                package.is_active = data['is_active']

            package.save()

            # Update included services if provided
            if 'included_services' in data:
                service_ids = data['included_services']
                from services.models import Service
                services = Service.objects.filter(id__in=service_ids)
                package.included_services.set(services)

            return JsonResponse({'success': True, 'message': 'Package updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def delete(self, request, package_id):
        """Delete consultancy package"""
        try:
            from services.models import OneTimeConsultancy
            package = get_object_or_404(OneTimeConsultancy, id=package_id)

            # Check if package has active purchases
            if package.consultancypurchase_set.filter(is_active=True).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete package with active purchases. Please deactivate it instead.'
                })

            package_name = package.name
            package.delete()

            return JsonResponse({'success': True, 'message': f'Package "{package_name}" deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminSettingsAPIView(UserPassesTestMixin, View):
    """API view for site settings management"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        """Get current site settings"""
        try:
            from core.models import SiteConfiguration
            config = SiteConfiguration.get_config()

            settings_data = {
                'site_name': config.site_name,
                'site_description': config.site_description,
                'contact_email': config.contact_email,
                'contact_phone': config.contact_phone,
                'address': config.address,
                'facebook_url': config.facebook_url,
                'twitter_url': config.twitter_url,
                'linkedin_url': config.linkedin_url,
                'instagram_url': config.instagram_url,
                'library_url': config.library_url,
                'library_opens_new_tab': config.library_opens_new_tab,
                'maintenance_mode': config.maintenance_mode,
                'allow_user_registration': config.allow_user_registration,
                'require_email_verification': config.require_email_verification,
                'google_analytics_id': config.google_analytics_id,
                'custom_header_scripts': config.custom_header_scripts,
                'custom_footer_scripts': config.custom_footer_scripts,
                'primary_color': config.primary_color,
                'secondary_color': config.secondary_color,
                'accent_color': config.accent_color,
                'custom_css': config.custom_css,
                'logo_url': config.logo.url if config.logo else None,
                'favicon_url': config.favicon.url if config.favicon else None,
                'hero_image_url': config.hero_image.url if config.hero_image else None,
                'about_page_image_url': config.about_page_image.url if config.about_page_image else None,
                'services_page_image_url': config.services_page_image.url if config.services_page_image else None,
                'resources_page_image_url': config.resources_page_image.url if config.resources_page_image else None,
                'contact_page_image_url': config.contact_page_image.url if config.contact_page_image else None,
                'university_default_image_url': config.university_default_image.url if config.university_default_image else None,
                'scholarship_default_image_url': config.scholarship_default_image.url if config.scholarship_default_image else None,
                'digital_default_image_url': config.digital_default_image.url if config.digital_default_image else None,
                'consultancy_default_image_url': config.consultancy_default_image.url if config.consultancy_default_image else None,
                'general_default_image_url': config.general_default_image.url if config.general_default_image else None,
                # Email settings
                'email_backend': config.email_backend,
                'email_host': config.email_host,
                'email_port': config.email_port,
                'email_use_tls': config.email_use_tls,
                'email_use_ssl': config.email_use_ssl,
                'email_host_user': config.email_host_user,
                'email_host_password': config.email_host_password,
                'default_from_email': config.default_from_email,
            }

            return JsonResponse({'success': True, 'settings': settings_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request):
        """Update site settings"""
        try:
            from core.models import SiteConfiguration
            config = SiteConfiguration.get_config()

            data = json.loads(request.body)

            # Update basic settings
            if 'site_name' in data:
                config.site_name = data['site_name']
            if 'site_description' in data:
                config.site_description = data['site_description']
            if 'contact_email' in data:
                config.contact_email = data['contact_email']
            if 'contact_phone' in data:
                config.contact_phone = data['contact_phone']
            if 'address' in data:
                config.address = data['address']

            # Update social media
            if 'facebook_url' in data:
                config.facebook_url = data['facebook_url']
            if 'twitter_url' in data:
                config.twitter_url = data['twitter_url']
            if 'linkedin_url' in data:
                config.linkedin_url = data['linkedin_url']
            if 'instagram_url' in data:
                config.instagram_url = data['instagram_url']

            # Update library settings
            if 'library_url' in data:
                config.library_url = data['library_url']
            if 'library_opens_new_tab' in data:
                config.library_opens_new_tab = data['library_opens_new_tab']

            # Update advanced settings
            if 'maintenance_mode' in data:
                config.maintenance_mode = data['maintenance_mode']
            if 'allow_user_registration' in data:
                config.allow_user_registration = data['allow_user_registration']
            if 'require_email_verification' in data:
                config.require_email_verification = data['require_email_verification']
            if 'google_analytics_id' in data:
                config.google_analytics_id = data['google_analytics_id']
            if 'custom_header_scripts' in data:
                config.custom_header_scripts = data['custom_header_scripts']
            if 'custom_footer_scripts' in data:
                config.custom_footer_scripts = data['custom_footer_scripts']

            # Update branding settings
            if 'primary_color' in data:
                config.primary_color = data['primary_color']
            if 'secondary_color' in data:
                config.secondary_color = data['secondary_color']
            if 'accent_color' in data:
                config.accent_color = data['accent_color']
            if 'custom_css' in data:
                config.custom_css = data['custom_css']

            # Update email settings
            if 'email_backend' in data:
                config.email_backend = data['email_backend']
            if 'email_host' in data:
                config.email_host = data['email_host']
            if 'email_port' in data:
                config.email_port = int(data['email_port']) if data['email_port'] else 587
            if 'email_use_tls' in data:
                config.email_use_tls = bool(data['email_use_tls'])
            if 'email_use_ssl' in data:
                config.email_use_ssl = bool(data['email_use_ssl'])
            if 'email_host_user' in data:
                config.email_host_user = data['email_host_user']
            if 'email_host_password' in data:
                # Only update password if it's not empty (to preserve existing encrypted passwords)
                if data['email_host_password'].strip():
                    # Remove spaces from app passwords (common Gmail issue)
                    clean_password = data['email_host_password'].replace(' ', '')
                    config.email_host_password = clean_password
            if 'default_from_email' in data:
                config.default_from_email = data['default_from_email']

            config.save()

            return JsonResponse({'success': True, 'message': 'Settings updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminSettingsFileUploadAPIView(UserPassesTestMixin, View):
    """API view for handling file uploads in site settings"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        """Handle file uploads"""
        try:
            from core.models import SiteConfiguration
            config = SiteConfiguration.get_config()

            # Handle main branding uploads
            if 'logo' in request.FILES:
                config.logo = request.FILES['logo']
            if 'favicon' in request.FILES:
                config.favicon = request.FILES['favicon']
            if 'hero_image' in request.FILES:
                config.hero_image = request.FILES['hero_image']

            # Handle page hero images
            if 'about_page_image' in request.FILES:
                config.about_page_image = request.FILES['about_page_image']
            if 'services_page_image' in request.FILES:
                config.services_page_image = request.FILES['services_page_image']
            if 'resources_page_image' in request.FILES:
                config.resources_page_image = request.FILES['resources_page_image']
            if 'contact_page_image' in request.FILES:
                config.contact_page_image = request.FILES['contact_page_image']

            # Handle about page section images
            if 'about_mission_image' in request.FILES:
                config.about_mission_image = request.FILES['about_mission_image']
            if 'about_approach_image' in request.FILES:
                config.about_approach_image = request.FILES['about_approach_image']

            # Handle default service category images
            if 'university_default_image' in request.FILES:
                config.university_default_image = request.FILES['university_default_image']
            if 'scholarship_default_image' in request.FILES:
                config.scholarship_default_image = request.FILES['scholarship_default_image']
            if 'digital_default_image' in request.FILES:
                config.digital_default_image = request.FILES['digital_default_image']
            if 'consultancy_default_image' in request.FILES:
                config.consultancy_default_image = request.FILES['consultancy_default_image']
            if 'general_default_image' in request.FILES:
                config.general_default_image = request.FILES['general_default_image']

            # Handle form data for branding settings
            if 'primary_color' in request.POST:
                config.primary_color = request.POST['primary_color']
            if 'secondary_color' in request.POST:
                config.secondary_color = request.POST['secondary_color']
            if 'accent_color' in request.POST:
                config.accent_color = request.POST['accent_color']
            if 'custom_css' in request.POST:
                config.custom_css = request.POST['custom_css']

            config.save()

            # Return updated URLs
            response_data = {
                'success': True,
                'message': 'Branding settings updated successfully',
                'logo_url': config.logo.url if config.logo else None,
                'favicon_url': config.favicon.url if config.favicon else None,
                'hero_image_url': config.hero_image.url if config.hero_image else None,
                'about_page_image_url': config.about_page_image.url if config.about_page_image else None,
                'services_page_image_url': config.services_page_image.url if config.services_page_image else None,
                'resources_page_image_url': config.resources_page_image.url if config.resources_page_image else None,
                'contact_page_image_url': config.contact_page_image.url if config.contact_page_image else None,
                'about_mission_image_url': config.about_mission_image.url if config.about_mission_image else None,
                'about_approach_image_url': config.about_approach_image.url if config.about_approach_image else None,
                'university_default_image_url': config.university_default_image.url if config.university_default_image else None,
                'scholarship_default_image_url': config.scholarship_default_image.url if config.scholarship_default_image else None,
                'digital_default_image_url': config.digital_default_image.url if config.digital_default_image else None,
                'consultancy_default_image_url': config.consultancy_default_image.url if config.consultancy_default_image else None,
                'general_default_image_url': config.general_default_image.url if config.general_default_image else None,
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AdminBackupAPIView(UserPassesTestMixin, View):
    """API view to trigger data backup"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        try:
            from django.core.management import call_command
            from django.http import JsonResponse
            import io
            import sys

            # Capture output
            old_stdout = sys.stdout
            redirect_output = io.StringIO()
            sys.stdout = redirect_output

            try:
                # Get options from request or use defaults
                import json
                try:
                    data = json.loads(request.body) if request.body else {}
                except:
                    data = {}
                
                include_media = data.get('include_media', True)  # Default to True
                compress = data.get('compress', True)  # Default to True
                
                # Build command arguments
                args = ['backup_data']
                if include_media:
                    args.append('--include-media')
                if compress:
                    args.append('--compress')
                
                call_command(*args)
                output = redirect_output.getvalue()
                sys.stdout = old_stdout # Restore stdout
                return JsonResponse({'success': True, 'message': 'Backup created successfully with media files included!', 'output': output})
            except Exception as e:
                sys.stdout = old_stdout # Restore stdout
                return JsonResponse({'success': False, 'error': f'Backup failed: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


class AdminRestoreAPIView(UserPassesTestMixin, View):
    """API view to trigger data restore"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        try:
            from django.core.management import call_command
            from django.http import JsonResponse
            from django.core.files.storage import default_storage
            import io
            import sys
            import os
            import tempfile

            # Check if backup file was uploaded
            if 'backup_file' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No backup file uploaded. Please select a backup file.'})
            
            backup_file = request.FILES['backup_file']
            
            # Validate file type
            if not (backup_file.name.endswith('.zip') or backup_file.name.endswith('.json')):
                return JsonResponse({'success': False, 'error': 'Invalid file type. Please upload a .zip or .json backup file.'})
            
            # Save uploaded file to temporary location
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, backup_file.name)
            
            try:
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in backup_file.chunks():
                        destination.write(chunk)
                
                # Capture output
                old_stdout = sys.stdout
                redirect_output = io.StringIO()
                sys.stdout = redirect_output

                try:
                    # Call restore command with the backup file path
                    call_command('restore_data', temp_file_path, '--include-media', '--clear-existing', '--force')
                    output = redirect_output.getvalue()
                    sys.stdout = old_stdout # Restore stdout
                    return JsonResponse({
                        'success': True, 
                        'message': 'Backup restored successfully! The page will reload to reflect changes.', 
                        'output': output
                    })
                except Exception as e:
                    sys.stdout = old_stdout # Restore stdout
                    return JsonResponse({'success': False, 'error': f'Restore failed: {str(e)}'})
                    
            finally:
                # Clean up temporary file
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except:
                    pass
                    
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


class AdminBackupHistoryAPIView(UserPassesTestMixin, View):
    """API view to get backup history"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        try:
            import os
            from datetime import datetime
            from django.conf import settings
            
            # Get backup directory
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            backups = []
            
            if os.path.exists(backup_dir):
                for item in os.listdir(backup_dir):
                    item_path = os.path.join(backup_dir, item)
                    if os.path.isfile(item_path) and (item.endswith('.zip') or item.endswith('.json')):
                        # Get file stats
                        stat = os.stat(item_path)
                        size = self.format_file_size(stat.st_size)
                        date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        
                        backups.append({
                            'name': item,
                            'path': item_path,
                            'size': size,
                            'date': date,
                            'timestamp': stat.st_mtime
                        })
                    elif os.path.isdir(item_path) and item.startswith('Edunox_backup_'):
                        # Directory backup
                        stat = os.stat(item_path)
                        size = self.get_directory_size(item_path)
                        date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        
                        backups.append({
                            'name': item,
                            'path': item_path,
                            'size': self.format_file_size(size),
                            'date': date,
                            'timestamp': stat.st_mtime
                        })
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return JsonResponse({'success': True, 'backups': backups})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error loading backup history: {str(e)}'})
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def get_directory_size(self, path):
        """Get total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size


class AdminDownloadBackupAPIView(UserPassesTestMixin, View):
    """API view to download backup files"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        try:
            from django.http import FileResponse, Http404
            import os
            from urllib.parse import unquote
            
            backup_path = request.GET.get('path')
            if not backup_path:
                return JsonResponse({'success': False, 'error': 'No backup path specified'})
            
            # Decode URL-encoded path
            backup_path = unquote(backup_path)
            
            # Security check - ensure path is within backup directory
            from django.conf import settings
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not backup_path.startswith(backup_dir):
                return JsonResponse({'success': False, 'error': 'Invalid backup path'})
            
            if not os.path.exists(backup_path):
                raise Http404("Backup file not found")
            
            if os.path.isfile(backup_path):
                response = FileResponse(
                    open(backup_path, 'rb'),
                    as_attachment=True,
                    filename=os.path.basename(backup_path)
                )
                return response
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Download failed: {str(e)}'})


class AdminDeleteBackupAPIView(UserPassesTestMixin, View):
    """API view to delete backup files"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        try:
            import json
            import os
            import shutil
            from django.conf import settings
            
            data = json.loads(request.body)
            backup_path = data.get('path')
            
            if not backup_path:
                return JsonResponse({'success': False, 'error': 'No backup path specified'})
            
            # Security check - ensure path is within backup directory
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not backup_path.startswith(backup_dir):
                return JsonResponse({'success': False, 'error': 'Invalid backup path'})
            
            if not os.path.exists(backup_path):
                return JsonResponse({'success': False, 'error': 'Backup file not found'})
            
            # Delete file or directory
            if os.path.isfile(backup_path):
                os.remove(backup_path)
            elif os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            
            return JsonResponse({'success': True, 'message': 'Backup deleted successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Delete failed: {str(e)}'})


class AdminEmailTestAPIView(UserPassesTestMixin, View):
    """API view for testing email configuration"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        """Send test email"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            from core.models import SiteConfiguration
            from django.utils import timezone
            import json

            data = json.loads(request.body)
            test_email = data.get('test_email', request.user.email)

            # Get current configuration
            config = SiteConfiguration.get_config()

            # Completely override settings for this test to avoid conflicts
            original_settings = {}

            # Clean the password (remove spaces)
            clean_password = config.email_host_password.replace(' ', '') if config.email_host_password else ''

            # Special handling for different email providers
            email_host = config.email_host
            email_port = config.email_port
            use_tls = config.email_use_tls
            use_ssl = config.email_use_ssl

            # Provider-specific optimizations
            if 'gmail.com' in email_host.lower():
                email_host = 'smtp.gmail.com'
                email_port = 587
                use_tls = True
                use_ssl = False
                print("DEBUG - Applied Gmail-specific settings")
            elif 'zoho.com' in email_host.lower():
                email_host = 'smtp.zoho.com'
                email_port = 587
                use_tls = True
                use_ssl = False
                print("DEBUG - Applied Zoho-specific settings")

            # Force these settings for the test (ignore environment)
            email_settings = {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',  # Force SMTP
                'EMAIL_HOST': email_host,
                'EMAIL_PORT': email_port,
                'EMAIL_USE_TLS': use_tls,
                'EMAIL_USE_SSL': use_ssl,
                'EMAIL_HOST_USER': config.email_host_user,
                'EMAIL_HOST_PASSWORD': clean_password,
                'DEFAULT_FROM_EMAIL': config.default_from_email or config.contact_email,
                'SERVER_EMAIL': config.default_from_email or config.contact_email,
                'EMAIL_TIMEOUT': 30,
                'EMAIL_USE_LOCALTIME': True,
            }

            # Backup and apply settings
            for key, value in email_settings.items():
                if hasattr(settings, key):
                    original_settings[key] = getattr(settings, key)
                setattr(settings, key, value)

            # Validate email configuration
            if (config.email_backend == 'django.core.mail.backends.smtp.EmailBackend' and
                (not config.email_host or not config.email_host_user or not config.email_host_password)):
                return JsonResponse({
                    'success': False,
                    'error': 'Email configuration is incomplete. Please configure SMTP host, username, and password first.'
                })

            try:
                # Debug: Log current email settings
                print(f"DEBUG - Email settings:")
                print(f"  Backend: {settings.EMAIL_BACKEND}")
                print(f"  Host: {settings.EMAIL_HOST}")
                print(f"  Port: {settings.EMAIL_PORT}")
                print(f"  Use TLS: {settings.EMAIL_USE_TLS}")
                print(f"  Use SSL: {settings.EMAIL_USE_SSL}")
                print(f"  User: {settings.EMAIL_HOST_USER}")
                print(f"  From: {settings.DEFAULT_FROM_EMAIL}")

                # Send test email
                send_mail(
                    subject='Test Email from Edunox GH',
                    message=f'''This is a test email sent from your Edunox GH admin panel.

If you received this email, your email configuration is working correctly!

Email Configuration Details:
- SMTP Host: {config.email_host}
- SMTP Port: {config.email_port}
- Use TLS: {config.email_use_tls}
- Use SSL: {config.email_use_ssl}
- From Email: {config.default_from_email or config.contact_email}

Sent at: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
Edunox GH Admin System''',
                    from_email=config.default_from_email or config.contact_email,
                    recipient_list=[test_email],
                    fail_silently=False,
                )

                return JsonResponse({
                    'success': True,
                    'message': f'Test email sent successfully to {test_email}! Please check your inbox and spam folder.'
                })

            except Exception as email_error:
                # More detailed error information
                error_msg = str(email_error)
                print(f"DEBUG - Email error: {error_msg}")

                # Provide specific guidance for common Gmail errors
                if '535' in error_msg and 'BadCredentials' in error_msg:
                    gmail_help = """
Gmail Authentication Error. Please check:
1. Use your Gmail address as username
2. Use an App Password (not your regular password)
3. Enable 2-Factor Authentication first
4. Generate App Password: Google Account → Security → App passwords
5. Make sure 'Less secure app access' is not needed (deprecated)
"""
                    return JsonResponse({
                        'success': False,
                        'error': f'Gmail Authentication Failed: {gmail_help}'
                    })
                elif '534' in error_msg:
                    return JsonResponse({
                        'success': False,
                        'error': 'Gmail Error: Please enable 2-Factor Authentication and use an App Password instead of your regular password.'
                    })
                elif 'Connection refused' in error_msg:
                    return JsonResponse({
                        'success': False,
                        'error': 'Connection refused. Check your SMTP host and port settings. For Gmail use: smtp.gmail.com:587'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Email sending failed: {error_msg}'
                    })
            finally:
                # Restore original settings
                for key, value in original_settings.items():
                    setattr(settings, key, value)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to send test email: {str(e)}'
            })


@login_required
@require_POST
def update_profile_picture(request):
    """Update user profile picture via AJAX"""
    try:
        if 'profile_picture' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file uploaded'})

        profile_picture = request.FILES['profile_picture']

        # Validate file type
        if not profile_picture.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'Please upload a valid image file'})

        # Validate file size (max 5MB)
        if profile_picture.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File size must be less than 5MB'})

        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Delete old profile picture if exists
        if profile.profile_picture:
            try:
                profile.profile_picture.delete(save=False)
            except:
                pass  # Ignore errors when deleting old file

        # Save new profile picture
        profile.profile_picture = profile_picture
        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Profile picture updated successfully!',
            'profile_picture_url': profile.profile_picture.url
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to update profile picture: {str(e)}'
        })
