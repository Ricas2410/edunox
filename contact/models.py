from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from core.models import BaseModel
import os


def contact_attachment_path(instance, filename):
    """Generate upload path for contact attachments"""
    return f'contact_attachments/{instance.contact_message.id}/{filename}'


class ContactMessage(BaseModel):
    """Contact form messages"""
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="If user was logged in")
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_contacts',
        limit_choices_to={'is_staff': True}
    )
    admin_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    @property
    def has_attachments(self):
        return self.attachments.exists()


class ContactAttachment(BaseModel):
    """File attachments for contact messages"""
    contact_message = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to=contact_attachment_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt'])],
        help_text="Allowed formats: PDF, JPG, PNG, DOC, DOCX, TXT. Max size: 5MB"
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    
    class Meta:
        verbose_name = "Contact Attachment"
        verbose_name_plural = "Contact Attachments"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Attachment for {self.contact_message.subject}"
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class ContactReply(BaseModel):
    """Replies to contact messages"""
    contact_message = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='replies')
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_internal = models.BooleanField(default=False, help_text="Internal note, not sent to user")
    email_sent = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Contact Reply"
        verbose_name_plural = "Contact Replies"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.contact_message.subject} by {self.created_by.username}"
