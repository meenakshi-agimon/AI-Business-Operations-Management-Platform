from django.db import models


class Employee(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=20)
    employee_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    job_role = models.CharField(max_length=50, blank=True, null=True)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    availability_status = models.CharField(max_length=20, blank=True, null=True)
    workload_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    active_tasks = models.IntegerField(blank=True, null=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'employees'
        managed = True

    def __str__(self):
        return self.employee_name or self.employee_id


class Project(models.Model):
    project_id = models.CharField(primary_key=True, max_length=20)
    project_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'projects'
        managed = True

    def __str__(self):
        return self.project_name or self.project_id

class Task(models.Model):
    task_id = models.CharField(primary_key=True, max_length=20)
    project_id = models.CharField(max_length=20, blank=True, null=True)
    employee_id = models.CharField(max_length=20, blank=True, null=True)
    task_title = models.CharField(max_length=150, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_priority = models.CharField(max_length=20, blank=True, null=True)
    task_status = models.CharField(max_length=20, blank=True, null=True)
    task_start_date = models.DateField(blank=True, null=True)
    task_deadline = models.DateField(blank=True, null=True)
    required_skill = models.CharField(max_length=50, blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hours_logged = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    allocation_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recommended_employee = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'tasks'
        managed = False

    def __str__(self):
        return self.task_title or self.task_id


class Finance(models.Model):
    finance_id = models.CharField(primary_key=True, max_length=20)
    project_id = models.CharField(max_length=20, blank=True, null=True)
    expense_type = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    expense_date = models.DateField(blank=True, null=True)
    approval_status = models.CharField(max_length=20, blank=True, null=True)
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    is_anomaly = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'finance'
        managed = False

    def __str__(self):
        return f"{self.finance_id} - {self.expense_type}"
