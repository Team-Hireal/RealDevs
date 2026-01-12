"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { 
  RefreshCw, 
  TrendingUp, 
  GitPullRequest, 
  GitCommit, 
  AlertTriangle,
  Users,
  ExternalLink,
  Copy,
  CheckCircle,
  Calendar,
  X
} from "lucide-react";
import { useState } from "react";
import Link from "next/link";
import { formatRelativeTime, formatNumber } from "@/lib/utils";
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";

export default function DashboardPage() {
  const [rangeDays, setRangeDays] = useState<number | null>(7);
  const [copied, setCopied] = useState(false);
  const [showCustomDatePopup, setShowCustomDatePopup] = useState(false);
  const [customDays, setCustomDays] = useState<string>("");
  const queryClient = useQueryClient();

  const { data: authStatus } = useQuery({
    queryKey: ["auth-status"],
    queryFn: () => api.getAuthStatus(),
  });

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard", rangeDays],
    queryFn: () => api.getDashboard(rangeDays ?? 7),
    enabled: authStatus?.configured,
  });

  const { data: weeklyReport } = useQuery({
    queryKey: ["weekly-report", rangeDays],
    queryFn: () => api.getWeeklyReport(rangeDays ?? 7),
    enabled: authStatus?.configured,
  });

  const syncMutation = useMutation({
    mutationFn: () => api.syncRepos(rangeDays),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (!authStatus?.configured) {
    return (
      <div className="flex min-h-screen bg-background">
        <Navigation />
        <main className="flex-1 p-8">
          <Card className="glass-card max-w-2xl mx-auto mt-20">
            <CardHeader>
              <CardTitle>Welcome to RealDevs</CardTitle>
              <CardDescription>
                Configure your GitHub Personal Access Token to get started
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/credentials">
                <Button className="w-full">Configure Credentials</Button>
              </Link>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const summary = dashboard?.team_summary;
  const contributors = dashboard?.contributors?.filter(c => c.is_internal) || [];
  const topContributor = contributors[0];

  // Prepare chart data - use accent color and a muted version
  const commitmentData = [
    { name: "Internal", value: summary?.internal_commits || 0, color: "hsl(var(--accent))" },
    { name: "External", value: summary?.external_commits || 0, color: "hsl(var(--muted-foreground))" },
  ];

  const handleCopyReport = async () => {
    if (weeklyReport?.text) {
      await navigator.clipboard.writeText(weeklyReport.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Navigation />
      
      <main className="flex-1 p-8 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold accent-text mb-2">Dashboard</h1>
            <p className="text-muted-foreground">
              Team momentum and activity insights
              {dashboard?.last_synced && (
                <span className="ml-2">
                  • Last synced {formatRelativeTime(dashboard.last_synced)}
                </span>
              )}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Range selector */}
            <div className="flex gap-2 flex-wrap">
              {[7, 30, 365].map((days) => (
                <Button
                  key={days}
                  variant={rangeDays === days ? "default" : "outline"}
                  size="sm"
                  onClick={() => setRangeDays(days)}
                >
                  {days === 365 ? "1 Year" : `${days}d`}
                </Button>
              ))}
              <Button
                variant={rangeDays === null ? "default" : "outline"}
                size="sm"
                onClick={() => setRangeDays(null)}
              >
                All Time
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCustomDatePopup(true)}
                className="flex items-center gap-2"
              >
                <Calendar className="w-4 h-4" />
                Custom
              </Button>
            </div>

            {/* Sync button */}
            <Button
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
              className="glow-sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
              Sync
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-40" />
            ))}
          </div>
        ) : (
          <>
            {/* Top 4 Dashboard Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Card 1: Total Code Commitment Trend */}
              <Card className="glass-card glow">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Commits
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline gap-2">
                    <div className="text-3xl font-bold accent-text">
                      {formatNumber(summary?.total_commits || 0)}
                    </div>
                    <TrendingUp className="w-5 h-5 accent-text" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {rangeDays ? `Last ${rangeDays} days` : "All Time"}
                  </p>
                  <div className="mt-4 h-12">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={[
                        { day: 1, commits: Math.floor((summary?.total_commits || 0) * 0.6) },
                        { day: 2, commits: Math.floor((summary?.total_commits || 0) * 0.7) },
                        { day: 3, commits: Math.floor((summary?.total_commits || 0) * 0.8) },
                        { day: 4, commits: summary?.total_commits || 0 },
                      ]}>
                        <Area 
                          type="monotone" 
                          dataKey="commits" 
                          stroke="hsl(var(--accent))" 
                          fill="hsl(var(--accent) / 0.3)" 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Card 2: Internal vs External */}
              <Card className="glass-card glow">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Commitment Split
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-2xl font-bold accent-text">
                        {summary?.internal_percentage?.toFixed(0) || 0}%
                      </div>
                      <p className="text-xs text-muted-foreground">Internal</p>
                    </div>
                    <div className="h-20 w-20">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={commitmentData}
                            cx="50%"
                            cy="50%"
                            innerRadius={20}
                            outerRadius={35}
                            paddingAngle={2}
                            dataKey="value"
                          >
                            {commitmentData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Internal</span>
                      <span className="font-medium">{summary?.internal_commits || 0}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">External</span>
                      <span className="font-medium">{summary?.external_commits || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Card 3: Top Committer */}
              <Card className="glass-card glow">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Top Contributor
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {topContributor ? (
                    <>
                      <div className="flex items-center gap-3 mb-3">
                        {topContributor.avatar_url ? (
                          <img 
                            src={topContributor.avatar_url} 
                            alt={topContributor.login}
                            className="w-12 h-12 rounded-full border-2 border-primary"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-lg font-bold">
                            {topContributor.login[0].toUpperCase()}
                          </div>
                        )}
                        <div>
                          <div className="font-semibold">{topContributor.login}</div>
                          <div className="text-xs text-muted-foreground">
                            Score: {topContributor.momentum_score}
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <div className="text-muted-foreground">Commits</div>
                          <div className="font-semibold">{topContributor.commits}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">PRs</div>
                          <div className="font-semibold">{topContributor.prs_merged}</div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-sm text-muted-foreground">
                      No data available
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Card 4: Red Flags */}
              <Card className="glass-card glow">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Risk Flags
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline gap-2 mb-3">
                    <div className="text-3xl font-bold">
                      {dashboard?.risk_flags?.length || 0}
                    </div>
                    {(dashboard?.risk_flags?.length || 0) > 0 ? (
                      <AlertTriangle className="w-5 h-5 accent-text" />
                    ) : (
                      <CheckCircle className="w-5 h-5 accent-text" />
                    )}
                  </div>
                  <div className="space-y-1">
                    {dashboard?.risk_flags?.slice(0, 2).map((flag, i) => (
                      <Badge
                        key={i}
                        variant={
                          flag.severity === "high"
                            ? "destructive"
                            : flag.severity === "medium"
                            ? "warning"
                            : "secondary"
                        }
                        className="text-xs"
                      >
                        {flag.type.replace(/_/g, " ")}
                      </Badge>
                    )) || (
                      <p className="text-xs text-muted-foreground">
                        All systems healthy ✓
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Risk Flags Section */}
            {dashboard?.risk_flags && dashboard.risk_flags.length > 0 && (
              <Card className="glass-card mb-8">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 accent-text" />
                    Risk Flags & Alerts
                  </CardTitle>
                  <CardDescription>
                    Potential issues identified in your team's workflow
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboard.risk_flags.map((flag, i) => (
                      <div
                        key={i}
                        className="p-4 rounded-lg border border-border bg-card/50"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge
                                variant={
                                  flag.severity === "high"
                                    ? "destructive"
                                    : flag.severity === "medium"
                                    ? "warning"
                                    : "secondary"
                                }
                              >
                                {flag.severity.toUpperCase()}
                              </Badge>
                              <h4 className="font-semibold">{flag.title}</h4>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {flag.description}
                            </p>
                            {flag.repo && (
                              <p className="text-xs text-muted-foreground mt-1">
                                Repository: {flag.repo}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Contributors Table */}
            <Card className="glass-card mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Team Contributors
                </CardTitle>
                <CardDescription>
                  Individual contribution breakdown for internal team members
                </CardDescription>
              </CardHeader>
              <CardContent>
                {contributors.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                            Contributor
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                            Commits
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                            PRs Opened
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                            PRs Merged
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                            Issues
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                            Score
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {contributors.map((contributor, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-secondary/50">
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                {contributor.avatar_url ? (
                                  <img
                                    src={contributor.avatar_url}
                                    alt={contributor.login}
                                    className="w-8 h-8 rounded-full"
                                  />
                                ) : (
                                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-xs font-bold">
                                    {contributor.login[0].toUpperCase()}
                                  </div>
                                )}
                                <div>
                                  <div className="font-medium">{contributor.login}</div>
                                  {contributor.name && (
                                    <div className="text-xs text-muted-foreground">
                                      {contributor.name}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="text-right py-3 px-4 font-semibold">
                              {contributor.commits}
                            </td>
                            <td className="text-right py-3 px-4 font-semibold">
                              {contributor.prs_opened}
                            </td>
                            <td className="text-right py-3 px-4 font-semibold">
                              {contributor.prs_merged}
                            </td>
                            <td className="text-right py-3 px-4 font-semibold">
                              {contributor.issues_closed}
                            </td>
                            <td className="text-right py-3 px-4">
                              <Badge variant="secondary">{contributor.momentum_score}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No team members configured. Add them in{" "}
                    <Link href="/credentials" className="text-primary hover:underline">
                      Credentials
                    </Link>
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Weekly Recap */}
            {weeklyReport && (
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle>Weekly Recap</CardTitle>
                  <CardDescription>
                    Auto-generated summary for the last {rangeDays} days
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="text-sm whitespace-pre-wrap font-mono bg-secondary/50 p-4 rounded-lg mb-4">
                    {weeklyReport.text}
                  </pre>
                  <Button onClick={handleCopyReport} variant="outline" className="w-full">
                    {copied ? (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy to Clipboard
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Custom Date Popup */}
        {showCustomDatePopup && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <Card className="glass-card max-w-md w-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Custom Date Range</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setShowCustomDatePopup(false);
                      setCustomDays("");
                    }}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <CardDescription>
                  Enter the number of days to filter the dashboard data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Number of Days
                  </label>
                  <Input
                    type="number"
                    placeholder="e.g., 14, 45, 90"
                    value={customDays}
                    onChange={(e) => setCustomDays(e.target.value)}
                    min="1"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        const days = parseInt(customDays);
                        if (days > 0) {
                          setRangeDays(days);
                          setShowCustomDatePopup(false);
                          setCustomDays("");
                        }
                      }
                    }}
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowCustomDatePopup(false);
                      setCustomDays("");
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => {
                      const days = parseInt(customDays);
                      if (days > 0) {
                        setRangeDays(days);
                        setShowCustomDatePopup(false);
                        setCustomDays("");
                      }
                    }}
                    disabled={!customDays || parseInt(customDays) <= 0}
                  >
                    Apply
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}

