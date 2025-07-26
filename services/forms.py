from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Booking, Service


class BookingForm(forms.ModelForm):
    """Service booking form"""

    CONTACT_METHOD_CHOICES = [
        ('EMAIL', 'Email'),
        ('PHONE', 'Phone Call'),
        ('WHATSAPP', 'WhatsApp'),
        ('IN_PERSON', 'In Person'),
    ]

    contact_method = forms.ChoiceField(
        choices=CONTACT_METHOD_CHOICES,
        initial='EMAIL',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    emergency_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Emergency contact number'
        })
    )

    # Optional profile fields for users who haven't completed their profile
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)'
        }),
        help_text='We may need to contact you about your booking'
    )

    education_level = forms.ChoiceField(
        choices=[('', 'Select your education level (optional)')] + [
            ('HIGH_SCHOOL', 'High School'),
            ('DIPLOMA', 'Diploma/Certificate'),
            ('BACHELOR', 'Bachelor\'s Degree'),
            ('MASTER', 'Master\'s Degree'),
            ('PHD', 'PhD/Doctorate'),
            ('OTHER', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Helps us provide better service recommendations'
    )

    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions.'}
    )

    class Meta:
        model = Booking
        fields = [
            'preferred_date', 'preferred_time', 'message',
            'contact_method', 'emergency_contact'
        ]
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'preferred_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Tell us about your specific needs, goals, or any questions you have...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop('service', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set minimum date to today
        self.fields['preferred_date'].widget.attrs['min'] = timezone.now().date().isoformat()

        # Add labels and help text
        self.fields['preferred_date'].label = 'Preferred Date'
        self.fields['preferred_time'].label = 'Preferred Time'
        self.fields['message'].label = 'Message (Optional)'
        self.fields['message'].help_text = 'Share any specific requirements or questions'
        self.fields['contact_method'].label = 'Preferred Contact Method'
        self.fields['emergency_contact'].label = 'Emergency Contact (Optional)'

        # Make fields required
        self.fields['preferred_date'].required = True
        self.fields['preferred_time'].required = True

        # Check if user profile is incomplete and conditionally show profile fields
        if self.user and hasattr(self.user, 'profile'):
            profile = self.user.profile
            if profile.phone_number:
                # Remove phone field if already in profile
                del self.fields['phone_number']
            else:
                self.fields['phone_number'].label = 'Phone Number (Optional)'
                self.fields['phone_number'].help_text = 'We may need to contact you about your booking'

            if profile.education_level:
                # Remove education field if already in profile
                del self.fields['education_level']
            else:
                self.fields['education_level'].label = 'Education Level (Optional)'
                self.fields['education_level'].help_text = 'Helps us provide better service recommendations'
        else:
            # Keep fields for users without profiles
            self.fields['phone_number'].label = 'Phone Number (Optional)'
            self.fields['education_level'].label = 'Education Level (Optional)'

    def clean_preferred_date(self):
        """Validate preferred date"""
        date = self.cleaned_data.get('preferred_date')

        if not date:
            raise ValidationError('Please select a preferred date.')

        # Check if date is not in the past
        if date < timezone.now().date():
            raise ValidationError('Please select a future date.')

        # Check if date is not too far in the future (60 days)
        max_date = timezone.now().date() + timedelta(days=60)
        if date > max_date:
            raise ValidationError('Please select a date within the next 60 days.')

        # Check if date is not a Sunday (assuming business doesn't operate on Sundays)
        if date.weekday() == 6:  # Sunday = 6
            raise ValidationError('We are closed on Sundays. Please select another date.')

        return date

    def clean_preferred_time(self):
        """Validate preferred time"""
        time_value = self.cleaned_data.get('preferred_time')

        if not time_value:
            raise ValidationError('Please select a preferred time.')

        # Check business hours (9 AM to 6 PM)
        business_start = time(9, 0)  # 9:00 AM
        business_end = time(18, 0)   # 6:00 PM

        if time_value < business_start or time_value > business_end:
            raise ValidationError('Please select a time between 9:00 AM and 6:00 PM.')

        return time_value

    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        preferred_time = cleaned_data.get('preferred_time')

        if preferred_date and preferred_time:
            # Combine date and time
            preferred_datetime = datetime.combine(preferred_date, preferred_time)
            preferred_datetime = timezone.make_aware(preferred_datetime)

            # Check if the datetime is at least 2 hours from now
            min_booking_time = timezone.now() + timedelta(hours=2)
            if preferred_datetime < min_booking_time:
                raise ValidationError(
                    'Bookings must be made at least 2 hours in advance.'
                )

            # Check for existing bookings at the same time (if service is provided)
            if self.service and self.user:
                # Check if another user has booked this time slot
                existing_booking = Booking.objects.filter(
                    service=self.service,
                    preferred_date=preferred_date,
                    preferred_time=preferred_time,
                    status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
                ).exclude(user=self.user).first()

                if existing_booking:
                    raise ValidationError(
                        'This time slot is already booked. Please select another time.'
                    )

                # Check if the same user already has a pending/confirmed booking for this service
                user_existing_booking = Booking.objects.filter(
                    service=self.service,
                    user=self.user,
                    status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
                ).first()

                if user_existing_booking:
                    raise ValidationError(
                        f'You already have a {user_existing_booking.get_status_display().lower()} booking for this service. '
                        f'Please wait for it to be completed or cancelled before booking again.'
                    )

        return cleaned_data

    def save(self, commit=True):
        """Save booking with additional data and update user profile if needed"""
        booking = super().save(commit=False)

        if self.service:
            booking.service = self.service
        if self.user:
            booking.user = self.user

        if commit:
            booking.save()

            # Update user profile with any provided information
            if self.user and hasattr(self.user, 'profile'):
                profile = self.user.profile
                profile_updated = False

                # Update phone number if provided and not already set
                phone_number = self.cleaned_data.get('phone_number')
                if phone_number and not profile.phone_number:
                    profile.phone_number = phone_number
                    profile_updated = True

                # Update education level if provided and not already set
                education_level = self.cleaned_data.get('education_level')
                if education_level and not profile.education_level:
                    profile.education_level = education_level
                    profile_updated = True

                if profile_updated:
                    profile.save()

        return booking


class BookingUpdateForm(forms.ModelForm):
    """Form for updating booking status (admin use)"""

    class Meta:
        model = Booking
        fields = ['status', 'assigned_to', 'admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add notes about this booking...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-md-6 mb-3'),
                Column('assigned_to', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'admin_notes',
            Submit('submit', 'Update Booking', css_class='btn btn-primary')
        )

        # Add labels
        self.fields['status'].label = 'Booking Status'
        self.fields['assigned_to'].label = 'Assign To Staff Member'
        self.fields['admin_notes'].label = 'Admin Notes'


class ServiceSearchForm(forms.Form):
    """Service search and filter form"""

    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...'
        })
    )

    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    price_range = forms.ChoiceField(
        choices=[
            ('', 'All Prices'),
            ('0-50', 'GHS 0 - 50'),
            ('51-100', 'GHS 51 - 100'),
            ('101-200', 'GHS 101 - 200'),
            ('200+', 'GHS 200+'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import here to avoid circular imports
        from .models import ServiceCategory

        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-3'),
                Column('category', css_class='form-group col-md-4 mb-3'),
                Column('price_range', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Filter Services', css_class='btn btn-primary')
        )
