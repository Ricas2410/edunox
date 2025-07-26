from django.contrib import admin
from .models import SiteConfiguration, FAQ, NavigationMenuItem


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'has_logo', 'has_banner', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['site_name', 'contact_email']
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'is_active')
        }),
        ('Branding & Images', {
            'fields': ('logo', 'favicon', 'banner_image', 'hero_image'),
            'description': 'Upload logo, favicon, and banner images for your site'
        }),
        ('Page Images', {
            'fields': ('about_page_image', 'services_page_image', 'resources_page_image', 'contact_page_image'),
            'description': 'Hero images for different pages'
        }),
        ('About Page Section Images', {
            'fields': ('about_mission_image', 'about_approach_image'),
            'description': 'Images for specific sections on the About page'
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('External Links', {
            'fields': ('library_url', 'library_opens_new_tab', 'jobs_url', 'jobs_opens_new_tab'),
            'description': 'Configure external links for navigation'
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
    )

    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Logo'

    def has_banner(self, obj):
        return bool(obj.banner_image)
    has_banner.boolean = True
    has_banner.short_description = 'Banner'


@admin.register(NavigationMenuItem)
class NavigationMenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu_type', 'link_type', 'group_name', 'order', 'is_active']
    list_filter = ['menu_type', 'link_type', 'is_active', 'opens_new_tab']
    search_fields = ['name', 'group_name', 'internal_url_name', 'external_url']
    list_editable = ['order', 'is_active']
    ordering = ['menu_type', 'order', 'name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('menu_type', 'name', 'icon', 'group_name')
        }),
        ('Link Configuration', {
            'fields': ('link_type', 'internal_url_name', 'external_url', 'service')
        }),
        ('Display Options', {
            'fields': ('opens_new_tab', 'order', 'is_active')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for common URL names
        if 'internal_url_name' in form.base_fields:
            form.base_fields['internal_url_name'].help_text = (
                "Common URL names: services:list, core:about, contact:contact, "
                "resources:list, core:faq, dashboard:home"
            )
        return form


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'created_at']
