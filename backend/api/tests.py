from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .serializers import EmployeeSerializer, ProjectSerializer
from .views import EmployeeDetailView, EmployeeListCreateView, ProjectDetailView, ProjectListCreateView


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
