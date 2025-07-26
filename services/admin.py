from django.contrib import admin
from .models import ServiceCategory, Service, Booking, OneTimeConsultancy, ConsultancyPurchase


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'pricing_type', 'get_price_display', 'is_featured', 'is_active', 'order']
    list_filter = ['category', 'pricing_type', 'is_featured', 'is_active', 'is_one_time_consultancy', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    list_editable = ['pricing_type', 'is_featured', 'is_active', 'order']
    ordering = ['category', 'order', 'name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'short_description', 'description')
        }),
        ('Pricing Configuration', {
            'fields': ('pricing_type', 'price', 'admin_price', 'is_one_time_consultancy'),
            'description': 'Configure how this service is priced'
        }),
        ('Service Details', {
            'fields': ('duration',)
        }),
        ('Visual Elements', {
            'fields': ('icon', 'image')
        }),
        ('Details', {
            'fields': ('features', 'requirements')
        }),
        ('External Link', {
            'fields': ('external_url', 'opens_in_new_tab'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )

    def get_price_display(self, obj):
        return obj.get_price_display()
    get_price_display.short_description = 'Price'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'preferred_date', 'status', 'get_price_info', 'assigned_to', 'created_at']
    list_filter = ['status', 'service__category', 'is_consultancy_booking', 'preferred_date', 'created_at']
    search_fields = ['user__username', 'user__email', 'service__name', 'message']
    list_editable = ['status', 'assigned_to']
    ordering = ['-created_at']
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'preferred_date', 'preferred_time', 'message')
        }),
        ('Pricing & Payment', {
            'fields': ('quoted_price', 'is_consultancy_booking', 'consultancy_purchase'),
            'description': 'Set custom pricing or link to consultancy package'
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('confirmed_date', 'completed_date'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service', 'assigned_to', 'consultancy_purchase')

    def get_price_info(self, obj):
        if obj.is_consultancy_booking:
            return "Consultancy Package"
        elif obj.quoted_price:
            return f"GHS {obj.quoted_price:,.2f}"
        else:
            return obj.service.get_price_display()
    get_price_info.short_description = 'Price'


@admin.register(OneTimeConsultancy)
class OneTimeConsultancyAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_months', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'duration_months', 'is_active']
    filter_horizontal = ['included_services']
    fieldsets = (
        ('Package Information', {
            'fields': ('name', 'description', 'price', 'duration_months', 'is_active')
        }),
        ('Package Features', {
            'fields': ('features',)
        }),
        ('Included Services', {
            'fields': ('included_services',)
        }),
    )


@admin.register(ConsultancyPurchase)
class ConsultancyPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'purchase_date', 'expiry_date', 'amount_paid', 'is_active']
    list_filter = ['package', 'is_active', 'purchase_date', 'expiry_date']
    search_fields = ['user__username', 'user__email', 'package__name']
    list_editable = ['is_active']
    ordering = ['-purchase_date']
    readonly_fields = ['purchase_date']
    fieldsets = (
        ('Purchase Information', {
            'fields': ('user', 'package', 'amount_paid', 'purchase_date')
        }),
        ('Validity', {
            'fields': ('expiry_date', 'is_active')
        }),
    )
