from rest_framework import serializers

from .models import Employee, Project


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'employee_name',
            'email',
            'department',
            'job_role',
            'experience_years',
            'hire_date',
            'skills',
            'availability_status',
            'workload_percentage',
            'active_tasks',
            'performance_score',
        ]
        read_only_fields = ['employee_id']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_id',
            'project_name',
            'description',
            'start_date',
            'deadline',
            'status',
            'risk_level',
        ]
        read_only_fields = ['project_id']
