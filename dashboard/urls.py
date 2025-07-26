from django.urls import path
from .views import (
    UserDashboardView, UserBookingsView, UserDocumentsView, UserProfileView,
    AdminDashboardView, AdminBookingsView, AdminContactsView, AdminUsersView,
    AdminDocumentsView, AdminServicesView, AdminConsultancyView, AdminSettingsView,
    AdminUserAPIView, AdminServiceAPIView, AdminUserCreateAPIView, AdminConsultancyAPIView,
    AdminSettingsAPIView, AdminSettingsFileUploadAPIView, AdminEmailTestAPIView,
    update_profile_picture
)

# app_name removed to use explicit namespaces in main urls.py

urlpatterns = [
    # User Dashboard
    path('', UserDashboardView.as_view(), name='home'),
    path('bookings/', UserBookingsView.as_view(), name='bookings'),
    path('documents/', UserDocumentsView.as_view(), name='documents'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update-picture/', update_profile_picture, name='update_profile_picture'),
    
    # Admin Dashboard
    path('admin/', AdminDashboardView.as_view(), name='admin_home'),
    path('admin/bookings/', AdminBookingsView.as_view(), name='admin_bookings'),
    path('admin/contacts/', AdminContactsView.as_view(), name='admin_contacts'),
    path('admin/users/', AdminUsersView.as_view(), name='admin_users'),
    path('admin/documents/', AdminDocumentsView.as_view(), name='admin_documents'),
    path('admin/services/', AdminServicesView.as_view(), name='admin_services'),
    path('admin/consultancy/', AdminConsultancyView.as_view(), name='admin_consultancy'),
    path('admin/settings/', AdminSettingsView.as_view(), name='admin_settings'),

    # Admin API endpoints
    path('api/admin/users/<int:user_id>/', AdminUserAPIView.as_view(), name='admin_user_api'),
    path('api/admin/users/create/', AdminUserCreateAPIView.as_view(), name='admin_user_create_api'),
    path('api/admin/services/<int:service_id>/', AdminServiceAPIView.as_view(), name='admin_service_api'),
    path('api/admin/consultancy/<int:package_id>/', AdminConsultancyAPIView.as_view(), name='admin_consultancy_api'),
    path('api/admin/settings/', AdminSettingsAPIView.as_view(), name='admin_settings_api'),
    path('api/admin/settings/upload/', AdminSettingsFileUploadAPIView.as_view(), name='admin_settings_upload_api'),
    path('api/admin/settings/test-email/', AdminEmailTestAPIView.as_view(), name='admin_email_test_api'),
]
