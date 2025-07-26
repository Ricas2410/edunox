from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import BaseModel


class ServiceCategory(BaseModel):
    """Service categories for organization"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class (e.g., fas fa-graduation-cap)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Service(BaseModel):
    """Services offered by EduBridge"""
    PRICING_TYPES = [
        ('FIXED', 'Fixed Price'),
        ('ADMIN_SET', 'Admin Set Price'),
        ('ONE_TIME_CONSULTANCY', 'One-Time Consultancy'),
        ('FREE', 'Free Service'),
    ]

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=255, help_text="Brief description for cards and listings")

    # Pricing fields
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='FIXED')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in GHS", null=True, blank=True)
    admin_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Admin-set price in GHS", null=True, blank=True)
    is_one_time_consultancy = models.BooleanField(default=False, help_text="Part of one-time consultancy package")

    duration = models.CharField(max_length=100, help_text="e.g., '2 hours', '1 week', 'Ongoing'")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    features = models.TextField(help_text="List of features, one per line")
    requirements = models.TextField(blank=True, help_text="Requirements for this service")
    external_url = models.URLField(blank=True, help_text="External link if service is hosted elsewhere")
    opens_in_new_tab = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('services:detail', kwargs={'pk': self.pk})
    
    def get_effective_price(self):
        """Get the effective price based on pricing type"""
        if self.pricing_type == 'FREE':
            return 0
        elif self.pricing_type == 'ADMIN_SET' and self.admin_price:
            return self.admin_price
        elif self.pricing_type == 'ONE_TIME_CONSULTANCY':
            # One-time consultancy services are included in the package
            return 0
        else:
            return self.price or 0

    def get_price_display(self):
        """Get formatted price display"""
        if self.pricing_type == 'FREE':
            return "Free"
        elif self.pricing_type == 'ONE_TIME_CONSULTANCY':
            return "Included in Consultancy"
        elif self.pricing_type == 'ADMIN_SET':
            if self.admin_price:
                return f"GHS {self.admin_price:,.2f}"
            else:
                return "Contact for Price"
        else:
            price = self.get_effective_price()
            return f"GHS {price:,.2f}" if price > 0 else "Free"

    @property
    def features_list(self):
        """Return features as a list"""
        return [feature.strip() for feature in self.features.split('\n') if feature.strip()]

    @property
    def requirements_list(self):
        """Return requirements as a list"""
        return [req.strip() for req in self.requirements.split('\n') if req.strip()]


class OneTimeConsultancy(BaseModel):
    """One-time consultancy package configuration"""
    name = models.CharField(max_length=200, default="Complete Educational Consultancy Package")
    description = models.TextField(default="Get access to all our services with one payment")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Package price in GHS")
    duration_months = models.PositiveIntegerField(default=12, help_text="Package validity in months")
    is_active = models.BooleanField(default=True)

    # Package features
    features = models.TextField(help_text="List of package features, one per line")
    included_services = models.ManyToManyField(Service, blank=True, help_text="Services included in this package")

    class Meta:
        verbose_name = "One-Time Consultancy Package"
        verbose_name_plural = "One-Time Consultancy Packages"

    def __str__(self):
        return self.name

    @property
    def features_list(self):
        """Return features as a list"""
        return [feature.strip() for feature in self.features.split('\n') if feature.strip()]


class ConsultancyPurchase(BaseModel):
    """Track one-time consultancy purchases"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultancy_purchases')
    package = models.ForeignKey(OneTimeConsultancy, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Consultancy Purchase"
        verbose_name_plural = "Consultancy Purchases"

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

    def is_valid(self):
        """Check if the consultancy package is still valid"""
        from django.utils import timezone
        return self.is_active and timezone.now() <= self.expiry_date


class Booking(BaseModel):
    """Service bookings by users"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True, help_text="Additional message or requirements")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bookings',
        limit_choices_to={'is_staff': True}
    )

    # Pricing and payment
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Admin-quoted price")
    is_consultancy_booking = models.BooleanField(default=False, help_text="Covered by consultancy package")
    consultancy_purchase = models.ForeignKey(ConsultancyPurchase, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.status})"


class BookingUpdate(BaseModel):
    """Updates and communications for bookings"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='updates')
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_internal = models.BooleanField(default=False, help_text="Internal note, not visible to user")
    
    class Meta:
        verbose_name = "Booking Update"
        verbose_name_plural = "Booking Updates"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.booking} by {self.created_by.username}"
