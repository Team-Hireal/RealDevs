-- RealDevs Database Initialization Script for Supabase
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/_/sql

-- ============================================================================
-- 1. AUTH TOKENS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth_tokens (
    id SERIAL PRIMARY KEY,
    encrypted_token TEXT NOT NULL,
    github_user_login VARCHAR(255) NOT NULL,
    github_user_id INTEGER NOT NULL,
    store_mode VARCHAR(20) DEFAULT 'encrypted',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2. REPOSITORIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    github_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    private BOOLEAN DEFAULT FALSE,
    default_branch VARCHAR(100) DEFAULT 'main',
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_repositories_github_id ON repositories(github_id);
CREATE INDEX IF NOT EXISTS idx_repositories_full_name ON repositories(full_name);

-- ============================================================================
-- 3. CONTRIBUTORS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS contributors (
    id SERIAL PRIMARY KEY,
    github_id INTEGER NOT NULL,
    login VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url VARCHAR(512),
    is_team_member BOOLEAN DEFAULT FALSE,
    repo_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    linkedin_url VARCHAR(512),
    twitter_url VARCHAR(512),
    website_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uix_repo_contributor UNIQUE (repo_id, github_id)
);

CREATE INDEX IF NOT EXISTS idx_contributors_github_id ON contributors(github_id);
CREATE INDEX IF NOT EXISTS idx_contributors_login ON contributors(login);

-- ============================================================================
-- 4. DAILY STATS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    repo_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    contributor_id INTEGER NOT NULL REFERENCES contributors(id) ON DELETE CASCADE,
    commits_count INTEGER DEFAULT 0,
    prs_opened INTEGER DEFAULT 0,
    prs_merged INTEGER DEFAULT 0,
    prs_closed INTEGER DEFAULT 0,
    issues_closed INTEGER DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uix_daily_repo_contributor UNIQUE (date, repo_id, contributor_id)
);

CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);

-- ============================================================================
-- 5. TEAM MEMBERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_members (
    id SERIAL PRIMARY KEY,
    github_login VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_members_github_login ON team_members(github_login);

-- ============================================================================
-- 6. SETTINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- ============================================================================
-- 7. EXTERNAL COMMITS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS external_commits (
    id SERIAL PRIMARY KEY,
    github_user_login VARCHAR(255) NOT NULL,
    github_user_id INTEGER NOT NULL,
    repo_full_name VARCHAR(255) NOT NULL,
    repo_owner VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(40) UNIQUE NOT NULL,
    commit_date TIMESTAMP WITH TIME ZONE NOT NULL,
    commit_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_external_commits_github_user_login ON external_commits(github_user_login);
CREATE INDEX IF NOT EXISTS idx_external_commits_github_user_id ON external_commits(github_user_id);
CREATE INDEX IF NOT EXISTS idx_external_commits_repo_full_name ON external_commits(repo_full_name);
CREATE INDEX IF NOT EXISTS idx_external_commits_commit_sha ON external_commits(commit_sha);
CREATE INDEX IF NOT EXISTS idx_external_commits_commit_date ON external_commits(commit_date);

-- ============================================================================
-- 8. EXTERNAL CONTRIBUTORS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS external_contributors (
    id SERIAL PRIMARY KEY,
    github_login VARCHAR(255) UNIQUE NOT NULL,
    github_user_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_external_contributors_github_login ON external_contributors(github_login);
CREATE INDEX IF NOT EXISTS idx_external_contributors_github_user_id ON external_contributors(github_user_id);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected output:
-- auth_tokens
-- contributors
-- daily_stats
-- external_commits
-- external_contributors
-- repositories
-- settings
-- team_members

-- ============================================================================
-- SUCCESS!
-- ============================================================================
-- Your database is now initialized and ready to use.
-- 
-- Next steps:
-- 1. Go to your deployment: https://www.realdevs.pro/credentials
-- 2. Add your GitHub username or PAT
-- 3. Configure team members
-- 4. Start tracking your repositories!
-- ============================================================================

