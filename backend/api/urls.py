from django.urls import path

from .views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    FinanceDetailView,
    FinanceListCreateView,
    ProjectDetailView,
    ProjectListCreateView,
    RecommendEmployeeView,
    TaskDetailView,
    TaskListCreateView,
)

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<str:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<str:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<str:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('finance/', FinanceListCreateView.as_view(), name='finance-list-create'),
    path('finance/<str:finance_id>/', FinanceDetailView.as_view(), name='finance-detail'),
    path('recommend-employee/', RecommendEmployeeView.as_view(), name='recommend-employee'),
]
