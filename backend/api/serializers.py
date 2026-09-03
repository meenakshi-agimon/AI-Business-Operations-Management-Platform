from rest_framework import serializers

from .models import Employee, Finance, Project, Task


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


class TaskSerializer(serializers.ModelSerializer):
    task_id = serializers.CharField(required=False)
    project_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Task
        fields = [
            'task_id',
            'project_id',
            'employee_id',
            'task_title',
            'task_description',
            'task_priority',
            'task_status',
            'task_start_date',
            'task_deadline',
            'required_skill',
            'estimated_hours',
            'hours_logged',
            'progress_percentage',
            'allocation_score',
            'recommended_employee',
        ]

    def validate_project_id(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        value = value.strip()
        if not Project.objects.filter(project_id=value).exists():
            raise serializers.ValidationError(f"Project with ID '{value}' does not exist.")
        return value

    def validate_employee_id(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        value = value.strip()
        if not Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(f"Employee with ID '{value}' does not exist.")
        return value

    def create(self, validated_data):
        if not validated_data.get('task_id'):
            import uuid
            validated_data['task_id'] = f"TSK{uuid.uuid4().hex[:6].upper()}"
        return super().create(validated_data)


class FinanceSerializer(serializers.ModelSerializer):
    finance_id = serializers.CharField(required=False)
    project_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Finance
        fields = [
            'finance_id',
            'project_id',
            'expense_type',
            'amount',
            'expense_date',
            'approval_status',
            'approved_by',
            'is_anomaly',
        ]

    def validate_project_id(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        value = value.strip()
        if not Project.objects.filter(project_id=value).exists():
            raise serializers.ValidationError(f"Project with ID '{value}' does not exist.")
        return value

    def create(self, validated_data):
        if not validated_data.get('finance_id'):
            import uuid
            validated_data['finance_id'] = f"FIN{uuid.uuid4().hex[:6].upper()}"
        return super().create(validated_data)


class RecommendEmployeeRequestSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=False, allow_blank=True)
    required_skill = serializers.CharField(required=False, allow_blank=True)
    task_priority = serializers.CharField(required=False, default='Medium', allow_blank=True)
    estimated_hours = serializers.DecimalField(required=False, max_digits=6, decimal_places=2, default=40.0, allow_null=True)
    top_n = serializers.IntegerField(required=False, default=5, min_value=1, max_value=50)


class EmployeeRecommendationSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    email = serializers.EmailField(allow_null=True, required=False)
    department = serializers.CharField(allow_null=True, required=False)
    job_role = serializers.CharField(allow_null=True, required=False)
    skills = serializers.CharField(allow_null=True, required=False)
    availability_status = serializers.CharField(allow_null=True, required=False)
    workload_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    active_tasks = serializers.IntegerField(allow_null=True, required=False)
    performance_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    experience_years = serializers.DecimalField(max_digits=4, decimal_places=1, allow_null=True, required=False)
    match_score = serializers.FloatField()
    recommended = serializers.BooleanField()
    match_reasons = serializers.ListField(child=serializers.CharField())
