from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.db import IntegrityError
import json
import logging

# Get logger for this module
logger = logging.getLogger(__name__)
from .forms import RegistrationForm, UserDocumentForm
from .models import UserProfile, UserDocument, EmailVerification


class RegistrationView(CreateView):
    """Simple user registration view"""
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:home')
    
    def form_valid(self, form):
        """Handle successful form submission with error handling"""
        try:
            # Save the user
            response = super().form_valid(form)

            # Create email verification
            verification = EmailVerification.objects.create(
                user=self.object,
                email=self.object.email
            )

            # Send verification email
            if verification.send_verification_email():
                messages.success(
                    self.request,
                    'Welcome to Edunox GH! Your account has been created successfully. '
                    'Please check your email to verify your account.'
                )
            else:
                messages.warning(
                    self.request,
                    'Account created successfully, but we couldn\'t send the verification email. '
                    'You can request a new verification email from your profile page.'
                )

            # Log the user in automatically with backend specified
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            login(self.request, self.object, backend=f'{backend.__module__}.{backend.__class__.__name__}')

            return redirect('dashboard:home')

        except IntegrityError as e:
            # Handle database integrity errors (duplicate username/email)
            if 'username' in str(e).lower():
                form.add_error('username', 'This username is already taken. Please choose a different one.')
            elif 'email' in str(e).lower():
                form.add_error('email', 'An account with this email address already exists.')
            else:
                form.add_error(None, 'An account with these details already exists. Please try different information.')

            messages.error(
                self.request,
                'Registration failed. Please check the form for errors and try again.'
            )
            return self.form_invalid(form)

        except Exception as e:
            # Handle any other unexpected errors
            messages.error(
                self.request,
                'An unexpected error occurred during registration. Please try again later.'
            )
            # Log the error for debugging
            logger.error(f"Registration error for user {form.cleaned_data.get('email', 'unknown')}: {str(e)}", exc_info=True)
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Your Account'
        context['page_description'] = 'Join EduBridge Ghana and start your educational journey'
        return context


@method_decorator(login_required, name='dispatch')
class ProfileCompleteView(TemplateView):
    """Profile completion guide"""
    template_name = 'accounts/profile_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            # Calculate completion percentage
            completion_fields = [
                profile.phone_number,
                profile.date_of_birth,
                profile.address,
                profile.education_level,
                profile.bio,
                profile.profile_picture
            ]
            completed_fields = sum(1 for field in completion_fields if field)
            context['completion_percentage'] = (completed_fields / len(completion_fields)) * 100
            
            # Missing fields
            missing_fields = []
            if not profile.phone_number:
                missing_fields.append('Phone Number')
            if not profile.date_of_birth:
                missing_fields.append('Date of Birth')
            if not profile.address:
                missing_fields.append('Address')
            if not profile.education_level:
                missing_fields.append('Education Level')
            if not profile.bio:
                missing_fields.append('Bio')
            if not profile.profile_picture:
                missing_fields.append('Profile Picture')
            
            context['missing_fields'] = missing_fields
        else:
            context['completion_percentage'] = 0
            context['missing_fields'] = ['Complete Profile Setup']
        
        return context


