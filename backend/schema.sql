-- NyayaSetu Database Schema
-- Run this in Supabase SQL Editor (https://supabase.com -> SQL Editor)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clusters table (must be created first, grievances references it)
CREATE TABLE IF NOT EXISTS clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT,
    ward TEXT,
    member_ids TEXT[],
    summary TEXT,
    ai_brief TEXT,
    count INTEGER DEFAULT 0,
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grievances table
CREATE TABLE IF NOT EXISTS grievances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_name TEXT NOT NULL,
    phone TEXT,
    ward TEXT NOT NULL,
    district TEXT DEFAULT 'Thiruvananthapuram',
    description TEXT NOT NULL,
    category TEXT,
    urgency INTEGER,
    credibility_score INTEGER,
    ai_summary TEXT,
    status TEXT DEFAULT 'open',
    hash TEXT,
    cluster_id UUID REFERENCES clusters(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_confirmed BOOLEAN DEFAULT FALSE,
    support_count INTEGER DEFAULT 0
);

-- Actions table
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grievance_id UUID REFERENCES grievances(id),
    action_type TEXT,
    performed_by TEXT DEFAULT 'system',
    notes TEXT,
    hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Legal cases table
CREATE TABLE IF NOT EXISTS legal_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prisoner_name TEXT NOT NULL,
    ward TEXT,
    ipc_section TEXT,
    max_sentence_years INTEGER,
    detention_start DATE,
    eligible_436a BOOLEAN DEFAULT FALSE,
    months_detained INTEGER,
    dlsa_contact TEXT,
    grievance_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_grievances_status ON grievances(status);
CREATE INDEX IF NOT EXISTS idx_grievances_ward ON grievances(ward);
CREATE INDEX IF NOT EXISTS idx_grievances_category ON grievances(category);
CREATE INDEX IF NOT EXISTS idx_grievances_cluster ON grievances(cluster_id);
CREATE INDEX IF NOT EXISTS idx_actions_grievance ON actions(grievance_id);
CREATE INDEX IF NOT EXISTS idx_legal_cases_eligible ON legal_cases(eligible_436a);

-- Enable Row Level Security (but allow all for anon key — for hackathon)
ALTER TABLE grievances ENABLE ROW LEVEL SECURITY;
ALTER TABLE clusters ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_cases ENABLE ROW LEVEL SECURITY;

-- Policies: allow all operations for anon key
CREATE POLICY "Allow all on grievances" ON grievances FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on clusters" ON clusters FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on actions" ON actions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on legal_cases" ON legal_cases FOR ALL USING (true) WITH CHECK (true);


-- =============================================
-- V2 EXPANSION: New tables and columns
-- =============================================

-- Add image columns to grievances (Feature 4: Multimodal AI)
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS image_verified BOOLEAN DEFAULT NULL;
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS support_count INTEGER DEFAULT 0;

-- Railway clusters table (must be created before railway_grievances)
CREATE TABLE IF NOT EXISTS railway_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT,
    train_number TEXT,
    railway_zone TEXT,
    station TEXT,
    member_ids TEXT[],
    summary TEXT,
    ai_brief TEXT,
    count INTEGER DEFAULT 0,
    alert_sent BOOLEAN DEFAULT FALSE,
    next_station TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Railway grievances table
CREATE TABLE IF NOT EXISTS railway_grievances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    passenger_name TEXT NOT NULL,
    phone TEXT,
    train_number TEXT NOT NULL,
    railway_zone TEXT NOT NULL,
    station TEXT,
    coach_number TEXT,
    description TEXT NOT NULL,
    category TEXT,
    urgency INTEGER,
    credibility_score INTEGER,
    ai_summary TEXT,
    status TEXT DEFAULT 'open',
    hash TEXT,
    cluster_id UUID REFERENCES railway_clusters(id),
    image_url TEXT,
    image_verified BOOLEAN DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_confirmed BOOLEAN DEFAULT FALSE
);

