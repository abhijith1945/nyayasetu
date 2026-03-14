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
    resolution_confirmed BOOLEAN DEFAULT FALSE
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
