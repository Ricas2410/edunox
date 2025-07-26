from django.urls import path
from .views import (
    RegistrationView, ProfileCompleteView, custom_login_redirect,
    MultiStepRegistrationView, upload_document_ajax, delete_document_ajax,
    send_verification_email, verify_email, EmailVerificationView,
    check_verification_status
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('register-steps/', MultiStepRegistrationView.as_view(), name='register_steps'),
    path('profile-complete/', ProfileCompleteView.as_view(), name='profile_complete'),
    path('login-redirect/', custom_login_redirect, name='login_redirect'),
    path('upload-document/', upload_document_ajax, name='upload_document_ajax'),
    path('delete-document/<int:document_id>/', delete_document_ajax, name='delete_document_ajax'),

    # Email verification
    path('send-verification/', send_verification_email, name='send_verification'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('email-verification/', EmailVerificationView.as_view(), name='email_verification'),
    path('check-verification-status/', check_verification_status, name='check_verification_status'),
]
