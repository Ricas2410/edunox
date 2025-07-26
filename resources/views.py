from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Resource, ResourceCategory, ResourceView


class ResourceListView(ListView):
    """List all published resources"""
    model = Resource
    template_name = 'resources/list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Resource.objects.filter(is_published=True).select_related('category', 'author')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__name__icontains=category_slug)
        
        # Filter by resource type
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ResourceCategory.objects.filter(is_active=True)
        context['resource_types'] = Resource.RESOURCE_TYPES
        context['featured_resources'] = Resource.objects.filter(
            is_published=True, 
            is_featured=True
        ).select_related('category')[:3]
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_type'] = self.request.GET.get('type', '')
        return context


class ResourceDetailView(DetailView):
    """Resource detail view"""
    model = Resource
    template_name = 'resources/detail.html'
    context_object_name = 'resource'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Get object by pk or slug"""
        if queryset is None:
            queryset = self.get_queryset()

        # Try to get by pk first
        pk = self.kwargs.get('pk')
        if pk is not None:
            try:
                obj = queryset.get(pk=pk)
            except Resource.DoesNotExist:
                from django.http import Http404
                raise Http404("No Resource found matching the query")
        else:
            # Fall back to slug
            obj = super().get_object(queryset)

        # Track view
        user = self.request.user if self.request.user.is_authenticated else None
        ip_address = self.get_client_ip()

        # Create or get view record
        view_obj, created = ResourceView.objects.get_or_create(
            resource=obj,
            user=user,
            ip_address=ip_address,
            defaults={
                'user_agent': self.request.META.get('HTTP_USER_AGENT', '')[:500]
            }
        )

        # Increment view count if new view
        if created:
            obj.increment_views()

        return obj
    
    def get_queryset(self):
        return Resource.objects.filter(is_published=True).select_related('category', 'author')
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Related resources
        context['related_resources'] = Resource.objects.filter(
            category=self.object.category,
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        
        # Check if user has bookmarked this resource
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = self.object.bookmarks.filter(
                user=self.request.user
            ).exists()
        
        return context


class ResourceCategoryView(ListView):
    """Resources by category"""
    model = Resource
    template_name = 'resources/category.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(ResourceCategory, pk=self.kwargs['category_pk'], is_active=True)
        return Resource.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('category', 'author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = ResourceCategory.objects.filter(is_active=True)
        return context
