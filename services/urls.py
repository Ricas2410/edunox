from django.urls import path
from .views import (
    ServiceListView, ServiceDetailView, ServiceCategoryView, book_service,
    get_available_time_slots, UoPeopleApplicationView, GhanaUniversityApplicationView,
    BasicComputerSkillsView, OnlineLearningSkillsView, EducationalCounselingView,
    cancel_booking, reschedule_booking
)

app_name = 'services'

urlpatterns = [
    path('', ServiceListView.as_view(), name='list'),
    path('<int:pk>/', ServiceDetailView.as_view(), name='detail'),
    path('<int:pk>/book/', book_service, name='book'),
    path('category/<int:category_pk>/', ServiceCategoryView.as_view(), name='category'),
    path('api/time-slots/<int:service_id>/<str:date>/', get_available_time_slots, name='time_slots'),
    path('booking/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/reschedule/', reschedule_booking, name='reschedule_booking'),

    # Individual Service Pages
    path('uopeople-application/', UoPeopleApplicationView.as_view(), name='uopeople_application'),
    path('ghana-university-application/', GhanaUniversityApplicationView.as_view(), name='ghana_university_application'),
    path('basic-computer-skills/', BasicComputerSkillsView.as_view(), name='basic_computer_skills'),
    path('online-learning-skills/', OnlineLearningSkillsView.as_view(), name='online_learning_skills'),
    path('educational-counseling/', EducationalCounselingView.as_view(), name='educational_counseling'),
]
