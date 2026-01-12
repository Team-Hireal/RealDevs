"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  LayoutDashboard, 
  TrendingUp, 
  Users, 
  AlertTriangle, 
  GitCommit, 
  GitPullRequest,
  CheckCircle2,
  RefreshCw,
  Copy,
  Calendar,
  ExternalLink,
  Loader2,
  BarChart3
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function DashboardPage() {
  const [rangeDays, setRangeDays] = useState<number | null>(7);
  const [copied, setCopied] = useState(false);
  const queryClient = useQueryClient();

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ["dashboard", rangeDays],
    queryFn: () => api.getDashboard(rangeDays),
    enabled: true,
  });

  const { data: weeklyReport } = useQuery({
    queryKey: ["weekly-report", rangeDays],
    queryFn: () => api.getWeeklyReport(rangeDays),
    enabled: !!dashboardData,
  });

  const { data: dailyCommitsData } = useQuery({
    queryKey: ["daily-commits", rangeDays],
    queryFn: () => api.getDailyCommits(rangeDays),
    enabled: !!dashboardData,
  });

  const syncMutation = useMutation({
    mutationFn: () => api.syncRepos(rangeDays),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["weekly-report"] });
    },
  });

  const handleCopyReport = async () => {
    if (weeklyReport?.text) {
      await navigator.clipboard.writeText(weeklyReport.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "secondary";
    }
  };

  const formatMomentumScore = (score: number) => {
    return score.toFixed(1);
  };

  const topContributor = dashboardData?.contributors
    ?.sort((a, b) => b.momentum_score - a.momentum_score)[0];

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Navigation />
        <main className="flex-1 p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <div className="space-y-6">
              <div className="h-12 bg-secondary/30 rounded-lg animate-pulse" />
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-40 bg-secondary/30 rounded-lg animate-pulse" />
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Navigation />
      
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-7xl mx-auto">
          {/* Header with Controls */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold accent-text mb-2">Dashboard</h1>
              <p className="text-muted-foreground">
                Team momentum and productivity overview
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Date Range Selector */}
              <div className="flex items-center gap-2 bg-secondary/30 rounded-lg p-1">
                <Button
                  variant={rangeDays === 7 ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setRangeDays(7)}
                  className="glow-sm"
                >
                  7d
                </Button>
                <Button
                  variant={rangeDays === 14 ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setRangeDays(14)}
                >
                  14d
                </Button>
                <Button
                  variant={rangeDays === 30 ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setRangeDays(30)}
                >
                  30d
                </Button>
                <Button
                  variant={rangeDays === null ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setRangeDays(null)}
                >
                  All
                </Button>
              </div>

              {/* Sync Button */}
              <Button
                onClick={() => syncMutation.mutate()}
                disabled={syncMutation.isPending}
                className="glow-sm"
              >
                {syncMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Syncing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sync
                  </>
                )}
              </Button>
            </div>
          </div>

          {dashboardData?.last_synced && (
            <div className="mb-6 text-sm text-muted-foreground flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Last synced: {new Date(dashboardData.last_synced).toLocaleString()}
            </div>
          )}

          {/* 4 Key Metric Cards */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {/* Total Code Commitment Trend */}
            <Card className="glass-card glow">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Code Commitment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold accent-text mb-1">
                  {dashboardData?.team_summary.total_commits || 0}
                </div>
                <p className="text-xs text-muted-foreground">Commits</p>
                <div className="mt-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-muted-foreground">
                    Momentum: {formatMomentumScore(dashboardData?.team_summary.momentum_score || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Internal vs External Split */}
            <Card className="glass-card glow">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Contribution Split
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Internal</span>
                    <span className="text-lg font-bold accent-text">
                      {dashboardData?.team_summary.internal_percentage.toFixed(0) || 0}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">External</span>
                    <span className="text-lg font-bold">
                      {dashboardData?.team_summary.external_percentage.toFixed(0) || 0}%
                    </span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden mt-2">
                    <div 
                      className="h-full accent-bg transition-all"
                      style={{ width: `${dashboardData?.team_summary.internal_percentage || 0}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Contributor */}
            <Card className="glass-card glow">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Top Contributor
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topContributor ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {topContributor.avatar_url ? (
                        <img 
                          src={topContributor.avatar_url} 
                          alt={topContributor.login}
                          className="w-8 h-8 rounded-full"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                          <Users className="w-4 h-4" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold truncate">{topContributor.login}</div>
                        <div className="text-xs text-muted-foreground">
                          {topContributor.is_internal ? "Internal" : "External"}
                        </div>
                      </div>
                    </div>
                    <div className="text-lg font-bold accent-text">
                      {formatMomentumScore(topContributor.momentum_score)}
                    </div>
                    <p className="text-xs text-muted-foreground">Momentum Score</p>
                  </div>
                ) : (
                  <div className="text-muted-foreground text-sm">No contributors yet</div>
                )}
              </CardContent>
            </Card>

            {/* Risk Flags Counter */}
            <Card className="glass-card glow">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Risk Flags
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold accent-text mb-1">
                  {dashboardData?.risk_flags.length || 0}
                </div>
                <p className="text-xs text-muted-foreground mb-3">Active alerts</p>
                <div className="flex gap-1">
                  {dashboardData?.risk_flags && dashboardData.risk_flags.filter(f => f.severity === "high").length > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {dashboardData.risk_flags.filter(f => f.severity === "high").length} High
                    </Badge>
                  )}
                  {dashboardData?.risk_flags && dashboardData.risk_flags.filter(f => f.severity === "medium").length > 0 && (
                    <Badge variant="default" className="text-xs">
                      {dashboardData.risk_flags.filter(f => f.severity === "medium").length} Med
                    </Badge>
                  )}
                  {dashboardData?.risk_flags && dashboardData.risk_flags.filter(f => f.severity === "low").length > 0 && (
                    <Badge variant="secondary" className="text-xs">
                      {dashboardData.risk_flags.filter(f => f.severity === "low").length} Low
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Daily Commits Bar Chart */}
            <Card className="glass-card glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Daily Commits
                </CardTitle>
                <CardDescription>
                  Commit activity over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dailyCommitsData?.daily_commits && dailyCommitsData.daily_commits.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dailyCommitsData.daily_commits}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="date" 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          return `${date.getMonth() + 1}/${date.getDate()}`;
                        }}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                        labelStyle={{ color: 'hsl(var(--foreground))' }}
                      />
                      <Legend wrapperStyle={{ color: 'hsl(var(--foreground))' }} />
                      <Bar dataKey="commits" fill="hsl(var(--primary))" name="Commits" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No commit data available</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Contribution Split Bar Chart */}
            <Card className="glass-card glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Contribution Split
                </CardTitle>
                <CardDescription>
                  Internal vs External contributions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dailyCommitsData?.internal_external_split && dailyCommitsData.internal_external_split.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dailyCommitsData.internal_external_split}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="category" 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                        labelStyle={{ color: 'hsl(var(--foreground))' }}
                      />
                      <Legend wrapperStyle={{ color: 'hsl(var(--foreground))' }} />
                      <Bar dataKey="count" fill="hsl(var(--primary))" name="Commits" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No contribution data available</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Top Contributors Ranking */}
          <Card className="glass-card glow mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Top Contributors Ranking
              </CardTitle>
              <CardDescription>
                Top 10 contributors sorted by momentum score
              </CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData?.contributors && dashboardData.contributors.length > 0 ? (
                <div className="space-y-3">
                  {dashboardData.contributors
                    .slice(0, 10)
                    .map((contributor, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-4 p-3 rounded-lg border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors"
                      >
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold">
                          {index + 1}
                        </div>
                        {contributor.avatar_url ? (
                          <img 
                            src={contributor.avatar_url} 
                            alt={contributor.login}
                            className="w-10 h-10 rounded-full"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                            <Users className="w-5 h-5" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold">{contributor.login}</div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>{contributor.commits} commits</span>
                            <span>•</span>
                            <span>{contributor.prs_merged} PRs</span>
                          </div>
                        </div>
                        <Badge variant={contributor.is_internal ? "default" : "secondary"}>
                          {contributor.is_internal ? "Internal" : "External"}
                        </Badge>
                        <div className="text-right">
                          <div className="font-bold accent-text text-lg">
                            {formatMomentumScore(contributor.momentum_score)}
                          </div>
                          <div className="text-xs text-muted-foreground">momentum</div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No contributors data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Risk Flags Section */}
            <Card className="glass-card glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Risk Flags
                </CardTitle>
                <CardDescription>
                  Active alerts and warnings for your team
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardData?.risk_flags && dashboardData.risk_flags.length > 0 ? (
                  <div className="space-y-3">
                    {dashboardData.risk_flags.map((flag, index) => (
                      <div
                        key={index}
                        className="p-3 rounded-lg border border-border bg-secondary/30"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant={getSeverityColor(flag.severity)}>
                              {flag.severity}
                            </Badge>
                            <span className="font-semibold text-sm">{flag.title}</span>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground mb-1">
                          {flag.description}
                        </p>
                        {flag.repo && (
                          <div className="text-xs text-muted-foreground">
                            Repo: <span className="font-mono">{flag.repo}</span>
                          </div>
                        )}
                        {flag.contributor && (
                          <div className="text-xs text-muted-foreground">
                            Contributor: <span className="font-mono">{flag.contributor}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <CheckCircle2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No risk flags at this time</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Weekly Recap */}
            <Card className="glass-card glow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Weekly Recap
                    </CardTitle>
                    <CardDescription>
                      Auto-generated team summary
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyReport}
                    disabled={!weeklyReport?.text}
                  >
                    {copied ? (
                      <>
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {weeklyReport?.text ? (
                  <div className="prose prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-muted-foreground font-sans bg-secondary/30 p-4 rounded-lg">
                      {weeklyReport.text}
                    </pre>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No report available yet</p>
                    <p className="text-xs mt-2">Sync data to generate a report</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

        </div>
      </main>
    </div>
  );
}
