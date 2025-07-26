from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserDocument


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserDocumentInline(admin.TabularInline):
    model = UserDocument
    fk_name = 'user'
    extra = 0
    readonly_fields = ['file_size', 'file_extension', 'created_at']
    fields = ['document_type', 'title', 'document_file', 'is_verified', 'file_size', 'created_at']


class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, UserDocumentInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'get_phone_number']
    list_filter = BaseUserAdmin.list_filter + ('profile__is_verified',)
    
    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone_number.short_description = 'Phone Number'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'education_level', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'education_level', 'gender', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'date_of_birth', 'gender')
        }),
        ('Address', {
            'fields': ('address', 'city', 'region')
        }),
        ('Education', {
            'fields': ('education_level', 'school_name', 'graduation_year', 'bio')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'is_verified', 'verification_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_type', 'title', 'file_size', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'title', 'description']
    readonly_fields = ['file_size', 'file_extension', 'created_at', 'updated_at']
    fieldsets = (
        ('Document Information', {
            'fields': ('user', 'document_type', 'title', 'document_file', 'description')
        }),
        ('File Details', {
            'fields': ('file_size', 'file_extension'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date', 'verification_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
