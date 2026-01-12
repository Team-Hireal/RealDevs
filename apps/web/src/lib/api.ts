/**
 * API client for RealDevs backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export interface ApiError {
  ok: false
  error: string
}

export interface UserInfo {
  login: string
  id: number
  name?: string
  avatar_url?: string
}

export interface AuthResponse {
  ok: boolean
  user?: UserInfo
  error?: string
}

export interface RepoInfo {
  id: number
  full_name: string
  owner: string
  name: string
  private: boolean
  default_branch: string
  updated_at?: string
  last_synced_at?: string
}

export interface DashboardData {
  team_summary: {
    total_commits: number
    total_prs_opened: number
    total_prs_merged: number
    total_issues_closed: number
    average_trend: number
    internal_commits: number
    external_commits: number
    internal_percentage: number
    external_percentage: number
  }
  repo_summaries: Array<{
    repo_id: number
    full_name: string
    commits: number
    prs_opened: number
    prs_merged: number
    issues_closed: number
    average_trend: number
    last_synced: string | null
  }>
  risk_flags: Array<{
    type: string
    severity: 'low' | 'medium' | 'high'
    title: string
    description: string
    repo?: string
    contributor?: string
  }>
  contributors: Array<{
    login: string
    name?: string
    avatar_url?: string
    is_internal: boolean
    commits: number
    prs_opened: number
    prs_merged: number
    issues_closed: number
    average_trend: number
  }>
  last_synced: string | null
  range_days: number
}

export interface TeamMember {
  id: number
  github_login: string
  created_at: string
}

export interface Settings {
  [key: string]: string
}

export interface InternalOrgsConfig {
  organizations: string[]
  repos: string[]
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Network error' }))
      throw new Error(error.error || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async health() {
    return this.request<{ status: string; service: string }>('/health')
  }

  async submitPat(pat: string, storeMode: 'encrypted' | 'memory' = 'encrypted'): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/pat', {
      method: 'POST',
      body: JSON.stringify({ pat, store_mode: storeMode }),
    })
  }

  async getAuthStatus() {
    return this.request<{ ok: boolean; configured: boolean; user?: UserInfo }>('/auth/status')
  }

  async listRepos() {
    return this.request<{ repos: RepoInfo[] }>('/repos')
  }

  async getSelectedRepos() {
    return this.request<{ repos: RepoInfo[] }>('/repos/selected')
  }

  async selectRepos(repoFullNames: string[]) {
    return this.request<{ ok: boolean; selected_count: number }>('/repos/select', {
      method: 'POST',
      body: JSON.stringify({ repo_full_names: repoFullNames }),
    })
  }

  async syncRepos(rangeDays: number | null = 7) {
    // https://github.com/SimonSaysGiveMeSmile
    const param = rangeDays === null ? 'all' : rangeDays
    return this.request<{ ok: boolean; synced_repos: string[]; stats: any }>('/sync', {
      method: 'POST',
      body: JSON.stringify({ range_days: param }),
    })
  }

  async getDashboard(rangeDays: number | null = 7): Promise<DashboardData> {
    const param = rangeDays === null ? 'all' : rangeDays
    return this.request<DashboardData>(`/dashboard?range_days=${param}`)
  }

  async getDailyCommits(rangeDays: number | null = 7, contributorLogin: string | null = null): Promise<{
    daily_commits: Array<{
      date: string
      commits: number
      internal: number
      external: number
    }>
    internal_external_split: Array<{
      category: string
      count: number
    }>
  }> {
    const param = rangeDays === null ? 'all' : rangeDays
    const url = contributorLogin 
      ? `/dashboard/daily-commits?range_days=${param}&contributor_login=${encodeURIComponent(contributorLogin)}`
      : `/dashboard/daily-commits?range_days=${param}`
    return this.request<{
      daily_commits: Array<{
        date: string
        commits: number
        internal: number
        external: number
      }>
      internal_external_split: Array<{
        category: string
        count: number
      }>
    }>(url)
  }

  async getWeeklyReport(rangeDays: number | null = 7) {
    const param = rangeDays === null ? 'all' : rangeDays
    return this.request<{ text: string }>(`/report/weekly?range_days=${param}`)
  }

  async getTeamMembers() {
    return this.request<{ members: TeamMember[] }>('/team-members')
  }

  async updateTeamMembers(githubLogins: string[]) {
    return this.request<{ ok: boolean; message: string }>('/team-members', {
      method: 'POST',
      body: JSON.stringify({ github_logins: githubLogins }),
    })
  }

  async getSettings() {
    return this.request<{ settings: Settings }>('/settings')
  }

  async updateSetting(key: string, value: string) {
    return this.request<{ ok: boolean; message: string }>('/settings', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
    })
  }

  async resetAll() {
    return this.request<{ ok: boolean; message: string }>('/reset', {
      method: 'POST',
    })
  }

  async getInternalOrgs() {
    return this.request<InternalOrgsConfig>('/internal-orgs')
  }

  async updateInternalOrgs(organizations: string[], repos: string[] = []) {
    return this.request<{ ok: boolean; message: string }>('/internal-orgs', {
      method: 'POST',
      body: JSON.stringify({ organizations, repos }),
    })
  }
}

export const api = new ApiClient()

