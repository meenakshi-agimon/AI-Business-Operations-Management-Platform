from django.db import models
from datetime import date

class Budget(models.Model):
    department = models.CharField(max_length=100) 
    category = models.CharField(max_length=100)
    limit_amount = models.FloatField()  
    used_amount = models.FloatField(default=0)
    period = models.CharField(max_length=20, default='2026-Q1')
    source = models.CharField(max_length=20, default='csv')

    def __str__(self):
        return f"{self.department}-{self.category}: ₹{self.limit_amount}"

    @property
    def limit(self):
        return self.limit_amount
    
    @property
    def budget_limit(self):
        return self.limit_amount

    class Meta:
        db_table = 'finance_module_budget'
        unique_together = ('department', 'category')

class Expense(models.Model):
    expense_id = models.CharField(max_length=50, primary_key=True)
    department = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    amount = models.FloatField(default=0)
    budget_used = models.FloatField(default=0)
    budget_allocated = models.FloatField(default=0)
    budget_limit = models.FloatField(default=0)
    vendor_name = models.CharField(max_length=200, default='Unknown', db_index=True)
    payment_method = models.CharField(max_length=50, default='Cash')
    # Keep as CharField to avoid date parsing errors from CSV - simplest for submission
    expense_date = models.CharField(max_length=20, default='2024-01-01')
    expense_priority = models.CharField(max_length=20, default='Medium')
    approval_status = models.CharField(max_length=20, default='Pending', db_index=True)

    def __str__(self):
        return self.expense_id

    @property
    def vendor(self):
        return self.vendor_name

    @property
    def priority(self):
        return self.expense_priority

    class Meta:
        db_table = 'finance_module_expense'
        ordering = ['-expense_id']

class Invoice(models.Model): 
    invoice_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    vendor_name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, default='Unknown') # extra for compatibility
    amount = models.FloatField()
    status = models.CharField(max_length=20, default='pending')
    expense_date = models.CharField(max_length=20, default='2024-01-01')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default='Cash', null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.invoice_number

    class Meta:
        db_table = 'finance_module_invoice'