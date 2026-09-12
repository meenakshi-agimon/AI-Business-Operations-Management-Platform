from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='finance_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_list, name='expenses'),
    path('budgets/', views.budget_list, name='budgets'),
    path('invoices/', views.invoice_list, name='invoices'),
    path('reports/detailed/', views.detailed_reports, name='reports'),
    path('anomalies/', views.anomaly_detection, name='anomalies'),
    path('import-csv-upload/', views.import_csv_upload, name='import-csv'),
    path('budgets/update/', views.update_budget_limit, name='update-budget'),
    path('clear/', views.clear_all, name='clear-all'),
    path('expenses/<str:expense_id>/approve/', views.approve_expense, name='approve'),
    path('expenses/<str:expense_id>/reject/', views.reject_expense, name='reject'),
    path('invoices/<str:invoice_number>/pay/', views.pay_invoice, name='pay-invoice'),
]