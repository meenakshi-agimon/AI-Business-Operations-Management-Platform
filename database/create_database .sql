-- =====================================================================
-- AI Business Operations Management Platform — Supabase PostgreSQL Schema
-- Purpose: Create the Employees, Projects, Tasks, and Finance tables
--          in the Supabase/PostgreSQL database.
--
-- NOTE:
-- Supabase already creates the database for you. Do not run CREATE DATABASE
-- or USE statements in Supabase SQL.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Employees table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.employees (
    employee_id           VARCHAR(20) PRIMARY KEY,
    employee_name         VARCHAR(100),
    email                 VARCHAR(150),
    department            VARCHAR(50),
    job_role              VARCHAR(50),
    experience_years      NUMERIC(4,1),
    hire_date             DATE,
    skills                TEXT,
    availability_status   VARCHAR(20),
    workload_percentage   NUMERIC(5,2),
    active_tasks          INTEGER,
    performance_score     NUMERIC(5,2)
);

-- ---------------------------------------------------------------------
-- 2. Projects table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    project_id            VARCHAR(20) PRIMARY KEY,
    project_name          VARCHAR(150),
    description           TEXT,
    start_date            DATE,
    deadline              DATE,
    status                VARCHAR(20),
    risk_level            VARCHAR(20)
);

-- ---------------------------------------------------------------------
-- 3. Tasks table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.tasks (
    task_id               VARCHAR(20) PRIMARY KEY,
    project_id            VARCHAR(20),
    employee_id           VARCHAR(20),
    task_title            VARCHAR(150),
    task_description      TEXT,
    task_priority         VARCHAR(20),
    task_status           VARCHAR(20),
    task_start_date       DATE,
    task_deadline         DATE,
    required_skill        VARCHAR(50),
    estimated_hours       NUMERIC(6,2),
    hours_logged          NUMERIC(6,2),
    progress_percentage   NUMERIC(5,2),
    allocation_score      NUMERIC(5,2),
    recommended_employee  BOOLEAN,
    CONSTRAINT fk_tasks_project
        FOREIGN KEY (project_id)
        REFERENCES public.projects(project_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_tasks_employee
        FOREIGN KEY (employee_id)
        REFERENCES public.employees(employee_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 4. Finance table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.finance (
    finance_id            VARCHAR(20) PRIMARY KEY,
    project_id            VARCHAR(20),
    expense_type          VARCHAR(50),
    amount                NUMERIC(12,2),
    expense_date          DATE,
    approval_status       VARCHAR(20),
    approved_by           VARCHAR(100),
    is_anomaly            BOOLEAN,
    CONSTRAINT fk_finance_project
        FOREIGN KEY (project_id)
        REFERENCES public.projects(project_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 5. Indexes for faster lookups
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tasks_employee ON public.tasks(employee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project  ON public.tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_finance_project ON public.finance(project_id);
