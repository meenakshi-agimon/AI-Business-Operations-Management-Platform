from unittest.mock import MagicMock, patch
from django.test import SimpleTestCase
from django.urls import resolve, reverse
from rest_framework.test import APIRequestFactory

from .models import Employee, Project
from .serializers import (
    EmployeeSerializer,
    FinanceSerializer,
    ProjectSerializer,
    RecommendEmployeeRequestSerializer,
    TaskSerializer,
)
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


class EmployeeProjectApiRouteTests(SimpleTestCase):
    def test_employee_urls_resolve(self):
        self.assertEqual(resolve('/api/employees/').func.view_class, EmployeeListCreateView)
        self.assertEqual(resolve('/api/employees/E001/').func.view_class, EmployeeDetailView)

    def test_project_urls_resolve(self):
        self.assertEqual(resolve('/api/projects/').func.view_class, ProjectListCreateView)
        self.assertEqual(resolve('/api/projects/P001/').func.view_class, ProjectDetailView)

    def test_employee_serializer_valid(self):
        payload = {
            'employee_id': 'E001',
            'employee_name': 'Akhilesh P. S',
            'email': 'akhilesh@example.com',
            'department': 'Engineering',
            'job_role': 'Developer',
            'experience_years': '3.5',
            'hire_date': '2024-01-15',
            'skills': 'Python, Django',
            'availability_status': 'Available',
            'workload_percentage': '35.50',
            'active_tasks': 2,
            'performance_score': '88.25',
        }
        serializer = EmployeeSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_project_serializer_valid(self):
        payload = {
            'project_id': 'P001',
            'project_name': 'Business Operations Portal',
            'description': 'Operations dashboard',
            'start_date': '2025-01-01',
            'deadline': '2025-12-31',
            'status': 'In Progress',
            'risk_level': 'Low',
        }
        serializer = ProjectSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_api_routes_names(self):
        self.assertEqual(reverse('employee-list-create'), '/api/employees/')
        self.assertEqual(reverse('employee-detail', kwargs={'employee_id': 'E001'}), '/api/employees/E001/')
        self.assertEqual(reverse('project-list-create'), '/api/projects/')
        self.assertEqual(reverse('project-detail', kwargs={'project_id': 'P001'}), '/api/projects/P001/')


