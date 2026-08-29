# Project Management Dataset — EDA Report

## 1. Data Overview

- **Total projects:** 10,000
- **Missing values:** 6,963
- **Duplicate records:** 0
- **Unique project managers:** 50
- **Duplicate project IDs:** 0

### Missing Values by Column

project_id                0
project_name              0
description               0
client_name               0
project_manager_id        0
department                0
start_date                0
planned_end_date          0
actual_end_date        6963
status                    0
priority                  0
progress_percentage       0
budget                    0
team_size                 0
created_date              0

## 2. Visualizations

The four required visualizations are:

1. Project Status Distribution
2. Project Priority Distribution
3. Projects by Start Month
4. Deadline Analysis (Overdue / Upcoming)

## 3. Deadline Analysis

Analysis date: **29-Aug-2026**

- **Overdue active projects:** 5,406
- **Upcoming active projects within 30 days:** 419

## 4. Initial Risk Analysis

A simple rule-based risk score was derived from:
- Deadline proximity/overdue status
- Project progress
- Priority
- Delayed/on-hold status

### Risk distribution

risk_level
Low         3143
Medium      3164
High        2993
Critical     700

This risk score is intended as an initial Project Management risk engine. It can later be connected to Task and Finance datasets for richer risk analysis.

## 5. Business Observations

1. The dataset contains 10,000 projects managed by 50 unique project managers, providing enough records for meaningful project-level analysis.
2. 'In Progress' is the most common project status, representing 54.6% of all projects.
3. High and Critical priority projects together account for 39.9% of projects, so a substantial share of the portfolio requires closer monitoring.
4. As of 29-Aug-2026, 5,406 active projects are past their planned end date and 419 active projects have deadlines within the next 30 days.
5. Using the initial rule-based risk engine (deadline + progress + priority + status), 3,693 projects are classified as High/Critical risk and should be prioritized for review.
