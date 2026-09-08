const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorData}`);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  return response.text();
}

export async function fetchEmployees() {
  return apiRequest('/employees/');
}

export async function createEmployee(payload) {
  return apiRequest('/employees/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchProjects() {
  return apiRequest('/projects/');
}

export async function fetchRecommendations({ topN = 5, requiredSkill = '', department = '', priority = '' } = {}) {
  const params = new URLSearchParams({ top_n: topN });

  if (requiredSkill) params.set('required_skill', requiredSkill);
  if (department) params.set('department', department);
  if (priority) params.set('task_priority', priority);

  return apiRequest(`/recommendations/?${params.toString()}`);
}

export async function createProject(payload) {
  return apiRequest('/projects/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
