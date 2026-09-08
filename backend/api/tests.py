from django.test import SimpleTestCase
from django.urls import resolve, reverse
import pandas as pd

from .recommendation import recommend_employees, recommend_for_task
from .serializers import EmployeeSerializer, ProjectSerializer
from .views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    ProjectDetailView,
    ProjectListCreateView,
    RecommendationListView,
)


class RecommendationModel:
    feature_names_in_ = ['feature_a', 'feature_b']
    classes_ = [0, 1]

    def predict(self, data):
        return [1, 0][:len(data)]

    def predict_proba(self, data):
        return [[0.1, 0.9], [0.8, 0.2]][:len(data)]


class EmployeeProjectApiRouteTests(SimpleTestCase):
    def test_employee_urls_resolve(self):
        self.assertEqual(resolve('/api/employees/').func.view_class, EmployeeListCreateView)
        self.assertEqual(resolve('/api/employees/E001/').func.view_class, EmployeeDetailView)

    def test_project_urls_resolve(self):
        self.assertEqual(resolve('/api/projects/').func.view_class, ProjectListCreateView)
        self.assertEqual(resolve('/api/projects/P001/').func.view_class, ProjectDetailView)

    def test_recommendation_url_resolves(self):
        self.assertEqual(resolve('/api/recommendations/').func.view_class, RecommendationListView)

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

    def test_recommendation_results_are_ranked_by_probability(self):
        data = pd.DataFrame([
            {'employee_id': 'E001', 'feature_a': 1, 'feature_b': 2},
            {'employee_id': 'E002', 'feature_a': 3, 'feature_b': 4},
        ])

        result = recommend_employees(data, top_n=2, model=RecommendationModel())

        self.assertEqual(result['employee_id'].tolist(), ['E001', 'E002'])
        self.assertEqual(result['probability'].tolist(), [0.9, 0.2])

    def test_recommendation_rejects_missing_features(self):
        data = pd.DataFrame([{'employee_id': 'E001', 'feature_a': 1}])

        with self.assertRaisesMessage(ValueError, 'missing model features: feature_b'):
            recommend_employees(data, model=RecommendationModel())

    def test_recommendation_filters_candidates_for_task(self):
        data = pd.DataFrame([
            {'employee_id': 'E001', 'feature_a': 1, 'feature_b': 2, 'required_skill_Python': 1},
            {'employee_id': 'E002', 'feature_a': 3, 'feature_b': 4, 'required_skill_Python': 0},
        ])
        model = RecommendationModel()

        result = recommend_for_task(
            data,
            {'required_skill': 'Python'},
            top_n=2,
            model=model,
        )

        self.assertEqual(result['employee_id'].tolist(), ['E001'])
