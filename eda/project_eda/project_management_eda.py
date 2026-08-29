import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("datasets/raw/project_dataset.csv")

# Date conversion
for col in ["start_date", "planned_end_date", "actual_end_date", "created_date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

print("Total projects:", len(df))
print("\nMissing values:\n", df.isna().sum())
print("\nDuplicate records:", df.duplicated().sum())
print("Unique project managers:", df["project_manager_id"].nunique())

# Status distribution
df["status"].value_counts().plot(kind="bar")
plt.title("Project Status Distribution")
plt.xlabel("Project Status")
plt.ylabel("Number of Projects")
plt.tight_layout()
plt.show()

# Priority distribution
df["priority"].value_counts().reindex(
    ["Low", "Medium", "High", "Critical"], fill_value=0
).plot(kind="bar")
plt.title("Project Priority Distribution")
plt.xlabel("Priority")
plt.ylabel("Number of Projects")
plt.tight_layout()
plt.show()

# Projects by month
monthly = df.set_index("start_date").resample("MS").size()
monthly.plot(kind="line", marker="o")
plt.title("Projects by Start Month")
plt.xlabel("Start Month")
plt.ylabel("Number of Projects")
plt.tight_layout()
plt.show()

# Deadline analysis
analysis_date = pd.Timestamp("2026-08-29")
active = df["status"].isin(["Planning", "In Progress", "On Hold", "Delayed"])
overdue = active & (df["planned_end_date"] < analysis_date)
upcoming = active & (df["planned_end_date"] >= analysis_date) & (
    df["planned_end_date"] <= analysis_date + pd.Timedelta(days=30)
)

deadline = pd.Series({
    "Overdue": overdue.sum(),
    "Upcoming (30 days)": upcoming.sum(),
    "Not overdue / >30 days": (active & ~overdue & ~upcoming).sum()
})
deadline.plot(kind="bar")
plt.title("Deadline Analysis")
plt.xlabel("Deadline Category")
plt.ylabel("Number of Projects")
plt.tight_layout()
plt.show()
