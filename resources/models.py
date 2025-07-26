from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from core.models import BaseModel


class ResourceCategory(BaseModel):
    """Categories for educational resources"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Resource Category"
        verbose_name_plural = "Resource Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Resource(BaseModel):
    """Educational resources and articles"""
    RESOURCE_TYPES = [
        ('ARTICLE', 'Article'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('LINK', 'External Link'),
        ('GUIDE', 'Guide'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='ARTICLE')
    description = models.TextField(help_text="Brief description for listings")
    content = models.TextField(blank=True, help_text="Full content for articles and guides")
    featured_image = models.ImageField(upload_to='resource_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    external_url = models.URLField(blank=True, help_text="External link URL")
    document_file = models.FileField(upload_to='resource_documents/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_resources')
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(auto_now_add=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 chars)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    
    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = self.description[:160]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('resources:detail', kwargs={'slug': self.slug})
    
    @property
    def tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ResourceView(BaseModel):
    """Track resource views for analytics"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='resource_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Resource View"
        verbose_name_plural = "Resource Views"
        unique_together = ['resource', 'user', 'ip_address']
    
    def __str__(self):
        return f"View of {self.resource.title}"


class ResourceBookmark(BaseModel):
    """User bookmarks for resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookmarks')
    
    class Meta:
        verbose_name = "Resource Bookmark"
        verbose_name_plural = "Resource Bookmarks"
        unique_together = ['user', 'resource']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.resource.title}"
