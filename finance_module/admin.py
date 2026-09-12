from django.contrib import admin
from .models import Expense, Budget, Invoice

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_id', 'department', 'category', 'amount', 'vendor_name', 'approval_status')
    list_filter = ('department', 'category', 'approval_status')
    search_fields = ('expense_id', 'vendor_name')
    list_per_page = 50

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('department', 'category', 'limit_amount', 'used_amount')
    list_filter = ('department',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'vendor_name', 'amount', 'status')
    list_filter = ('status',)