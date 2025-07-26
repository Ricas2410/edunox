"""
Email notification service for EduBridge Ghana
Handles all email communications including welcome emails, booking confirmations, etc.
"""

import logging
from typing import Dict, List, Optional, Any
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from celery import shared_task

logger = logging.getLogger(__name__)


class EmailService:
    """Centralized email service for all notifications"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edubridge.com')
        self.site_url = self._get_site_url()
    
    def _get_site_url(self) -> str:
        """Get the current site URL"""
        try:
            site = Site.objects.get_current()
            protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
            return f"{protocol}://{site.domain}"
        except:
            return getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    def send_email(
        self,
        template_name: str,
        context: Dict[str, Any],
        to_emails: List[str],
        subject: str,
        from_email: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List] = None
    ) -> bool:
        """
        Send an email using HTML template
        
        Args:
            template_name: Name of the email template (without .html)
            context: Template context variables
            to_emails: List of recipient email addresses
            subject: Email subject
            from_email: Sender email (optional)
            cc_emails: CC recipients (optional)
            bcc_emails: BCC recipients (optional)
            attachments: File attachments (optional)
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Add site URL to context
            context['site_url'] = self.site_url
            
            # Render HTML content
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Create plain text version
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email or self.from_email,
                to=to_emails,
                cc=cc_emails or [],
                bcc=bcc_emails or []
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)
            
            # Send email
            email.send()
            
            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {', '.join(to_emails)}: {str(e)}")
            return False
    
    def send_welcome_email(self, user) -> bool:
        """Send welcome email to new users"""
        context = {
            'user': user,
        }
        
        return self.send_email(
            template_name='welcome',
            context=context,
            to_emails=[user.email],
            subject='Welcome to EduBridge Ghana - Your Educational Journey Starts Here!'
        )
    
    def send_booking_confirmation(self, booking) -> bool:
        """Send booking confirmation email"""
        context = {
            'booking': booking,
        }
        
        return self.send_email(
            template_name='booking_confirmation',
            context=context,
            to_emails=[booking.user.email],
            subject=f'Booking Confirmation - {booking.service.name} (#{booking.id})'
        )
    
    def send_booking_status_update(self, booking, old_status: str) -> bool:
        """Send email when booking status changes"""
        status_messages = {
            'CONFIRMED': 'Your booking has been confirmed!',
            'IN_PROGRESS': 'Your service is now in progress',
            'COMPLETED': 'Your service has been completed',
            'CANCELLED': 'Your booking has been cancelled'
        }
        
        context = {
            'booking': booking,
            'old_status': old_status,
            'status_message': status_messages.get(booking.status, 'Your booking status has been updated')
        }
        
        subject = f'Booking Update - {booking.service.name} (#{booking.id})'
        
        return self.send_email(
            template_name='booking_status_update',
            context=context,
            to_emails=[booking.user.email],
            subject=subject
        )
    
    def send_document_verification_email(self, document, is_verified: bool) -> bool:
        """Send email when document verification status changes"""
        context = {
            'document': document,
            'is_verified': is_verified,
        }
        
        status = 'verified' if is_verified else 'rejected'
        subject = f'Document {status.title()} - {document.title}'
        
        return self.send_email(
            template_name='document_verification',
            context=context,
            to_emails=[document.user.email],
            subject=subject
        )
    
    def send_contact_message_confirmation(self, contact_message) -> bool:
        """Send confirmation email for contact form submissions"""
        context = {
            'message': contact_message,
        }
        
        return self.send_email(
            template_name='contact_confirmation',
            context=context,
            to_emails=[contact_message.email],
            subject='Message Received - We\'ll Get Back to You Soon!'
        )
    
    def send_admin_notification(self, subject: str, message: str, context: Dict = None) -> bool:
        """Send notification email to administrators"""
        admin_emails = getattr(settings, 'ADMIN_EMAILS', ['admin@edubridge.com'])
        
        context = context or {}
        context['message'] = message
        
        return self.send_email(
            template_name='admin_notification',
            context=context,
            to_emails=admin_emails,
            subject=f'[EduBridge Admin] {subject}'
        )
    
    def send_password_reset_email(self, user, reset_url: str) -> bool:
        """Send password reset email"""
        context = {
            'user': user,
            'reset_url': reset_url,
        }
        
        return self.send_email(
            template_name='password_reset',
            context=context,
            to_emails=[user.email],
            subject='Reset Your EduBridge Ghana Password'
        )
    
    def send_newsletter(self, subscribers: List[str], subject: str, content: str) -> bool:
        """Send newsletter to subscribers"""
        context = {
            'content': content,
        }
        
        return self.send_email(
            template_name='newsletter',
            context=context,
            to_emails=[],  # Empty to_emails since we're using BCC
            bcc_emails=subscribers,
            subject=subject
        )


# Celery tasks for asynchronous email sending
@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self, user_id: int):
    """Async task to send welcome email"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        email_service = EmailService()
        
        success = email_service.send_welcome_email(user)
        
        if not success:
            raise Exception("Failed to send welcome email")
            
        return f"Welcome email sent to {user.email}"
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_task(self, booking_id: int):
    """Async task to send booking confirmation email"""
    try:
        from services.models import Booking
        
        booking = Booking.objects.select_related('user', 'service').get(id=booking_id)
        email_service = EmailService()
        
        success = email_service.send_booking_confirmation(booking)
        
        if not success:
            raise Exception("Failed to send booking confirmation email")
            
        return f"Booking confirmation sent to {booking.user.email}"
        
    except Exception as exc:
        logger.error(f"Failed to send booking confirmation: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_document_verification_task(self, document_id: int, is_verified: bool):
    """Async task to send document verification email"""
    try:
        from accounts.models import UserDocument
        
        document = UserDocument.objects.select_related('user').get(id=document_id)
        email_service = EmailService()
        
        success = email_service.send_document_verification_email(document, is_verified)
        
        if not success:
            raise Exception("Failed to send document verification email")
            
        return f"Document verification email sent to {document.user.email}"
        
    except Exception as exc:
        logger.error(f"Failed to send document verification email: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def send_admin_notification_task(subject: str, message: str, context: Dict = None):
    """Async task to send admin notification"""
    try:
        email_service = EmailService()
        success = email_service.send_admin_notification(subject, message, context)
        
        if success:
            return f"Admin notification sent: {subject}"
        else:
            return f"Failed to send admin notification: {subject}"
            
    except Exception as exc:
        logger.error(f"Failed to send admin notification: {exc}")
        return f"Error sending admin notification: {exc}"


# Convenience function to get email service instance
def get_email_service() -> EmailService:
    """Get EmailService instance"""
    return EmailService()
