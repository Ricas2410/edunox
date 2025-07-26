from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Service, ServiceCategory, Booking
from .forms import BookingForm, ServiceSearchForm


@method_decorator(cache_page(60 * 10), name='dispatch')  # Cache for 10 minutes
class ServiceListView(ListView):
    """List all available services with search and filtering"""
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).select_related('category').annotate(
            booking_count=Count('bookings')
        )

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Category filter - handle both ID and name/slug
        category_param = self.request.GET.get('category')
        if category_param:
            # Try to filter by ID first (for numeric values)
            if category_param.isdigit():
                queryset = queryset.filter(category_id=category_param)
            else:
                # Handle slug-like category names
                category_name_map = {
                    'university-applications': 'University Applications',
                    'scholarships': 'Scholarship Support',
                    'digital-training': 'Digital Training',
                    'consultancy': 'Consultancy'
                }
                category_name = category_name_map.get(category_param, category_param.replace('-', ' ').title())
                queryset = queryset.filter(category__name__icontains=category_name)

        # Price filter
        price_range = self.request.GET.get('price_range')
        if price_range:
            if price_range == '0-50':
                queryset = queryset.filter(price__lte=50)
            elif price_range == '51-100':
                queryset = queryset.filter(price__gte=51, price__lte=100)
            elif price_range == '101-200':
                queryset = queryset.filter(price__gte=101, price__lte=200)
            elif price_range == '200+':
                queryset = queryset.filter(price__gt=200)

        return queryset.order_by('category__order', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True).order_by('order')
        context['featured_services'] = Service.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category')[:3]
        context['search_form'] = ServiceSearchForm(self.request.GET)

        # Add current filters for template
        context['current_category'] = self.request.GET.get('category', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_price_range'] = self.request.GET.get('price_range', '')

        return context


@method_decorator(cache_page(60 * 20), name='dispatch')  # Cache for 20 minutes
class ServiceDetailView(DetailView):
    """Display service details with booking option"""
    model = Service
    template_name = 'services/detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add related services from the same category
        context['related_services'] = Service.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:3]

        # Add booking form if user is authenticated
        if self.request.user.is_authenticated:
            context['booking_form'] = BookingForm(
                service=self.object,
                user=self.request.user
            )

        return context


@login_required
def book_service(request, pk):
    """Book a service with enhanced form validation"""
    service = get_object_or_404(Service, pk=pk, is_active=True)

    if request.method == 'POST':
        form = BookingForm(request.POST, service=service, user=request.user)
        if form.is_valid():
            booking = form.save()

            messages.success(
                request,
                f'Your booking for "{service.name}" has been submitted successfully! '
                f'Booking reference: #{booking.id}. We will contact you soon to confirm the details.'
            )
            return redirect('dashboard:bookings')
    else:
        form = BookingForm(service=service, user=request.user)

    return render(request, 'services/book.html', {
        'service': service,
        'form': form
    })


class ServiceCategoryView(ListView):
    """Services by category"""
    model = Service
    template_name = 'services/category.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(ServiceCategory, pk=self.kwargs['category_pk'], is_active=True)
        return Service.objects.filter(category=self.category, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        return context


def get_available_time_slots(request, service_id, date):
    """API endpoint to get available time slots for a service on a specific date"""
    try:
        service = get_object_or_404(Service, pk=service_id, is_active=True)

        # Parse the date
        from datetime import datetime
        booking_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Define business hours (9 AM to 6 PM)
        business_hours = [
            '09:00', '10:00', '11:00', '12:00',
            '14:00', '15:00', '16:00', '17:00'
        ]

        # Get existing bookings for this date
        existing_bookings = Booking.objects.filter(
            service=service,
            preferred_date=booking_date,
            status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
        ).values_list('preferred_time', flat=True)

        # Convert existing booking times to strings for comparison
        booked_times = [time.strftime('%H:%M') for time in existing_bookings if time]

        # Filter out booked times
        available_slots = [
            {
                'time': time_slot,
                'available': time_slot not in booked_times
            }
            for time_slot in business_hours
        ]

        return JsonResponse({
            'success': True,
            'slots': available_slots
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    if request.method == 'POST':
        try:
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)

            # Only allow cancellation of pending or confirmed bookings
            if booking.status not in ['PENDING', 'CONFIRMED']:
                return JsonResponse({
                    'success': False,
                    'error': 'This booking cannot be cancelled.'
                })

            # Update booking status
            old_status = booking.status
            booking.status = 'CANCELLED'
            booking.save()

            # Send email notification
            from core.email_service import EmailService
            email_service = EmailService()
            email_service.send_booking_status_update(booking, old_status)

            return JsonResponse({
                'success': True,
                'message': 'Booking cancelled successfully.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def reschedule_booking(request, booking_id):
    """Reschedule a booking"""
    if request.method == 'POST':
        try:
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)

            # Only allow rescheduling of pending or confirmed bookings
            if booking.status not in ['PENDING', 'CONFIRMED']:
                return JsonResponse({
                    'success': False,
                    'error': 'This booking cannot be rescheduled.'
                })

            import json
            data = json.loads(request.body)
            new_date = data.get('new_date')
            new_time = data.get('new_time')

            if not new_date or not new_time:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide both new date and time.'
                })

            # Parse date and time
            from datetime import datetime
            try:
                booking_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                booking_time = datetime.strptime(new_time, '%H:%M').time()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid date or time format.'
                })

            # Check if the new time slot is available
            existing_booking = Booking.objects.filter(
                service=booking.service,
                preferred_date=booking_date,
                preferred_time=booking_time,
                status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
            ).exclude(id=booking.id).first()

            if existing_booking:
                return JsonResponse({
                    'success': False,
                    'error': 'This time slot is already booked. Please select another time.'
                })

            # Update booking
            booking.preferred_date = booking_date
            booking.preferred_time = booking_time
            booking.status = 'PENDING'  # Reset to pending for admin confirmation
            booking.save()

            return JsonResponse({
                'success': True,
                'message': 'Booking rescheduled successfully. Please wait for confirmation.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Individual Service Pages
class UoPeopleApplicationView(TemplateView):
    """University of the People Application Service Page"""
    template_name = 'services/uopeople_application.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service'] = Service.objects.get(name='University of the People Application')
        except Service.DoesNotExist:
            context['service'] = None
        return context


class GhanaUniversityApplicationView(TemplateView):
    """Ghana University Application Service Page"""
    template_name = 'services/ghana_university_application.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service'] = Service.objects.get(name='Ghana University Application')
        except Service.DoesNotExist:
            context['service'] = None
        return context


class BasicComputerSkillsView(TemplateView):
    """Basic Computer Skills Service Page"""
    template_name = 'services/basic_computer_skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service'] = Service.objects.get(name='Basic Computer Skills')
        except Service.DoesNotExist:
            context['service'] = None
        return context


class OnlineLearningSkillsView(TemplateView):
    """Online Learning Skills Service Page"""
    template_name = 'services/online_learning_skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service'] = Service.objects.get(name='Online Learning Skills')
        except Service.DoesNotExist:
            context['service'] = None
        return context


class EducationalCounselingView(TemplateView):
    """Educational Counseling Service Page"""
    template_name = 'services/educational_counseling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service'] = Service.objects.get(name='Educational Counseling')
        except Service.DoesNotExist:
            context['service'] = None
        return context