class TaskApiRouteTests(SimpleTestCase):
    def test_task_urls_resolve(self):
        self.assertEqual(resolve('/api/tasks/').func.view_class, TaskListCreateView)
        self.assertEqual(resolve('/api/tasks/TSK001/').func.view_class, TaskDetailView)

    def test_task_api_routes_names(self):
        self.assertEqual(reverse('task-list-create'), '/api/tasks/')
        self.assertEqual(reverse('task-detail', kwargs={'task_id': 'TSK001'}), '/api/tasks/TSK001/')

    @patch('api.models.Project.objects.filter')
    @patch('api.models.Employee.objects.filter')
    def test_task_serializer_valid(self, mock_emp_filter, mock_proj_filter):
        mock_proj_filter.return_value.exists.return_value = True
        mock_emp_filter.return_value.exists.return_value = True
        payload = {
            'task_id': 'TSK001',
            'project_id': 'P001',
            'employee_id': 'E001',
            'task_title': 'Build Authentication Module',
            'task_description': 'Implement JWT auth and user sessions',
            'task_priority': 'High',
            'task_status': 'In Progress',
            'task_start_date': '2026-01-10',
            'task_deadline': '2026-02-15',
            'required_skill': 'Python',
            'estimated_hours': '40.00',
            'hours_logged': '15.50',
            'progress_percentage': '38.75',
            'allocation_score': '85.50',
            'recommended_employee': True,
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['task_title'], 'Build Authentication Module')
        self.assertEqual(serializer.validated_data['task_priority'], 'High')

    def test_task_serializer_optional_fields(self):
        payload = {
            'task_title': 'Setup DB indexes',
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch('api.models.Project.objects.filter')
    @patch('api.models.Employee.objects.filter')
    def test_task_serializer_invalid_foreign_keys(self, mock_emp_filter, mock_proj_filter):
        mock_proj_filter.return_value.exists.return_value = False
        mock_emp_filter.return_value.exists.return_value = False
        payload = {
            'task_id': 'TSK001',
            'project_id': 'NONEXISTENT_P',
            'employee_id': 'NONEXISTENT_E',
            'task_title': 'Build Authentication Module',
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project_id', serializer.errors)
        self.assertIn('employee_id', serializer.errors)

    def test_task_serializer_blank_foreign_keys_converted_to_none(self):
        payload = {
            'task_title': 'Task with blank FKs',
            'project_id': '   ',
            'employee_id': '',
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data['project_id'])
        self.assertIsNone(serializer.validated_data['employee_id'])


class FinanceApiRouteTests(SimpleTestCase):
    def test_finance_urls_resolve(self):
        self.assertEqual(resolve('/api/finance/').func.view_class, FinanceListCreateView)
        self.assertEqual(resolve('/api/finance/FIN001/').func.view_class, FinanceDetailView)

    def test_finance_api_routes_names(self):
        self.assertEqual(reverse('finance-list-create'), '/api/finance/')
        self.assertEqual(reverse('finance-detail', kwargs={'finance_id': 'FIN001'}), '/api/finance/FIN001/')

    @patch('api.models.Project.objects.filter')
    def test_finance_serializer_valid(self, mock_proj_filter):
        mock_proj_filter.return_value.exists.return_value = True
        payload = {
            'finance_id': 'FIN001',
            'project_id': 'P001',
            'expense_type': 'Cloud Infrastructure',
            'amount': '1250.75',
            'expense_date': '2026-02-01',
            'approval_status': 'Approved',
            'approved_by': 'Finance Director',
            'is_anomaly': False,
        }
        serializer = FinanceSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['expense_type'], 'Cloud Infrastructure')
        self.assertEqual(serializer.validated_data['approval_status'], 'Approved')

    def test_finance_serializer_optional_fields(self):
        payload = {
            'amount': '500.00',
            'expense_type': 'Software License',
        }
        serializer = FinanceSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch('api.models.Project.objects.filter')
    def test_finance_serializer_invalid_project_id(self, mock_proj_filter):
        mock_proj_filter.return_value.exists.return_value = False
        payload = {
            'finance_id': 'FIN001',
            'project_id': 'NONEXISTENT_P',
            'expense_type': 'Cloud Infrastructure',
        }
        serializer = FinanceSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project_id', serializer.errors)

    def test_finance_serializer_blank_project_id_converted_to_none(self):
        payload = {
            'expense_type': 'Operations',
            'amount': '250.00',
            'project_id': '  ',
        }
        serializer = FinanceSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data['project_id'])


class RecommendEmployeeApiTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_recommend_employee_url_resolves(self):
        self.assertEqual(resolve('/api/recommend-employee/').func.view_class, RecommendEmployeeView)

    def test_recommend_employee_route_name(self):
        self.assertEqual(reverse('recommend-employee'), '/api/recommend-employee/')

    def test_recommend_employee_serializer_valid(self):
        payload = {
            'required_skill': 'Python',
            'task_priority': 'High',
            'estimated_hours': '50.00',
            'top_n': 3,
        }
        serializer = RecommendEmployeeRequestSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['required_skill'], 'Python')
        self.assertEqual(serializer.validated_data['top_n'], 3)

    def test_recommend_employee_serializer_defaults(self):
        payload = {}
        serializer = RecommendEmployeeRequestSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data.get('top_n'), 5)
        self.assertEqual(serializer.validated_data.get('task_priority'), 'Medium')

    def test_recommend_employee_post_request(self):
        view = RecommendEmployeeView.as_view()
        request = self.factory.post(
            '/api/recommend-employee/',
            {'required_skill': 'Machine Learning', 'task_priority': 'Critical', 'estimated_hours': 60.0, 'top_n': 2},
            format='json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('task_criteria', response.data)
        self.assertIn('recommendations', response.data)
        self.assertEqual(response.data['task_criteria']['required_skill'], 'Machine Learning')

    def test_recommend_employee_get_request(self):
        view = RecommendEmployeeView.as_view()
        request = self.factory.get('/api/recommend-employee/?required_skill=Django&top_n=3')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('recommendations', response.data)

    def test_recommendation_scoring_logic(self):
        view = RecommendEmployeeView()
        emp1 = Employee(
            employee_id='EMP001',
            employee_name='Alice Smith',
            skills='Python, Django, PostgreSQL',
            availability_status='Available',
            workload_percentage=20.0,
            active_tasks=1,
            performance_score=95.0,
            experience_years=5.0,
        )
        emp2 = Employee(
            employee_id='EMP002',
            employee_name='Bob Jones',
            skills='Java, Spring Boot',
            availability_status='On Leave',
            workload_percentage=80.0,
            active_tasks=5,
            performance_score=60.0,
            experience_years=1.0,
        )

        from unittest.mock import patch
        with patch('api.models.Employee.objects.all', return_value=[emp1, emp2]):
            recs, total = view.get_recommendations(required_skill='Python', top_n=5)
            self.assertEqual(total, 2)
            self.assertEqual(len(recs), 2)
            self.assertEqual(recs[0]['employee_id'], 'EMP001')
            self.assertTrue(recs[0]['recommended'])
            self.assertGreater(recs[0]['match_score'], recs[1]['match_score'])
            self.assertFalse(recs[1]['recommended'])

    def test_recommend_employee_invalid_top_n(self):
        view = RecommendEmployeeView.as_view()
        request = self.factory.post(
            '/api/recommend-employee/',
            {'top_n': 0},
            format='json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_recommend_employee_empty_candidate_pool(self):
        view = RecommendEmployeeView()
        from unittest.mock import patch
        with patch('api.models.Employee.objects.all', return_value=[]):
            recs, total = view.get_recommendations(required_skill='Python')
            self.assertEqual(total, 0)
            self.assertEqual(recs, [])

    def test_recommend_employee_with_task_id_lookup(self):
        from .models import Task
        view = RecommendEmployeeView()
        mock_task = Task(
            task_id='TSK999',
            required_skill='React',
            task_priority='High',
            estimated_hours=30.0,
        )
        emp1 = Employee(
            employee_id='EMP003',
            employee_name='Charlie Brown',
            skills='React, TypeScript',
            availability_status='Available',
            workload_percentage=10.0,
            active_tasks=1,
            performance_score=90.0,
            experience_years=4.0,
        )
        from unittest.mock import MagicMock, patch
        mock_qs = MagicMock()
        mock_qs.first.return_value = mock_task
        with patch('api.models.Task.objects.filter', return_value=mock_qs), \
             patch('api.models.Employee.objects.all', return_value=[emp1]):
            recs, total = view.get_recommendations(task_id='TSK999')
            self.assertEqual(total, 1)
            self.assertEqual(recs[0]['employee_id'], 'EMP003')
            self.assertTrue(recs[0]['recommended'])


class ModelStringAndValidationTests(SimpleTestCase):
    def test_task_str_representation(self):
        from .models import Task
        task1 = Task(task_id='TSK001', task_title='API Integration')
        self.assertEqual(str(task1), 'API Integration')

        task2 = Task(task_id='TSK002', task_title='')
        self.assertEqual(str(task2), 'TSK002')

    def test_finance_str_representation(self):
        from .models import Finance
        finance = Finance(finance_id='FIN001', expense_type='Cloud Storage')
        self.assertEqual(str(finance), 'FIN001 - Cloud Storage')

    def test_task_serializer_invalid_decimal(self):
        payload = {
            'task_title': 'Task with bad estimate',
            'estimated_hours': 'not-a-number',
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('estimated_hours', serializer.errors)

    def test_finance_serializer_invalid_amount(self):
        payload = {
            'expense_type': 'Operations',
            'amount': 'invalid-amount',
        }
        serializer = FinanceSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
