import pandas as pd


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "C:/Users/nived/New folder (2)/AI-Business-Operations-Management-Platform/datasets/cleaned/Business_Operation_ml_ready.csv"

df = pd.read_csv(DATA_PATH)


# ============================================================
# 2. SELECT PROJECT MANAGEMENT FEATURES
# ============================================================

project_features = [
    "employee_id",
    "workload_percentage",
    "active_tasks",
    "estimated_hours",
    "hours_logged",
    "progress_percentage",
    "task_priority_Critical",
    "task_priority_High",
    "task_priority_Low",
    "task_priority_Medium",
    "task_priority_Unknown",
    "task_status_Blocked",
    "task_status_Completed",
    "task_status_In Progress",
    "task_status_Not Started",
    "task_status_Unknown"
]

project_df = df[project_features].copy()


# ============================================================
# 3. CONVERT PRIORITY
# ============================================================

def get_priority(row):

    if row["task_priority_Critical"]:
        return "Critical"

    elif row["task_priority_High"]:
        return "High"

    elif row["task_priority_Medium"]:
        return "Medium"

    elif row["task_priority_Low"]:
        return "Low"

    else:
        return "Unknown"


project_df["priority"] = project_df.apply(get_priority, axis=1)


# ============================================================
# 4. CONVERT STATUS
# ============================================================

def get_status(row):

    if row["task_status_Blocked"]:
        return "Blocked"

    elif row["task_status_Completed"]:
        return "Completed"

    elif row["task_status_In Progress"]:
        return "In Progress"

    elif row["task_status_Not Started"]:
        return "Not Started"

    else:
        return "Unknown"


project_df["status"] = project_df.apply(get_status, axis=1)


# ============================================================
# 5. EFFORT UTILIZATION
# ============================================================

project_df["effort_utilization"] = (
    project_df["hours_logged"] /
    project_df["estimated_hours"]
) * 100


# ============================================================
# 6. EFFORT RISK
# ============================================================

project_df["effort_utilization_capped"] = (
    project_df["effort_utilization"].clip(upper=150)
)

project_df["effort_risk"] = (
    project_df["effort_utilization_capped"] / 150
) * 100


# ============================================================
# 7. WORKLOAD RISK
# ============================================================

project_df["workload_risk"] = (
    project_df["workload_percentage"]
)


# ============================================================
# 8. ACTIVE TASK RISK
# ============================================================

project_df["active_tasks_risk"] = (
    project_df["active_tasks"] / 10
) * 100


# ============================================================
# 9. PRIORITY RISK
# ============================================================

priority_risk_map = {
    "Critical": 100,
    "High": 75,
    "Medium": 50,
    "Low": 25,
    "Unknown": 0
}

project_df["priority_risk"] = (
    project_df["priority"].map(priority_risk_map)
)


# ============================================================
# 10. STATUS RISK
# ============================================================

status_risk_map = {
    "Blocked": 100,
    "In Progress": 50,
    "Not Started": 40,
    "Completed": 0,
    "Unknown": 0
}

project_df["status_risk"] = (
    project_df["status"].map(status_risk_map)
)


# ============================================================
# 11. PROGRESS RISK
# ============================================================

project_df["effort_progress_gap"] = (
    project_df["effort_utilization"] -
    project_df["progress_percentage"]
)

project_df["progress_risk"] = (
    project_df["effort_progress_gap"]
    .clip(lower=0, upper=50)
    / 50
) * 100


# ============================================================
# 12. FINAL RISK SCORE
# ============================================================

project_df["risk_score"] = (
    0.25 * project_df["effort_risk"] +
    0.25 * project_df["progress_risk"] +
    0.20 * project_df["workload_risk"] +
    0.15 * project_df["priority_risk"] +
    0.10 * project_df["status_risk"] +
    0.05 * project_df["active_tasks_risk"]
)


# ============================================================
# 13. RISK LEVEL
# ============================================================

def get_risk_level(score):

    if score <= 30:
        return "Low"

    elif score <= 50:
        return "Medium"

    elif score <= 70:
        return "High"

    else:
        return "Critical"


project_df["risk_level"] = (
    project_df["risk_score"].apply(get_risk_level)
)


# ============================================================
# 14. IDENTIFY RISK FACTORS
# ============================================================

def get_risk_factors(row):

    factors = []

    if row["effort_risk"] >= 70:
        factors.append("High effort utilization")

    if row["progress_risk"] >= 50:
        factors.append("Effort is high compared with progress")

    if row["workload_risk"] >= 80:
        factors.append("High workload")

    if row["active_tasks_risk"] >= 70:
        factors.append("High number of active tasks")

    if row["priority"] == "Critical":
        factors.append("Critical priority")

    elif row["priority"] == "High":
        factors.append("High priority")

    if row["status"] == "Blocked":
        factors.append("Task is blocked")

    return factors


project_df["risk_factors"] = (
    project_df.apply(get_risk_factors, axis=1)
)


# ============================================================
# 15. ANALYZE ONE TASK
# ============================================================

def analyze_task(index):

    row = project_df.loc[index]

    result = {
        "employee_id": row["employee_id"],
        "priority": row["priority"],
        "status": row["status"],
        "progress": round(row["progress_percentage"], 2),
        "workload": round(row["workload_percentage"], 2),
        "effort_utilization": round(
            row["effort_utilization"], 2
        ),
        "risk_score": round(
            row["risk_score"], 2
        ),
        "risk_level": row["risk_level"],
        "risk_factors": row["risk_factors"]
    }

    return result


# ============================================================
# 16. TEST
# ============================================================

result = analyze_task(10561)

print("\n========== PROJECT MANAGEMENT RISK ANALYSIS ==========")

for key, value in result.items():
    print(f"{key}: {value}")