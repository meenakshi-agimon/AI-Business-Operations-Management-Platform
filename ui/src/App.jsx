import { useState } from "react";
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

const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Projects", icon: FolderKanban },
  { name: "Employees", icon: Users },
  { name: "Finance", icon: Wallet },
  { name: "AI & Analytics", icon: Brain },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

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
          {activePage === "Dashboard" && <Dashboard />}

          {activePage === "Projects" && (
            <Placeholder title="Project Management" />
          )}

          {activePage === "Employees" && (
            <Placeholder title="Employee Management" />
          )}

          {activePage === "Finance" && (
            <Placeholder title="Finance Management" />
          )}

          {activePage === "AI & Analytics" && (
            <Placeholder title="AI & Analytics" />
          )}
        </section>
      </main>
    </div>
  );
}

function Dashboard() {
  return (
    <>
      {/* Welcome Section */}
      <div className="welcome">
        <div>
          <h2>Good morning, Team RP2</h2>
          <p>
            Here's an overview of the business operations dataset.
          </p>
        </div>

        <button className="primary-button">
          View Reports
        </button>
      </div>

      {/* Dataset Statistics */}
      <div className="stats-grid">
        <StatCard
          title="Total Employees"
          value="4,999"
          change="Dataset"
        />

        <StatCard
          title="Total Tasks"
          value="50,000"
          change="Dataset"
        />

        <StatCard
          title="Avg. Workload"
          value="55.66%"
          change="Dataset"
        />

        <StatCard
          title="Avg. Performance"
          value="69.71%"
          change="Dataset"
        />
      </div>

      {/* Dashboard Panels */}
      <div className="dashboard-grid">

        {/* Task Progress */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Task Progress</h3>
              <p>Current task status from dataset</p>
            </div>

            <span className="badge">
              Dataset
            </span>
          </div>

          <div className="progress-item">
            <div>
              <span>Average Task Progress</span>
              <strong>78.72%</strong>
            </div>

            <div className="progress">
              <div style={{ width: "78.72%" }} />
            </div>
          </div>

          <div className="progress-item">
            <div>
              <span>Completed Tasks</span>
              <strong>17,225</strong>
            </div>

            <div className="progress">
              <div style={{ width: "68.9%" }} />
            </div>
          </div>

          <div className="progress-item">
            <div>
              <span>In Progress Tasks</span>
              <strong>23,437</strong>
            </div>

            <div className="progress">
              <div style={{ width: "46.9%" }} />
            </div>
          </div>

          <div className="progress-item">
            <div>
              <span>Blocked Tasks</span>
              <strong>2,950</strong>
            </div>

            <div className="progress">
              <div style={{ width: "5.9%" }} />
            </div>
          </div>
        </div>

        {/* Dataset Insights */}
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

              <p>
                3,233 employees are currently available.
              </p>
            </div>
          </div>

          <div className="insight">
            <div className="insight-dot" />

            <div>
              <strong>Employee Workload</strong>

              <p>
                Average employee workload is 55.66%.
              </p>
            </div>
          </div>

          <div className="insight">
            <div className="insight-dot" />

            <div>
              <strong>Task Progress</strong>

              <p>
                Average task progress is 78.72%.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Employee Availability */}
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
              <td>
                <span className="status success">
                  Available
                </span>
              </td>

              <td>3,233</td>

              <td>64.67%</td>
            </tr>

            <tr>
              <td>
                <span className="status pending">
                  Busy
                </span>
              </td>

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

      {/* Task Status */}
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

function StatCard({ title, value, change }) {
  return (
    <div className="stat-card">
      <span>{title}</span>

      <div className="stat-value">
        {value}
      </div>

      <small>
        {change}
      </small>
    </div>
  );
}

function Placeholder({ title }) {
  return (
    <div className="placeholder">
      <h2>{title}</h2>

      <p>
        This module will be connected to the team backend
        during the integration phase.
      </p>
    </div>
  );
}

export default App;