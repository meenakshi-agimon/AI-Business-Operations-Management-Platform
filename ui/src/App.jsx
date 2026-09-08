import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  Wallet,
  Brain,
  Settings,
  Bell,
  Search,
  ChevronDown,
} from "lucide-react";

import { fetchEmployees, fetchProjects, fetchRecommendations } from "./lib/api";

const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Projects", icon: FolderKanban },
  { name: "Employees", icon: Users },
  { name: "Finance", icon: Wallet },
  { name: "AI & Analytics", icon: Brain },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [employees, setEmployees] = useState([]);
  const [projects, setProjects] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchRecommendations = async (filters) => {
    setLoading(true);
    setError("");

    try {
      setRecommendations(await fetchRecommendations(filters));
    } catch (err) {
      setError(err.message || "Unable to calculate recommendations.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const loadData = async () => {
      if (!["Employees", "Projects", "AI & Analytics"].includes(activePage)) {
        return;
      }

      setLoading(true);
      setError("");

      try {
        const data =
          activePage === "Employees"
            ? await fetchEmployees()
            : activePage === "Projects"
              ? await fetchProjects()
              : await fetchRecommendations();

        if (!cancelled) {
          if (activePage === "Employees") {
            setEmployees(data);
          } else if (activePage === "Projects") {
            setProjects(data);
          } else {
            setRecommendations(data);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load data from the backend API.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      cancelled = true;
    };
  }, [activePage]);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">AI</div>

          <div>
            <h2>BusinessOps</h2>
            <span>Management Platform</span>
          </div>
        </div>

        <nav>
          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => setActivePage(item.name)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <Settings size={19} />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>{activePage}</h1>
            <p>AI Business Operations Management Platform</p>
          </div>

          <div className="topbar-actions">
            <div className="search">
              <Search size={18} />
              <input placeholder="Search..." />
            </div>

            <button className="icon-button">
              <Bell size={19} />
            </button>

            <div className="profile">
              <div className="avatar">RM</div>

              <div>
                <strong>Team RP2</strong>
                <span>Administrator</span>
              </div>

              <ChevronDown size={16} />
            </div>
          </div>
        </header>

        <section className="content">
          <div className="panel" style={{ marginBottom: "1rem" }}>
            <div className="panel-header">
              <div>
                <h3>Backend API Mode</h3>
                <p>Employee and Project data is fetched through the Django API</p>
              </div>
            </div>
            <p style={{ margin: 0, color: "#1f2937" }}>
              Frontend tables for Employees and Projects are intentionally not queried directly from Supabase.
            </p>
          </div>

          {activePage === "Dashboard" && <Dashboard />}

          {activePage === "Projects" && (
            <ProjectTable projects={projects} loading={loading} error={error} />
          )}

          {activePage === "Employees" && (
            <EmployeeTable employees={employees} loading={loading} error={error} />
          )}

          {activePage === "Finance" && (
            <Placeholder title="Finance Management" />
          )}

          {activePage === "AI & Analytics" && (
            <RecommendationTable
              recommendations={recommendations}
              loading={loading}
              error={error}
              onSearch={searchRecommendations}
            />
          )}
        </section>
      </main>
    </div>
  );
}

function Dashboard() {
  return (
    <>
      <div className="welcome">
        <div>
          <h2>Good morning, Team RP2</h2>
          <p>Here's an overview of the business operations dataset.</p>
        </div>

        <button className="primary-button">View Reports</button>
      </div>

      <div className="stats-grid">
        <StatCard title="Total Employees" value="4,999" change="Dataset" />
        <StatCard title="Total Tasks" value="50,000" change="Dataset" />
        <StatCard title="Avg. Workload" value="55.66%" change="Dataset" />
        <StatCard title="Avg. Performance" value="69.71%" change="Dataset" />
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Task Progress</h3>
              <p>Current task status from dataset</p>
            </div>
            <span className="badge">Dataset</span>
          </div>

          <div className="progress-item">
            <div>
              <span>Average Task Progress</span>
              <strong>78.72%</strong>
            </div>
            <div className="progress"><div style={{ width: "78.72%" }} /></div>
          </div>

          <div className="progress-item">
            <div>
              <span>Completed Tasks</span>
              <strong>17,225</strong>
            </div>
            <div className="progress"><div style={{ width: "68.9%" }} /></div>
          </div>

          <div className="progress-item">
            <div>
              <span>In Progress Tasks</span>
              <strong>23,437</strong>
            </div>
            <div className="progress"><div style={{ width: "46.9%" }} /></div>
          </div>

          <div className="progress-item">
            <div>
              <span>Blocked Tasks</span>
              <strong>2,950</strong>
            </div>
            <div className="progress"><div style={{ width: "5.9%" }} /></div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Dataset Insights</h3>
              <p>Current operational indicators</p>
            </div>
            <Brain size={20} />
          </div>

          <div className="insight">
            <div className="insight-dot" />
            <div>
              <strong>Employee Availability</strong>
              <p>3,233 employees are currently available.</p>
            </div>
          </div>

          <div className="insight">
            <div className="insight-dot" />
            <div>
              <strong>Employee Workload</strong>
              <p>Average employee workload is 55.66%.</p>
            </div>
          </div>

          <div className="insight">
            <div className="insight-dot" />
            <div>
              <strong>Task Progress</strong>
              <p>Average task progress is 78.72%.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Employee Availability</h3>
            <p>Unique employee availability status</p>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Employees</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span className="status success">Available</span></td>
              <td>3,233</td>
              <td>64.67%</td>
            </tr>
            <tr>
              <td><span className="status pending">Busy</span></td>
              <td>1,398</td>
              <td>27.97%</td>
            </tr>
            <tr>
              <td>On Leave</td>
              <td>279</td>
              <td>5.58%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Task Status Overview</h3>
            <p>Task distribution from the business operations dataset</p>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Task Status</th>
              <th>Number of Tasks</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>In Progress</td>
              <td>23,437</td>
            </tr>
            <tr>
              <td>Completed</td>
              <td>17,225</td>
            </tr>
            <tr>
              <td>Not Started</td>
              <td>6,033</td>
            </tr>
            <tr>
              <td>Blocked</td>
              <td>2,950</td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}

function EmployeeTable({ employees, loading, error }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h3>Employee Management</h3>
          <p>Live data from the Django backend API</p>
        </div>
      </div>

      {loading && <p>Loading employees...</p>}
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Name</th>
              <th>Department</th>
              <th>Role</th>
              <th>Availability</th>
              <th>Workload</th>
            </tr>
          </thead>
          <tbody>
            {employees.length === 0 ? (
              <tr>
                <td colSpan="6">No employee records found.</td>
              </tr>
            ) : (
              employees.map((employee) => (
                <tr key={employee.employee_id || employee.email}>
                  <td>{employee.employee_id}</td>
                  <td>{employee.employee_name}</td>
                  <td>{employee.department}</td>
                  <td>{employee.job_role}</td>
                  <td>{employee.availability_status}</td>
                  <td>{employee.workload_percentage}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

function ProjectTable({ projects, loading, error }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h3>Project Management</h3>
          <p>Live data from the Django backend API</p>
        </div>
      </div>

      {loading && <p>Loading projects...</p>}
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Project ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Risk</th>
              <th>Start Date</th>
              <th>Deadline</th>
            </tr>
          </thead>
          <tbody>
            {projects.length === 0 ? (
              <tr>
                <td colSpan="6">No project records found.</td>
              </tr>
            ) : (
              projects.map((project) => (
                <tr key={project.project_id || project.project_name}>
                  <td>{project.project_id}</td>
                  <td>{project.project_name}</td>
                  <td>{project.status}</td>
                  <td>{project.risk_level}</td>
                  <td>{project.start_date}</td>
                  <td>{project.deadline}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

function RecommendationTable({ recommendations, loading, error, onSearch }) {
  const [requiredSkill, setRequiredSkill] = useState("");
  const [department, setDepartment] = useState("");
  const [priority, setPriority] = useState("");

  const submitTask = (event) => {
    event.preventDefault();
    onSearch({ requiredSkill, department, priority, topN: 5 });
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h3>Recommended Employees</h3>
          <p>Top candidates ranked by the employee recommendation model</p>
        </div>
        <span className="badge">AI Model</span>
      </div>

      <form className="recommendation-form" onSubmit={submitTask}>
        <label>
          Required skill
          <select value={requiredSkill} onChange={(event) => setRequiredSkill(event.target.value)}>
            <option value="">Any skill</option>
            <option value="Python">Python</option>
            <option value="Django">Django</option>
            <option value="SQL">SQL</option>
            <option value="React">React</option>
            <option value="Machine Learning">Machine Learning</option>
          </select>
        </label>
        <label>
          Department
          <select value={department} onChange={(event) => setDepartment(event.target.value)}>
            <option value="">Any department</option>
            <option value="Engineering">Engineering</option>
            <option value="Data Science">Data Science</option>
            <option value="IT">IT</option>
            <option value="Finance">Finance</option>
            <option value="Operations">Operations</option>
          </select>
        </label>
        <label>
          Priority
          <select value={priority} onChange={(event) => setPriority(event.target.value)}>
            <option value="">Any priority</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>
        <button className="primary-button" type="submit">Recommend</button>
      </form>

      {loading && <p>Calculating recommendations...</p>}
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Employee ID</th>
              <th>Recommendation</th>
              <th>Probability</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.length === 0 ? (
              <tr><td colSpan="4">No employees match these task requirements.</td></tr>
            ) : recommendations.map((recommendation, index) => (
              <tr key={recommendation.employee_id}>
                <td>{index + 1}</td>
                <td>{recommendation.employee_id}</td>
                <td>
                  <span className={`status ${recommendation.recommended ? "success" : "pending"}`}>
                    {recommendation.recommended ? "Recommended" : "Not recommended"}
                  </span>
                </td>
                <td>{(recommendation.probability * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function StatCard({ title, value, change }) {
  return (
    <div className="stat-card">
      <span>{title}</span>
      <div className="stat-value">{value}</div>
      <small>{change}</small>
    </div>
  );
}

function Placeholder({ title }) {
  return (
    <div className="placeholder">
      <h2>{title}</h2>
      <p>This module will be connected to the team backend during the integration phase.</p>
    </div>
  );
}

export default App;