from django.contrib import admin
from .models import ResourceCategory, Resource, ResourceView, ResourceBookmark


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'resource_type', 'author', 'is_featured', 'is_published', 'views_count', 'published_at']
    list_filter = ['category', 'resource_type', 'is_featured', 'is_published', 'published_at']
    search_fields = ['title', 'description', 'content', 'tags']
    list_editable = ['is_featured', 'is_published']
    ordering = ['-published_at']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'published_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'resource_type', 'author')
        }),
        ('Content', {
            'fields': ('description', 'content', 'featured_image')
        }),
        ('Media & Links', {
            'fields': ('video_url', 'external_url', 'document_file'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'is_featured', 'is_published')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')


@admin.register(ResourceView)
class ResourceViewAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['resource__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ResourceBookmark)
class ResourceBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
