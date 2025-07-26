from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from core.models import BaseModel
import os
import uuid
from datetime import timedelta


def user_document_path(instance, filename):
    """Generate upload path for user documents"""
    return f'user_documents/{instance.user.id}/{filename}'


class UserProfile(BaseModel):
    """Extended user profile"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('SHS', 'Senior High School'),
        ('DIPLOMA', 'Diploma'),
        ('BACHELOR', 'Bachelor\'s Degree'),
        ('MASTER', 'Master\'s Degree'),
        ('PHD', 'PhD'),
        ('OTHER', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True)
    school_name = models.CharField(max_length=200, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Tell us about yourself and your educational goals")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class UserDocument(BaseModel):
    """User uploaded documents"""
    DOCUMENT_TYPES = [
        ('ID', 'National ID/Passport'),
        ('BIRTH_CERT', 'Birth Certificate'),
        ('ACADEMIC', 'Academic Results/Transcript'),
        ('RECOMMENDATION', 'Recommendation Letter'),
        ('PERSONAL_STATEMENT', 'Personal Statement'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    document_file = models.FileField(
        upload_to=user_document_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        help_text="Allowed formats: PDF, JPG, PNG, DOC, DOCX. Max size: 5MB"
    )
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "User Document"
        verbose_name_plural = "User Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def file_size(self):
        """Get file size in MB"""
        if self.document_file:
            return round(self.document_file.size / (1024 * 1024), 2)
        return 0
    
    @property
    def file_extension(self):
        """Get file extension"""
        if self.document_file:
            return os.path.splitext(self.document_file.name)[1].lower()
        return ''


class EmailVerification(BaseModel):
    """Email verification tokens"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Email verification for {self.user.username} - {self.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if verification token is expired"""
        return timezone.now() > self.expires_at

    def verify(self):
        """Mark email as verified"""
        if not self.is_expired():
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()

            # Update user's email if different
            if self.user.email != self.email:
                self.user.email = self.email
                self.user.save()

            return True
        return False

    def send_verification_email(self):
        """Send verification email to user"""
        try:
            from django.urls import reverse
            from django.contrib.sites.models import Site
            from core.models import SiteConfiguration

            # Apply email settings
            config = SiteConfiguration.get_config()
            config.apply_email_settings()

            subject = 'Verify Your Email - Edunox GH'

            # Create verification URL with proper domain
            try:
                current_site = Site.objects.get_current()
                domain = current_site.domain
                if domain == 'example.com':  # Default Django site
                    domain = 'localhost:8000'
                protocol = 'https' if settings.DEBUG is False else 'http'
            except:
                domain = 'localhost:8000'
                protocol = 'http'

            verification_path = reverse('accounts:verify_email', kwargs={'token': self.token})
            verification_url = f"{protocol}://{domain}{verification_path}"

            # Render email template
            html_message = render_to_string('emails/email_verification.html', {
                'user': self.user,
                'verification_url': verification_url,
                'expires_at': self.expires_at,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False


class PasswordReset(BaseModel):
    """Password reset tokens"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Password reset for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=2)  # 2 hours expiry
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if reset token is expired"""
        return timezone.now() > self.expires_at

    def use_token(self):
        """Mark token as used"""
        if not self.is_expired() and not self.is_used:
            self.is_used = True
            self.used_at = timezone.now()
            self.save()
            return True
        return False
