from django.urls import path

from .views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    ProjectDetailView,
    ProjectListCreateView,
    RecommendationListView,
)

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<str:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<str:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendation-list'),
]