def custom_login_redirect(request):
    """Custom login redirect based on user type"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:admin_home')
        else:
            return redirect('dashboard:home')
    return redirect('account_login')


class MultiStepRegistrationView(TemplateView):
    """Multi-step registration with document upload"""
    template_name = 'accounts/multi_step_registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_form'] = RegistrationForm()
        context['document_form'] = UserDocumentForm()
        context['page_title'] = 'Create Your Account'
        context['page_description'] = 'Join EduBridge Ghana in 3 simple steps'
        return context

    def post(self, request, *args, **kwargs):
        step = request.POST.get('step', '1')

        if step == '1':
            return self.handle_step_1(request)
        elif step == '2':
            return self.handle_step_2(request)
        elif step == '3':
            return self.handle_step_3(request)

        return self.get(request, *args, **kwargs)

    def handle_step_1(self, request):
        """Handle user account creation with error handling"""
        form = RegistrationForm(request.POST)

        if form.is_valid():
            try:
                user = form.save()

                # Log the user in with backend specified
                from django.contrib.auth import get_backends
                backend = get_backends()[0]
                login(request, user, backend=f'{backend.__module__}.{backend.__class__.__name__}')

                # Store user ID in session for next steps
                request.session['registration_user_id'] = user.id
                request.session['registration_step'] = 2

                return JsonResponse({
                    'success': True,
                    'message': 'Account created successfully! Please complete your profile.',
                    'next_step': 2
                })
            except IntegrityError as e:
                logger.error(f"Multi-step registration IntegrityError: {str(e)}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'errors': {'email': ['An account with this email address already exists.']},
                    'message': 'Registration failed. An account with this email already exists.'
                })
            except Exception as e:
                logger.error(f"Multi-step registration error: {str(e)}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['An unexpected error occurred. Please try again.']},
                    'message': 'Registration failed. Please try again later.'
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.'
            })

    def handle_step_2(self, request):
        """Handle profile completion"""
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Please complete step 1 first.',
                'redirect': True
            })

        # Update profile with additional information
        profile = request.user.profile
        profile.phone_number = request.POST.get('phone_number', '')
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.region = request.POST.get('region', '')
        profile.education_level = request.POST.get('education_level', '')
        profile.school_name = request.POST.get('school_name', '')
        profile.graduation_year = request.POST.get('graduation_year') or None
        profile.bio = request.POST.get('bio', '')

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()

        request.session['registration_step'] = 3

        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully! Now upload your documents.',
            'next_step': 3
        })

    def handle_step_3(self, request):
        """Handle document uploads"""
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Please complete previous steps first.',
                'redirect': True
            })

        uploaded_documents = []

        # Handle ID document
        if 'id_document' in request.FILES:
            doc = UserDocument.objects.create(
                user=request.user,
                document_type='ID',
                title='National ID/Passport',
                document_file=request.FILES['id_document'],
                description='Identity verification document'
            )
            uploaded_documents.append(doc.title)

        # Handle academic results
        if 'academic_results' in request.FILES:
            doc = UserDocument.objects.create(
                user=request.user,
                document_type='ACADEMIC',
                title='Academic Results',
                document_file=request.FILES['academic_results'],
                description='Academic transcripts/results'
            )
            uploaded_documents.append(doc.title)

        # Handle additional documents
        for i, file in enumerate(request.FILES.getlist('additional_documents')):
            if i < 3:  # Limit to 3 additional documents
                doc = UserDocument.objects.create(
                    user=request.user,
                    document_type='OTHER',
                    title=f'Additional Document {i+1}',
                    document_file=file,
                    description='Additional supporting document'
                )
                uploaded_documents.append(doc.title)

        # Clear registration session data
        request.session.pop('registration_user_id', None)
        request.session.pop('registration_step', None)

        messages.success(
            request,
            f'Registration completed successfully! Uploaded documents: {", ".join(uploaded_documents)}. '
            'Your documents will be reviewed and verified by our team.'
        )

        return JsonResponse({
            'success': True,
            'message': 'Registration completed successfully!',
            'redirect_url': reverse_lazy('dashboard:home')
        })


@login_required
def upload_document_ajax(request):
    """AJAX document upload endpoint with error handling"""
    if request.method == 'POST':
        try:
            form = UserDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save(commit=False)
                document.user = request.user
                document.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Document uploaded successfully!',
                    'document': {
                        'id': document.id,
                        'title': document.title,
                        'type': document.get_document_type_display(),
                        'size': document.file_size,
                        'created_at': document.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
        except Exception as e:
            logger.error(f"Document upload error for user {request.user.id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while uploading the document. Please try again.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def delete_document_ajax(request, document_id):
    """AJAX document deletion endpoint"""
    if request.method == 'POST':
        try:
            document = UserDocument.objects.get(id=document_id, user=request.user)
            document_title = document.title
            document.delete()

            return JsonResponse({
                'success': True,
                'message': f'Document "{document_title}" deleted successfully!'
            })
        except UserDocument.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Document not found or you do not have permission to delete it.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def send_verification_email(request):
    """Send email verification to user"""
    if request.method == 'POST' and request.user.is_authenticated:
        # Create or get existing verification
        verification, created = EmailVerification.objects.get_or_create(
            user=request.user,
            email=request.user.email,
            is_verified=False,
            defaults={'expires_at': timezone.now() + timezone.timedelta(hours=24)}
        )

        if verification.send_verification_email():
            messages.success(request, 'Verification email sent! Please check your inbox.')
        else:
            messages.error(request, 'Failed to send verification email. Please try again.')

    return redirect('dashboard:user_dashboard')


def verify_email(request, token):
    """Verify email address using token"""
    try:
        verification = EmailVerification.objects.get(token=token, is_verified=False)

        if verification.is_expired():
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('dashboard:user_dashboard')

        if verification.verify():
            messages.success(request, 'Email verified successfully!')

            # Update user profile verification status
            if hasattr(verification.user, 'profile'):
                profile = verification.user.profile
                profile.is_verified = True
                profile.verification_date = timezone.now()
                profile.save()
        else:
            messages.error(request, 'Failed to verify email. Please try again.')

    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link.')

    return redirect('dashboard:user_dashboard')


class EmailVerificationView(TemplateView):
    """Email verification status page"""
    template_name = 'account/email_verification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['verification'] = EmailVerification.objects.filter(
                user=self.request.user,
                is_verified=False
            ).first()
        return context


@login_required
@require_POST
def send_verification_email(request):
    """Send verification email to the current user"""
    try:
        # Get or create email verification for the user
        verification, created = EmailVerification.objects.get_or_create(
            user=request.user,
            email=request.user.email,
            defaults={'is_verified': False}
        )

        # If already verified, don't send again
        if verification.is_verified:
            messages.info(request, 'Your email is already verified.')
            return redirect('dashboard:profile')

        # Send verification email
        if verification.send_verification_email():
            messages.success(
                request,
                'Verification email sent successfully! Please check your inbox and spam folder.'
            )
        else:
            messages.error(
                request,
                'Failed to send verification email. Please try again later or contact support.'
            )

    except Exception as e:
        messages.error(
            request,
            'An error occurred while sending the verification email. Please try again.'
        )

    return redirect('dashboard:profile')


@login_required
def check_verification_status(request):
    """Check email verification status via AJAX"""
    try:
        verification = EmailVerification.objects.filter(
            user=request.user,
            email=request.user.email
        ).first()

        is_verified = verification.is_verified if verification else False

        return JsonResponse({
            'success': True,
            'is_verified': is_verified,
            'email': request.user.email
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
