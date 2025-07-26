from django.urls import path
from .views import ResourceListView, ResourceDetailView, ResourceCategoryView

app_name = 'resources'

urlpatterns = [
    path('', ResourceListView.as_view(), name='list'),
    path('<int:pk>/', ResourceDetailView.as_view(), name='detail'),
    path('<slug:slug>/', ResourceDetailView.as_view(), name='detail_slug'),
    path('category/<int:category_pk>/', ResourceCategoryView.as_view(), name='category'),
]
