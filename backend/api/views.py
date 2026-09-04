from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Finance, Project, Task
from .ml_services import (
    MLModelError,
    get_delay_feature_list,
    get_delay_model,
    get_risk_model,
)
from .serializers import (
    EmployeeRecommendationSerializer,
    EmployeeSerializer,
    FinanceSerializer,
    ProjectDelayPredictionRequestSerializer,
    ProjectSerializer,
    RecommendEmployeeRequestSerializer,
    RiskPredictionRequestSerializer,
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


class RiskPredictionView(APIView):
    """
    POST /api/ml/risk-prediction/
    Predict project risk level (Low, Medium, High, Critical) using trained XGBoost model.
    """

    RISK_LEVEL_MAP = {
        0: 'Low',
        1: 'Medium',
        2: 'High',
        3: 'Critical',
    }

    FEATURE_NAMES = [
        'total_tasks',
        'avg_progress',
        'avg_estimated_hours',
        'avg_hours_logged',
        'avg_allocation_score',
        'avg_workload',
        'avg_experience',
        'avg_performance',
    ]

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not data.get('project_id') and request.query_params.get('project_id'):
            data['project_id'] = request.query_params.get('project_id')

        serializer = RiskPredictionRequestSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project_id = serializer.validated_data['project_id'].strip()

        # 1. Fetch project from database
        project = Project.objects.filter(project_id=project_id).first()
        if not project:
            return Response(
                {'error': f"Project with ID '{project_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Fetch project's tasks
        tasks = list(Task.objects.filter(project_id=project_id))
        if not tasks:
            return Response(
                {'error': f"Project '{project_id}' has no tasks to evaluate risk."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Fetch assigned employees
        assigned_employee_ids = {
            t.employee_id.strip()
            for t in tasks
            if t.employee_id and str(t.employee_id).strip()
        }
        if not assigned_employee_ids:
            return Response(
                {'error': f"Project '{project_id}' tasks have no assigned employees to evaluate risk."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employees = list(Employee.objects.filter(employee_id__in=assigned_employee_ids))
        if not employees:
            return Response(
                {'error': f"No employee records found for the assigned tasks in project '{project_id}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Calculate exactly the 8 project-level features
        total_tasks = float(len(tasks))

        progress_vals = [float(t.progress_percentage) for t in tasks if t.progress_percentage is not None]
        avg_progress = sum(progress_vals) / len(progress_vals) if progress_vals else 0.0

        est_hours_vals = [float(t.estimated_hours) for t in tasks if t.estimated_hours is not None]
        avg_estimated_hours = sum(est_hours_vals) / len(est_hours_vals) if est_hours_vals else 0.0

        hours_logged_vals = [float(t.hours_logged) for t in tasks if t.hours_logged is not None]
        avg_hours_logged = sum(hours_logged_vals) / len(hours_logged_vals) if hours_logged_vals else 0.0

        alloc_score_vals = [float(t.allocation_score) for t in tasks if t.allocation_score is not None]
        avg_allocation_score = sum(alloc_score_vals) / len(alloc_score_vals) if alloc_score_vals else 0.0

        workload_vals = [float(e.workload_percentage) for e in employees if e.workload_percentage is not None]
        avg_workload = sum(workload_vals) / len(workload_vals) if workload_vals else 0.0

        exp_vals = [float(e.experience_years) for e in employees if e.experience_years is not None]
        avg_experience = sum(exp_vals) / len(exp_vals) if exp_vals else 0.0

        perf_vals = [float(e.performance_score) for e in employees if e.performance_score is not None]
        avg_performance = sum(perf_vals) / len(perf_vals) if perf_vals else 0.0

        feature_vector = [
            total_tasks,
            avg_progress,
            avg_estimated_hours,
            avg_hours_logged,
            avg_allocation_score,
            avg_workload,
            avg_experience,
            avg_performance,
        ]

        # 5. Load model via ml_services.py
        try:
            model = get_risk_model()
        except (MLModelError, Exception) as exc:
            return Response(
                {'error': f"Failed to load risk prediction model: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 6. Predict using XGBoost model
        try:
            import pandas as pd
            input_df = pd.DataFrame([feature_vector], columns=self.FEATURE_NAMES)
            raw_prediction = model.predict(input_df)[0]
        except Exception:
            import numpy as np
            arr = np.array([feature_vector])
            raw_prediction = model.predict(arr)[0]

        pred_idx = int(raw_prediction)
        risk_level = self.RISK_LEVEL_MAP.get(pred_idx, 'Unknown')

        return Response({
            'project_id': project.project_id,
            'risk_level': risk_level,
        }, status=status.HTTP_200_OK)


class ProjectDelayPredictionView(APIView):
    """
    POST /api/ml/delay-prediction/
    Predict if a project will be delayed ("Delayed" vs "Not Delayed")
    using trained RandomForestClassifier and 22 project-level features.
    """

    @staticmethod
    def _safe_float(val, default=0.0):
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not data.get('project_id') and request.query_params.get('project_id'):
            data['project_id'] = request.query_params.get('project_id')

        serializer = ProjectDelayPredictionRequestSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project_id = serializer.validated_data['project_id'].strip()

        # 1. Fetch project from database
        project = Project.objects.filter(project_id=project_id).first()
        if not project:
            return Response(
                {'error': f"Project with ID '{project_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Fetch project's tasks
        tasks = list(Task.objects.filter(project_id=project_id))
        if not tasks:
            return Response(
                {'error': f"Project '{project_id}' has no tasks to evaluate delay."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Fetch assigned employees
        assigned_employee_ids = {
            t.employee_id.strip()
            for t in tasks
            if t.employee_id and str(t.employee_id).strip()
        }
        if not assigned_employee_ids:
            return Response(
                {'error': f"Project '{project_id}' tasks have no assigned employees to evaluate delay."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employees = list(Employee.objects.filter(employee_id__in=assigned_employee_ids))
        if not employees:
            return Response(
                {'error': f"No employee records found for the assigned tasks in project '{project_id}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Calculate 19 raw project-level features
        total_tasks = float(len(tasks))

        progress_vals = [self._safe_float(t.progress_percentage) for t in tasks if t.progress_percentage is not None]
        avg_progress = sum(progress_vals) / len(progress_vals) if progress_vals else 0.0

        est_hours_vals = [self._safe_float(t.estimated_hours) for t in tasks if t.estimated_hours is not None]
        avg_estimated_hours = sum(est_hours_vals) / len(est_hours_vals) if est_hours_vals else 0.0
        total_estimated_hours = sum(est_hours_vals) if est_hours_vals else 0.0

        hours_logged_vals = [self._safe_float(t.hours_logged) for t in tasks if t.hours_logged is not None]
        avg_hours_logged = sum(hours_logged_vals) / len(hours_logged_vals) if hours_logged_vals else 0.0
        total_hours_logged = sum(hours_logged_vals) if hours_logged_vals else 0.0

        hours_efficiency = (total_hours_logged / total_estimated_hours) if total_estimated_hours > 0 else 0.0

        if project.start_date and project.deadline:
            try:
                project_duration_days = float(max(0, (project.deadline - project.start_date).days))
            except Exception:
                project_duration_days = 0.0
        else:
            project_duration_days = 0.0

        completed_task_count = float(sum(1 for t in tasks if (t.task_status or '').strip().lower() == 'completed'))
        in_progress_task_count = float(sum(1 for t in tasks if (t.task_status or '').strip().lower() == 'in progress'))
        on_hold_task_count = float(sum(1 for t in tasks if (t.task_status or '').strip().lower() == 'on hold'))
        not_started_task_count = float(sum(1 for t in tasks if (t.task_status or '').strip().lower() == 'not started'))
        cancelled_task_count = float(sum(1 for t in tasks if (t.task_status or '').strip().lower() == 'cancelled'))

        alloc_score_vals = [self._safe_float(t.allocation_score) for t in tasks if t.allocation_score is not None]
        avg_allocation_score = sum(alloc_score_vals) / len(alloc_score_vals) if alloc_score_vals else 0.0

        workload_vals = [self._safe_float(e.workload_percentage) for e in employees if e.workload_percentage is not None]
        avg_workload = sum(workload_vals) / len(workload_vals) if workload_vals else 0.0

        exp_vals = [self._safe_float(e.experience_years) for e in employees if e.experience_years is not None]
        avg_experience = sum(exp_vals) / len(exp_vals) if exp_vals else 0.0

        perf_vals = [self._safe_float(e.performance_score) for e in employees if e.performance_score is not None]
        avg_performance = sum(perf_vals) / len(perf_vals) if perf_vals else 0.0

        task_durations = []
        for t in tasks:
            if t.task_start_date and t.task_deadline:
                try:
                    task_durations.append(float(max(0, (t.task_deadline - t.task_start_date).days)))
                except Exception:
                    pass
        avg_task_duration_days = sum(task_durations) / len(task_durations) if task_durations else 0.0

        # 5. Determine risk_level using existing Risk Prediction logic/model
        risk_feature_vector = [
            total_tasks,
            avg_progress,
            avg_estimated_hours,
            avg_hours_logged,
            avg_allocation_score,
            avg_workload,
            avg_experience,
            avg_performance,
        ]

        try:
            risk_model = get_risk_model()
            import pandas as pd
            risk_input_df = pd.DataFrame([risk_feature_vector], columns=RiskPredictionView.FEATURE_NAMES)
            raw_risk_pred = risk_model.predict(risk_input_df)[0]
            risk_level = RiskPredictionView.RISK_LEVEL_MAP.get(int(raw_risk_pred), 'Low')
        except (MLModelError, Exception) as exc:
            return Response(
                {'error': f"Failed to determine risk level via risk model: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 6. One-hot encode risk_level into exactly the 4 binary indicators
        risk_level_Critical = 1.0 if risk_level == 'Critical' else 0.0
        risk_level_High = 1.0 if risk_level == 'High' else 0.0
        risk_level_Low = 1.0 if risk_level == 'Low' else 0.0
        risk_level_Medium = 1.0 if risk_level == 'Medium' else 0.0

        raw_feature_dict = {
            'total_tasks': total_tasks,
            'avg_progress': avg_progress,
            'avg_estimated_hours': avg_estimated_hours,
            'total_estimated_hours': total_estimated_hours,
            'avg_hours_logged': avg_hours_logged,
            'total_hours_logged': total_hours_logged,
            'hours_efficiency': hours_efficiency,
            'project_duration_days': project_duration_days,
            'completed_task_count': completed_task_count,
            'in_progress_task_count': in_progress_task_count,
            'on_hold_task_count': on_hold_task_count,
            'not_started_task_count': not_started_task_count,
            'cancelled_task_count': cancelled_task_count,
            'avg_allocation_score': avg_allocation_score,
            'avg_workload': avg_workload,
            'avg_experience': avg_experience,
            'avg_performance': avg_performance,
            'avg_task_duration_days': avg_task_duration_days,
            'risk_level_Critical': risk_level_Critical,
            'risk_level_High': risk_level_High,
            'risk_level_Low': risk_level_Low,
            'risk_level_Medium': risk_level_Medium,
        }

        # 7. Load project_delay_features.pkl and arrange the 22 features in exact training order
        try:
            delay_features = get_delay_feature_list()
            delay_model = get_delay_model()
        except (MLModelError, Exception) as exc:
            return Response(
                {'error': f"Failed to load delay prediction model or features: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        ordered_vector = [raw_feature_dict.get(col, 0.0) for col in delay_features]

        # 8. Pass the final 22-feature input to project_delay_random_forest.pkl
        try:
            delay_input_df = pd.DataFrame([ordered_vector], columns=delay_features)
            raw_delay_pred = delay_model.predict(delay_input_df)[0]
        except Exception:
            import numpy as np
            arr = np.array([ordered_vector])
            raw_delay_pred = delay_model.predict(arr)[0]

        # 9. Convert prediction: 1 -> "Delayed", 0 -> "Not Delayed"
        delay_prediction = "Delayed" if int(raw_delay_pred) == 1 else "Not Delayed"

        # 10. Return JSON
        return Response({
            'project_id': project.project_id,
            'delay_prediction': delay_prediction,
        }, status=status.HTTP_200_OK)




