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
