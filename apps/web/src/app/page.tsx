"use client";

import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { useTheme } from "@/contexts/theme-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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

// GitHub Icon Component
const GitHubIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
  </svg>
);
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from "recharts";

export default function DashboardPage() {
  const [rangeDays, setRangeDays] = useState<number | null>(7);
  const [copied, setCopied] = useState(false);
  const [selectedContributor, setSelectedContributor] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { accentColor } = useTheme();

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
    queryKey: ["daily-commits", rangeDays, selectedContributor],
    queryFn: () => api.getDailyCommits(rangeDays, selectedContributor),
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

  const selectedContributorData = useMemo(() => {
    if (!selectedContributor || !dashboardData?.contributors) return null;
    return dashboardData.contributors.find(c => c.login === selectedContributor);
  }, [selectedContributor, dashboardData?.contributors]);

  const sortedContributors = useMemo(() => {
    if (!dashboardData?.contributors) return [];
    return [...dashboardData.contributors].sort((a, b) => b.momentum_score - a.momentum_score);
  }, [dashboardData?.contributors]);

  // Computed metrics that switch between team and individual contributor data
  const displayMetrics = useMemo(() => {
    if (selectedContributorData) {
      // Calculate individual contributor's internal/external split
      const totalCommits = selectedContributorData.commits;
      const internalPercentage = selectedContributorData.is_internal ? 100 : 0;
      const externalPercentage = selectedContributorData.is_internal ? 0 : 100;
      
      return {
        totalCommits: selectedContributorData.commits,
        momentumScore: selectedContributorData.momentum_score,
        internalPercentage,
        externalPercentage,
        isIndividual: true,
      };
    }
    
    // Team-wide data
    return {
      totalCommits: dashboardData?.team_summary.total_commits || 0,
      momentumScore: dashboardData?.team_summary.momentum_score || 0,
      internalPercentage: dashboardData?.team_summary.internal_percentage || 0,
      externalPercentage: dashboardData?.team_summary.external_percentage || 0,
      isIndividual: false,
    };
  }, [selectedContributorData, dashboardData]);

  // Filter risk flags for selected contributor
  const displayRiskFlags = useMemo(() => {
    if (!dashboardData?.risk_flags) return [];
    if (!selectedContributor) return dashboardData.risk_flags;
    
    // Filter to only show flags related to the selected contributor
    return dashboardData.risk_flags.filter(
      flag => flag.contributor === selectedContributor
    );
  }, [dashboardData?.risk_flags, selectedContributor]);

  // Get accent color HSL value for gradients
  const getAccentColorHsl = () => {
    const accentColors: Record<string, string> = {
      gold: "45 65% 52%",
      "metallic-pink": "335 45% 58%",
      bronze: "28 55% 42%",
      copper: "18 65% 48%",
      platinum: "200 12% 80%",
      steel: "210 20% 55%",
      "rose-gold": "15 45% 60%",
      titanium: "195 18% 65%",
    };
    return accentColors[accentColor] || accentColors.gold;
  };

  // Prepare pie chart data for contribution split
  const pieChartData = useMemo(() => {
    return [
      { name: "Internal", value: displayMetrics.internalPercentage },
      { name: "External", value: displayMetrics.externalPercentage },
    ];
  }, [displayMetrics.internalPercentage, displayMetrics.externalPercentage]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Navigation />
        <main className="flex-1 p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <div className="space-y-6">
              <div className="h-12 bg-[hsl(0_0%_8%)] rounded-lg animate-pulse" />
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-40 bg-[hsl(0_0%_8%)] rounded-lg animate-pulse" />
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
              <div className="flex items-center gap-2 bg-[hsl(0_0%_8%)] rounded-lg p-1">
                <Button
                  variant={rangeDays === 7 ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setRangeDays(7)}
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
            <Card className="glass-card flex flex-col h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {selectedContributor ? `${selectedContributor}'s Commits` : "Total Code Commitment"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <div className="text-3xl font-bold accent-text mb-1">
                  {displayMetrics.totalCommits}
                </div>
                <p className="text-xs text-muted-foreground mb-3">Commits</p>
                {dailyCommitsData?.daily_commits && dailyCommitsData.daily_commits.length > 0 ? (
                  <div className="flex-1 min-h-[120px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={dailyCommitsData.daily_commits}>
                        <defs>
                          <linearGradient id="commitGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={`hsl(${getAccentColorHsl()} / 0.8)`} />
                            <stop offset="100%" stopColor={`hsl(${getAccentColorHsl()} / 0.1)`} />
                          </linearGradient>
                        </defs>
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'hsl(var(--card))', 
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px',
                            padding: '4px 8px'
                          }}
                          labelStyle={{ color: 'hsl(var(--foreground))', fontSize: '10px' }}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="commits" 
                          fill="url(#commitGradient)"
                          stroke={`hsl(${getAccentColorHsl()})`}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, fill: `hsl(${getAccentColorHsl()})` }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="flex-1 min-h-[120px] flex items-center justify-center">
                    <div className="text-center">
                      <TrendingUp className="w-6 h-6 mx-auto mb-1 opacity-50 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground">No trend data</p>
                    </div>
                  </div>
                )}
                <div className="mt-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-muted-foreground">
                    Momentum: {formatMomentumScore(displayMetrics.momentumScore)}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Internal vs External Split */}
            <Card className="glass-card flex flex-col h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {selectedContributor ? "Contributor Type" : "Contribution Split"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <div className="flex-1 min-h-[120px] flex items-center justify-center mb-3">
                  {pieChartData.some(d => d.value > 0) ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <defs>
                          <linearGradient id="internalGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={`hsl(${getAccentColorHsl()} / 0.9)`} />
                            <stop offset="100%" stopColor={`hsl(${getAccentColorHsl()} / 0.5)`} />
                          </linearGradient>
                          <linearGradient id="externalGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={`hsl(${getAccentColorHsl()} / 0.4)`} />
                            <stop offset="100%" stopColor={`hsl(${getAccentColorHsl()} / 0.1)`} />
                          </linearGradient>
                        </defs>
                        <Pie
                          data={pieChartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={30}
                          outerRadius={50}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {pieChartData.map((entry, index) => (
                            <Cell 
                              key={`cell-${index}`} 
                              fill={index === 0 ? "url(#internalGradient)" : "url(#externalGradient)"}
                            />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'hsl(var(--card))', 
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px',
                            padding: '4px 8px'
                          }}
                          labelStyle={{ color: 'hsl(var(--foreground))', fontSize: '10px' }}
                          formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center">
                      <Users className="w-6 h-6 mx-auto mb-1 opacity-50 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground">No data</p>
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Internal</span>
                    <span className="text-lg font-bold accent-text">
                      {displayMetrics.internalPercentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">External</span>
                    <span className="text-lg font-bold">
                      {displayMetrics.externalPercentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Contributor / Selected Contributor */}
            <Card className="glass-card flex flex-col h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {selectedContributor ? "Selected Contributor" : "Top Contributor"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                {(selectedContributorData || topContributor) ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {(selectedContributorData || topContributor)?.avatar_url ? (
                        <img 
                          src={(selectedContributorData || topContributor)!.avatar_url} 
                          alt={(selectedContributorData || topContributor)!.login}
                          className="w-8 h-8 rounded-full"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                          <Users className="w-4 h-4" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold truncate">{(selectedContributorData || topContributor)!.login}</div>
                        <div className="text-xs text-muted-foreground">
                          {(selectedContributorData || topContributor)!.is_internal ? "Internal" : "External"}
                        </div>
                      </div>
                    </div>
                    <div className="text-lg font-bold accent-text">
                      {formatMomentumScore((selectedContributorData || topContributor)!.momentum_score)}
                    </div>
                    <p className="text-xs text-muted-foreground">Momentum Score</p>
                  </div>
                ) : (
                  <div className="text-muted-foreground text-sm">No contributors yet</div>
                )}
              </CardContent>
            </Card>

            {/* Risk Flags Counter */}
            <Card className="glass-card flex flex-col h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {selectedContributor ? `${selectedContributor}'s Risk Flags` : "Risk Flags"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                <div className="text-3xl font-bold accent-text mb-1">
                  {displayRiskFlags.length}
                </div>
                <p className="text-xs text-muted-foreground mb-3">
                  {selectedContributor ? "Personal alerts" : "Active alerts"}
                </p>
                <div className="flex gap-1 flex-wrap">
                  {displayRiskFlags.filter(f => f.severity === "high").length > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {displayRiskFlags.filter(f => f.severity === "high").length} High
                    </Badge>
                  )}
                  {displayRiskFlags.filter(f => f.severity === "medium").length > 0 && (
                    <Badge variant="default" className="text-xs">
                      {displayRiskFlags.filter(f => f.severity === "medium").length} Med
                    </Badge>
                  )}
                  {displayRiskFlags.filter(f => f.severity === "low").length > 0 && (
                    <Badge variant="secondary" className="text-xs">
                      {displayRiskFlags.filter(f => f.severity === "low").length} Low
                    </Badge>
                  )}
                  {displayRiskFlags.length === 0 && selectedContributor && (
                    <span className="text-xs text-muted-foreground">No flags</span>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Daily Commits Bar Chart */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Daily Commits
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  {selectedContributor 
                    ? `Individual commit activity for ${selectedContributor}` 
                    : "Team commit activity over time"}
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
                          date.setDate(date.getDate() + 1);
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
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Contribution Split
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  {selectedContributor 
                    ? `${selectedContributor}'s internal vs external contributions` 
                    : "Team internal vs external contributions"}
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

          {/* Contributors Section */}
          <Card className="glass-card mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Contributors
                  </CardTitle>
                  <CardDescription>
                    {selectedContributor ? "Individual contributor details" : "Top contributors sorted by momentum score"}
                  </CardDescription>
                </div>
                <div className="w-64">
                  <Select 
                    value={selectedContributor || "all"} 
                    onValueChange={(value) => setSelectedContributor(value === "all" ? null : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select contributor" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Contributors</SelectItem>
                      {sortedContributors.map((contributor) => (
                        <SelectItem key={contributor.login} value={contributor.login}>
                          {contributor.login} {contributor.is_internal ? "(Internal)" : "(External)"}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {selectedContributorData ? (
                /* Individual Contributor View */
                <div className="space-y-6">
                  {/* Contributor Profile Header */}
                  <div className="flex items-center gap-4 p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                    {selectedContributorData.avatar_url ? (
                      <img 
                        src={selectedContributorData.avatar_url} 
                        alt={selectedContributorData.login}
                        className="w-16 h-16 rounded-full"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center">
                        <Users className="w-8 h-8" />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold">{selectedContributorData.login}</h3>
                      {selectedContributorData.name && (
                        <p className="text-muted-foreground">{selectedContributorData.name}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant={selectedContributorData.is_internal ? "default" : "secondary"}>
                          {selectedContributorData.is_internal ? "Internal" : "External"}
                        </Badge>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <TrendingUp className="w-4 h-4" />
                          <span>Momentum: {formatMomentumScore(selectedContributorData.momentum_score)}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="icon"
                      asChild
                      className="shrink-0"
                    >
                      <a
                        href={`https://github.com/${selectedContributorData.login}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={`View ${selectedContributorData.login} on GitHub`}
                      >
                        <GitHubIcon className="w-5 h-5" />
                      </a>
                    </Button>
                  </div>

                  {/* Contributor Metrics Grid */}
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div className="p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <GitCommit className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Commits</span>
                      </div>
                      <div className="text-2xl font-bold accent-text">
                        {selectedContributorData.commits}
                      </div>
                    </div>
                    
                    <div className="p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <GitPullRequest className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">PRs Opened</span>
                      </div>
                      <div className="text-2xl font-bold accent-text">
                        {selectedContributorData.prs_opened}
                      </div>
                    </div>
                    
                    <div className="p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">PRs Merged</span>
                      </div>
                      <div className="text-2xl font-bold accent-text">
                        {selectedContributorData.prs_merged}
                      </div>
                    </div>
                    
                    <div className="p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Issues Closed</span>
                      </div>
                      <div className="text-2xl font-bold accent-text">
                        {selectedContributorData.issues_closed}
                      </div>
                    </div>
                  </div>

                  {/* Contributor Performance Summary */}
                  <div className="p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                    <h4 className="font-semibold mb-3">Performance Summary</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">PR Success Rate:</span>
                        <span className="font-semibold">
                          {selectedContributorData.prs_opened > 0
                            ? `${((selectedContributorData.prs_merged / selectedContributorData.prs_opened) * 100).toFixed(1)}%`
                            : "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Avg Commits per PR:</span>
                        <span className="font-semibold">
                          {selectedContributorData.prs_merged > 0
                            ? (selectedContributorData.commits / selectedContributorData.prs_merged).toFixed(1)
                            : "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Momentum Score:</span>
                        <span className="font-semibold accent-text">
                          {formatMomentumScore(selectedContributorData.momentum_score)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* All Contributors Ranking View */
                dashboardData?.contributors && dashboardData.contributors.length > 0 ? (
                  <div className="space-y-3">
                    {sortedContributors
                      .slice(0, 10)
                      .map((contributor, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-4 p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)] hover:bg-[hsl(0_0%_10%)] transition-colors"
                        >
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold">
                            {index + 1}
                          </div>
                          {contributor.avatar_url ? (
                            <img 
                              src={contributor.avatar_url} 
                              alt={contributor.login}
                              className="w-10 h-10 rounded-full cursor-pointer"
                              onClick={() => setSelectedContributor(contributor.login)}
                            />
                          ) : (
                            <div 
                              className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center cursor-pointer"
                              onClick={() => setSelectedContributor(contributor.login)}
                            >
                              <Users className="w-5 h-5" />
                            </div>
                          )}
                          <div 
                            className="flex-1 min-w-0 cursor-pointer"
                            onClick={() => setSelectedContributor(contributor.login)}
                          >
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
                          <Button
                            variant="ghost"
                            size="icon"
                            asChild
                            className="shrink-0"
                          >
                            <a
                              href={`https://github.com/${contributor.login}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              aria-label={`View ${contributor.login} on GitHub`}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <GitHubIcon className="w-5 h-5" />
                            </a>
                          </Button>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No contributors data available</p>
                  </div>
                )
              )}
            </CardContent>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Risk Flags Section */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Risk Flags
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  {selectedContributor 
                    ? `Alerts and warnings for ${selectedContributor}` 
                    : "Active alerts and warnings for your team"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {displayRiskFlags.length > 0 ? (
                  <div className="space-y-3">
                    {displayRiskFlags.map((flag, index) => (
                      <div
                        key={index}
                        className="p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)]"
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
                        {/* https://github.com/SimonSaysGiveMeSmile */}
                        {flag.contributor && !selectedContributor && (
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
                    <p>{selectedContributor ? `No risk flags for ${selectedContributor}` : "No risk flags at this time"}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Weekly Recap */}
            <Card className="glass-card">
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
                    <pre className="whitespace-pre-wrap text-sm text-muted-foreground font-sans bg-[hsl(0_0%_8%)] p-4 rounded-lg">
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