-- Railway actions table
CREATE TABLE IF NOT EXISTS railway_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grievance_id UUID REFERENCES railway_grievances(id),
    action_type TEXT,
    performed_by TEXT DEFAULT 'system',
    notes TEXT,
    hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Budget allocations table (FinTech & Audit Layer)
CREATE TABLE IF NOT EXISTS budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grievance_id UUID REFERENCES grievances(id),
    cluster_id UUID REFERENCES clusters(id),
    department TEXT NOT NULL,
    amount_allocated NUMERIC(12,2) DEFAULT 0,
    amount_spent NUMERIC(12,2) DEFAULT 0,
    description TEXT,
    auditor_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    flagged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Predictions table (Predictive Resource Allocation)
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ward TEXT NOT NULL,
    category TEXT NOT NULL,
    month TEXT NOT NULL,
    predicted_count INTEGER,
    confidence FLOAT,
    trend TEXT,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- V2 Indexes
CREATE INDEX IF NOT EXISTS idx_railway_grievances_status ON railway_grievances(status);
CREATE INDEX IF NOT EXISTS idx_railway_grievances_train ON railway_grievances(train_number);
CREATE INDEX IF NOT EXISTS idx_railway_grievances_zone ON railway_grievances(railway_zone);
CREATE INDEX IF NOT EXISTS idx_railway_grievances_cluster ON railway_grievances(cluster_id);
CREATE INDEX IF NOT EXISTS idx_railway_actions_grievance ON railway_actions(grievance_id);
CREATE INDEX IF NOT EXISTS idx_budget_grievance ON budget_allocations(grievance_id);
CREATE INDEX IF NOT EXISTS idx_budget_cluster ON budget_allocations(cluster_id);
CREATE INDEX IF NOT EXISTS idx_budget_flagged ON budget_allocations(auditor_flagged);
CREATE INDEX IF NOT EXISTS idx_predictions_ward ON predictions(ward);
CREATE INDEX IF NOT EXISTS idx_predictions_month ON predictions(month);

-- V2 RLS
ALTER TABLE railway_grievances ENABLE ROW LEVEL SECURITY;
ALTER TABLE railway_clusters ENABLE ROW LEVEL SECURITY;
ALTER TABLE railway_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE budget_allocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all on railway_grievances" ON railway_grievances FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on railway_clusters" ON railway_clusters FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on railway_actions" ON railway_actions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on budget_allocations" ON budget_allocations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on predictions" ON predictions FOR ALL USING (true) WITH CHECK (true);


-- =============================================
-- PHASE 1: Authentication & Authorization
-- =============================================

-- Users table (citizen, officer, auditor, admin)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('citizen', 'officer', 'auditor', 'admin')),
    full_name TEXT,
    phone TEXT,
    ward TEXT,
    sms_notifications_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_ward ON users(ward);

-- Assignments table for officer assignment workflow
CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grievance_id UUID NOT NULL REFERENCES grievances(id) ON DELETE CASCADE,
    officer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'assigned' CHECK (status IN ('assigned', 'in_progress', 'completed')),
    notes TEXT,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_assignments_grievance ON assignments(grievance_id);
CREATE INDEX IF NOT EXISTS idx_assignments_officer ON assignments(officer_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);

-- Add officer_id and auditor_id to grievances if not exists
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS officer_id UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS auditor_id UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE grievances ADD COLUMN IF NOT EXISTS at_risk_of_sla_breach BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_grievances_officer ON grievances(officer_id);
CREATE INDEX IF NOT EXISTS idx_grievances_auditor ON grievances(auditor_id);
CREATE INDEX IF NOT EXISTS idx_grievances_sla_risk ON grievances(at_risk_of_sla_breach);

-- Apply RLS and base policies for users (allow all for now, can be refined)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all on users" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on assignments" ON assignments FOR ALL USING (true) WITH CHECK (true);
