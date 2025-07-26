from django.contrib import admin
from .models import ContactMessage, ContactAttachment, ContactReply


class ContactAttachmentInline(admin.TabularInline):
    model = ContactAttachment
    extra = 0
    readonly_fields = ['original_filename', 'file_size_mb', 'created_at']
    fields = ['file', 'original_filename', 'file_size_mb', 'created_at']


class ContactReplyInline(admin.TabularInline):
    model = ContactReply
    extra = 0
    readonly_fields = ['created_at']
    fields = ['message', 'created_by', 'is_internal', 'email_sent', 'created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'has_attachments', 'assigned_to', 'created_at']
    list_filter = ['status', 'created_at', 'assigned_to']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['status', 'assigned_to']
    ordering = ['-created_at']
    inlines = [ContactAttachmentInline, ContactReplyInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'user')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Management', {
            'fields': ('status', 'assigned_to', 'admin_notes', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assigned_to')


@admin.register(ContactAttachment)
class ContactAttachmentAdmin(admin.ModelAdmin):
    list_display = ['contact_message', 'original_filename', 'file_size_mb', 'created_at']
    list_filter = ['created_at']
    search_fields = ['contact_message__name', 'contact_message__subject', 'original_filename']
    readonly_fields = ['original_filename', 'file_size', 'file_size_mb', 'file_extension', 'created_at']
    ordering = ['-created_at']


@admin.register(ContactReply)
class ContactReplyAdmin(admin.ModelAdmin):
    list_display = ['contact_message', 'created_by', 'is_internal', 'email_sent', 'created_at']
    list_filter = ['is_internal', 'email_sent', 'created_at']
    search_fields = ['contact_message__name', 'contact_message__subject', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
