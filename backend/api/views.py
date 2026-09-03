from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Finance, Project, Task
from .serializers import (
    EmployeeRecommendationSerializer,
    EmployeeSerializer,
    FinanceSerializer,
    ProjectSerializer,
    RecommendEmployeeRequestSerializer,
    TaskSerializer,
)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'employee_id'


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'


class FinanceListCreateView(generics.ListCreateAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer


class FinanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    lookup_field = 'finance_id'


class RecommendEmployeeView(APIView):
    def get_recommendations(
        self,
        required_skill=None,
        task_priority='Medium',
        estimated_hours=40.0,
        task_id=None,
        top_n=5
    ):
        if task_id and not required_skill:
            try:
                task = Task.objects.filter(task_id=task_id).first()
                if task:
                    required_skill = task.required_skill or required_skill
                    task_priority = task.task_priority or task_priority
                    estimated_hours = float(task.estimated_hours or estimated_hours)
            except Exception:
                pass

        req_skill_str = (required_skill or '').strip().lower()

        try:
            employees = list(Employee.objects.all())
        except Exception:
            employees = []

        results = []
        for emp in employees:
            skills_raw = emp.skills or ''
            emp_skills = [s.strip().lower() for s in skills_raw.replace(';', ',').split(',')]
            emp_skills = [s for s in emp_skills if s]

            # 1. Skill Match
            if not req_skill_str:
                skill_score = 0.8
                skill_matched = 'General'
            else:
                matched_items = [s for s in emp_skills if req_skill_str in s or s in req_skill_str or req_skill_str == s]
                if matched_items:
                    skill_score = 1.0
                    skill_matched = matched_items[0]
                elif req_skill_str in (emp.job_role or '').lower() or req_skill_str in (emp.department or '').lower():
                    skill_score = 0.75
                    skill_matched = emp.job_role or emp.department or req_skill_str
                else:
                    skill_score = 0.15
                    skill_matched = None

            # 2. Availability
            avail_str = (emp.availability_status or '').strip().lower()
            if avail_str == 'available':
                avail_score = 1.0
            elif avail_str == 'busy':
                avail_score = 0.45
            elif avail_str in ('on leave', 'leave'):
                avail_score = 0.05
            else:
                avail_score = 0.5

            # 3. Workload
            try:
                workload_val = float(emp.workload_percentage or 0.0)
            except (ValueError, TypeError):
                workload_val = 0.0
            workload_score = max(0.0, min(1.0, 1.0 - (workload_val / 100.0)))

            # 4. Performance
            try:
                perf_val = float(emp.performance_score or 0.0)
            except (ValueError, TypeError):
                perf_val = 0.0
            perf_score = max(0.0, min(1.0, perf_val / 100.0))

            # 5. Experience
            try:
                exp_val = float(emp.experience_years or 0.0)
            except (ValueError, TypeError):
                exp_val = 0.0
            exp_score = min(1.0, exp_val / 10.0)

            # 6. Active Tasks
            try:
                tasks_val = int(emp.active_tasks or 0)
            except (ValueError, TypeError):
                tasks_val = 0
            tasks_score = max(0.0, 1.0 - (tasks_val / 10.0))

            composite_score = (
                skill_score * 35.0
                + perf_score * 25.0
                + avail_score * 15.0
                + workload_score * 15.0
                + exp_score * 5.0
                + tasks_score * 5.0
            )

            is_recommended = composite_score >= 55.0 and avail_score > 0.1

            reasons = []
            if skill_matched:
                reasons.append(f"Skill matched: {skill_matched}")
            if perf_val >= 75.0:
                reasons.append(f"High performance score ({perf_val:.1f})")
            if avail_str == 'available' and workload_val < 70.0:
                reasons.append(f"Available with manageable workload ({workload_val:.1f}%)")
            if exp_val >= 3.0:
                reasons.append(f"{exp_val:.1f} years of experience")

            if not reasons:
                reasons.append("General profile match")

            results.append({
                'employee_id': emp.employee_id,
                'employee_name': emp.employee_name or emp.employee_id,
                'email': emp.email,
                'department': emp.department,
                'job_role': emp.job_role,
                'skills': emp.skills,
                'availability_status': emp.availability_status,
                'workload_percentage': emp.workload_percentage,
                'active_tasks': emp.active_tasks,
                'performance_score': emp.performance_score,
                'experience_years': emp.experience_years,
                'match_score': round(composite_score, 2),
                'recommended': is_recommended,
                'match_reasons': reasons,
            })

        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:top_n], len(employees)

    def post(self, request, *args, **kwargs):
        serializer = RecommendEmployeeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        recommendations, total_candidates = self.get_recommendations(
            required_skill=data.get('required_skill'),
            task_priority=data.get('task_priority', 'Medium'),
            estimated_hours=float(data.get('estimated_hours') or 40.0),
            task_id=data.get('task_id'),
            top_n=data.get('top_n', 5),
        )

        return Response({
            'status': 'success',
            'task_criteria': {
                'task_id': data.get('task_id'),
                'required_skill': data.get('required_skill'),
                'task_priority': data.get('task_priority'),
                'estimated_hours': float(data.get('estimated_hours')) if data.get('estimated_hours') is not None else None,
            },
            'total_candidates_evaluated': total_candidates,
            'recommendations': recommendations,
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        serializer = RecommendEmployeeRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        recommendations, total_candidates = self.get_recommendations(
            required_skill=data.get('required_skill'),
            task_priority=data.get('task_priority', 'Medium'),
            estimated_hours=float(data.get('estimated_hours') or 40.0),
            task_id=data.get('task_id'),
            top_n=data.get('top_n', 5),
        )

        return Response({
            'status': 'success',
            'task_criteria': {
                'task_id': data.get('task_id'),
                'required_skill': data.get('required_skill'),
                'task_priority': data.get('task_priority'),
                'estimated_hours': float(data.get('estimated_hours')) if data.get('estimated_hours') is not None else None,
            },
            'total_candidates_evaluated': total_candidates,
            'recommendations': recommendations,
        }, status=status.HTTP_200_OK)
