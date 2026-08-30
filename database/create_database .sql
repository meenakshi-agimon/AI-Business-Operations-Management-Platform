-- =====================================================================
-- AI Business Operations Management Platform — Database Schema
-- Author: Akhilesh P. S
-- Purpose: Create database + Employees, Projects, Tasks, Finance tables
--          with primary and foreign keys.
--
-- NOTES / ASSUMPTIONS (flag these with the team before finalizing):
--   1. Employees table is built directly from the cleaned Employee
--      Management dataset (Business_Operation.csv → cleaned version).
--      Column names/types below match that dataset's protected fields.
--   2. Projects table is a reasonable placeholder — Project Management
--      module details (owned by another subgroup) may need adjusting once
--      their schema/dataset is finalized.
--   3. Tasks table links Employees + Projects, and includes the
--      allocation fields (required_skill, allocation_score,
--      recommended_employee) from the Employee Management flow.
--   4. Finance table is a reasonable placeholder based on the proposal's
--      "expenses, invoices, budgets, approvals" description — confirm
--      with whoever owns the Finance Management module.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Create the database
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS ai_ops_platform;
USE ai_ops_platform;

-- ---------------------------------------------------------------------
-- 2. Employees table
--    Source: cleaned Employee Management dataset
-- ---------------------------------------------------------------------
CREATE TABLE Employees (
    employee_id           VARCHAR(20)   NOT NULL,
    employee_name         VARCHAR(100),
    email                 VARCHAR(150),
    department            VARCHAR(50),
    job_role              VARCHAR(50),
    experience_years      DECIMAL(4,1),
    hire_date             DATE,
    skills                TEXT,               -- comma-separated, as cleaned
    availability_status   VARCHAR(20),
    workload_percentage   DECIMAL(5,2),
    active_tasks          INT,
    performance_score     DECIMAL(5,2),
    PRIMARY KEY (employee_id)
);

-- ---------------------------------------------------------------------
-- 3. Projects table
--    Placeholder structure — confirm fields with Project Management
--    subgroup once their dataset/requirements are finalized.
-- ---------------------------------------------------------------------
CREATE TABLE Projects (
    project_id            VARCHAR(20)   NOT NULL,
    project_name          VARCHAR(150),
    description           TEXT,
    start_date            DATE,
    deadline              DATE,
    status                VARCHAR(20),        -- e.g. Not Started / In Progress / Completed
    risk_level            VARCHAR(20),        -- e.g. Low / Medium / High (AI risk identification output)
    PRIMARY KEY (project_id)
);

-- ---------------------------------------------------------------------
-- 4. Tasks table
--    Links Employees + Projects. Includes allocation-related fields
--    from the Employee Management AI flow:
--    Required Skill -> Skill Match -> Availability -> Workload -> Recommended Employee
-- ---------------------------------------------------------------------
CREATE TABLE Tasks (
    task_id               VARCHAR(20)   NOT NULL,
    project_id            VARCHAR(20),
    employee_id           VARCHAR(20),        -- employee currently assigned (nullable until assigned)
    task_title            VARCHAR(150),
    task_description      TEXT,
    task_priority         VARCHAR(20),        -- Low / Medium / High / Critical
    task_status           VARCHAR(20),        -- Not Started / In Progress / Blocked / Completed
    task_start_date       DATE,
    task_deadline         DATE,
    required_skill        VARCHAR(50),
    estimated_hours       DECIMAL(6,2),
    hours_logged          DECIMAL(6,2),
    progress_percentage   DECIMAL(5,2),
    allocation_score      DECIMAL(5,2),
    recommended_employee  TINYINT(1),         -- 0/1 flag
    PRIMARY KEY (task_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 5. Finance table
--    Placeholder structure based on proposal's Finance Management
--    description (expenses, invoices, budgets, approvals). Confirm
--    fields with whoever owns the Finance Management module.
-- ---------------------------------------------------------------------
CREATE TABLE Finance (
    finance_id            VARCHAR(20)   NOT NULL,
    project_id            VARCHAR(20),        -- expense tied to a project (nullable if general expense)
    expense_type          VARCHAR(50),        -- e.g. Travel, Equipment, Software
    amount                DECIMAL(12,2),
    expense_date          DATE,
    approval_status       VARCHAR(20),        -- Pending / Approved / Rejected
    approved_by           VARCHAR(100),
    is_anomaly            TINYINT(1),         -- 0/1 flag, output of anomaly detection
    PRIMARY KEY (finance_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 6. Indexes to speed up common lookups (optional but recommended)
-- ---------------------------------------------------------------------
CREATE INDEX idx_tasks_employee ON Tasks(employee_id);
CREATE INDEX idx_tasks_project  ON Tasks(project_id);
CREATE INDEX idx_finance_project ON Finance(project_id);
