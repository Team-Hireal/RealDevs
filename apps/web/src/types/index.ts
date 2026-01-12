/**
 * Shared TypeScript types for RealDevs frontend
 */

export interface User {
  login: string;
  id: number;
  name?: string;
  avatar_url?: string;
}

export interface Repository {
  id: number;
  full_name: string;
  owner: string;
  name: string;
  private: boolean;
  default_branch: string;
  updated_at?: string;
  last_synced_at?: string;
}

export interface Contributor {
  login: string;
  name?: string;
  avatar_url?: string;
  is_internal: boolean;
  commits: number;
  prs_opened: number;
  prs_merged: number;
  issues_closed: number;
  average_trend: number;
}

export interface TeamSummary {
  total_commits: number;
  total_prs_opened: number;
  total_prs_merged: number;
  total_issues_closed: number;
  average_trend: number;
  internal_commits: number;
  external_commits: number;
  internal_percentage: number;
  external_percentage: number;
}

export interface RepoSummary {
  repo_id: number;
  full_name: string;
  commits: number;
  prs_opened: number;
  prs_merged: number;
  issues_closed: number;
  average_trend: number;
  last_synced: string | null;
}

export type RiskSeverity = 'low' | 'medium' | 'high';

export interface RiskFlag {
  type: string;
  severity: RiskSeverity;
  title: string;
  description: string;
  repo?: string;
  contributor?: string;
}

export interface DashboardData {
  team_summary: TeamSummary;
  repo_summaries: RepoSummary[];
  risk_flags: RiskFlag[];
  contributors: Contributor[];
  last_synced: string | null;
  range_days: number;
}

export interface TeamMember {
  id: number;
  github_login: string;
  created_at: string;
}

export interface Settings {
  [key: string]: string;
}

