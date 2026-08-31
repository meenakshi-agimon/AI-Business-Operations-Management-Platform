/*
============================================================
AI BUSINESS OPERATIONS MANAGEMENT PLATFORM
DATABASE IMPORT & VALIDATION
============================================================

Author  : Rajesh Mani
Database: ai_ops_platform

Purpose:
1. Verify database and tables
2. Verify record counts
3. Verify primary-key integrity
4. Verify foreign-key relationships
5. Perform basic data-quality checks
6. Run basic relational JOIN queries

Expected Records:
Employees : 4,999
Projects  : 10,000
Tasks     : 500
Finance   : 1,000

Total : 16,499

IMPORTANT:
This script is READ-ONLY.
It does NOT INSERT, UPDATE, DELETE, ALTER, or DROP data.
============================================================
*/


-- ============================================================
-- 1. SELECT DATABASE
-- ============================================================

USE ai_ops_platform;


-- ============================================================
-- 2. VERIFY TABLES
-- ============================================================

SHOW TABLES;


-- ============================================================
-- 3. VERIFY TABLE STRUCTURES
-- ============================================================

DESCRIBE Employees;

DESCRIBE Projects;

DESCRIBE Tasks;

DESCRIBE Finance;


-- ============================================================
-- 4. RECORD COUNT VALIDATION
-- ============================================================

SELECT
    'Employees' AS table_name,
    COUNT(*) AS record_count
FROM Employees

UNION ALL

SELECT
    'Projects',
    COUNT(*)
FROM Projects

UNION ALL

SELECT
    'Tasks',
    COUNT(*)
FROM Tasks

UNION ALL

SELECT
    'Finance',
    COUNT(*)
FROM Finance;


-- ============================================================
-- 5. TOTAL RECORD COUNT
-- ============================================================

SELECT
    (
        (SELECT COUNT(*) FROM Employees) +
        (SELECT COUNT(*) FROM Projects) +
        (SELECT COUNT(*) FROM Tasks) +
        (SELECT COUNT(*) FROM Finance)
    ) AS total_records;


-- ============================================================
-- 6. PRIMARY KEY VALIDATION
-- Checks:
--   - Total records
--   - Unique IDs
--   - NULL IDs
-- ============================================================

SELECT
    'Employees' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT employee_id) AS unique_ids,
    SUM(employee_id IS NULL) AS null_ids
FROM Employees

UNION ALL

SELECT
    'Projects',
    COUNT(*),
    COUNT(DISTINCT project_id),
    SUM(project_id IS NULL)
FROM Projects

UNION ALL

SELECT
    'Tasks',
    COUNT(*),
    COUNT(DISTINCT task_id),
    SUM(task_id IS NULL)
FROM Tasks

UNION ALL

SELECT
    'Finance',
    COUNT(*),
    COUNT(DISTINCT finance_id),
    SUM(finance_id IS NULL)
FROM Finance;


-- ============================================================
-- 7. FOREIGN KEY VALIDATION
-- Tasks → Projects
-- Expected invalid references: 0
-- ============================================================

SELECT
    COUNT(*) AS invalid_task_project_references
FROM Tasks t
LEFT JOIN Projects p
    ON t.project_id = p.project_id
WHERE p.project_id IS NULL;


-- ============================================================
-- 8. FOREIGN KEY VALIDATION
-- Tasks → Employees
-- Expected invalid references: 0
-- ============================================================

SELECT
    COUNT(*) AS invalid_task_employee_references
FROM Tasks t
LEFT JOIN Employees e
    ON t.employee_id = e.employee_id
WHERE e.employee_id IS NULL;


-- ============================================================
-- 9. FOREIGN KEY VALIDATION
-- Finance → Projects
-- Expected invalid references: 0
-- ============================================================

SELECT
    COUNT(*) AS invalid_finance_project_references
FROM Finance f
LEFT JOIN Projects p
    ON f.project_id = p.project_id
WHERE f.project_id IS NOT NULL
  AND p.project_id IS NULL;


-- ============================================================
-- 10. DATA QUALITY CHECK
-- Employee workload must be between 0 and 100
-- ============================================================

SELECT
    COUNT(*) AS invalid_employee_workload
FROM Employees
WHERE workload_percentage < 0
   OR workload_percentage > 100;


-- ============================================================
-- 11. DATA QUALITY CHECK
-- Employee performance must be between 0 and 100
-- ============================================================

SELECT
    COUNT(*) AS invalid_employee_performance
FROM Employees
WHERE performance_score < 0
   OR performance_score > 100;


-- ============================================================
-- 12. DATA QUALITY CHECK
-- Task progress must be between 0 and 100
-- ============================================================

SELECT
    COUNT(*) AS invalid_task_progress
FROM Tasks
WHERE progress_percentage < 0
   OR progress_percentage > 100;


-- ============================================================
-- 13. DATA QUALITY CHECK
-- Task hours cannot be negative
-- ============================================================

SELECT
    COUNT(*) AS negative_task_hours
FROM Tasks
WHERE estimated_hours < 0
   OR hours_logged < 0;


-- ============================================================
-- 14. DATA QUALITY CHECK
-- Finance amounts cannot be negative
-- ============================================================

SELECT
    COUNT(*) AS negative_finance_amounts
FROM Finance
WHERE amount < 0;


-- ============================================================
-- 15. BASIC RELATIONAL JOIN
-- Task → Project → Employee
-- ============================================================

SELECT
    t.task_id,
    t.task_title,
    t.project_id,
    p.project_name,
    t.employee_id,
    e.employee_name,
    t.task_status,
    t.progress_percentage
FROM Tasks t
LEFT JOIN Projects p
    ON t.project_id = p.project_id
LEFT JOIN Employees e
    ON t.employee_id = e.employee_id
LIMIT 10;


-- ============================================================
-- 16. BASIC FINANCE QUERY
-- Expense summary by type
-- ============================================================

SELECT
    expense_type,
    COUNT(*) AS expense_count,
    SUM(amount) AS total_amount
FROM Finance
GROUP BY expense_type
ORDER BY total_amount DESC;


-- ============================================================
-- 17. FINAL DATABASE SUMMARY
-- ============================================================

SELECT
    (SELECT COUNT(*) FROM Employees) AS employees,
    (SELECT COUNT(*) FROM Projects) AS projects,
    (SELECT COUNT(*) FROM Tasks) AS tasks,
    (SELECT COUNT(*) FROM Finance) AS finance,
    (
        (SELECT COUNT(*) FROM Employees) +
        (SELECT COUNT(*) FROM Projects) +
        (SELECT COUNT(*) FROM Tasks) +
        (SELECT COUNT(*) FROM Finance)
    ) AS total_records;


/*
============================================================
FINAL EXPECTED RESULTS
============================================================

Employees              : 4,999
Projects               : 10,000
Tasks                  : 500
Finance                : 1,000
Total                  : 16,499

Primary Keys           : PASS
NULL Primary IDs       : 0
Duplicate Primary IDs  : 0

Tasks → Projects       : 0 invalid
Tasks → Employees      : 0 invalid
Finance → Projects     : 0 invalid

Employee Workload      : 0 invalid
Employee Performance   : 0 invalid
Task Progress          : 0 invalid
Task Hours             : 0 invalid
Finance Amounts        : 0 invalid

Database Validation    : COMPLETE

Author: Rajesh Mani
============================================================
*/