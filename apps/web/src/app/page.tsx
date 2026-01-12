"use client";

import { useState, useMemo, useEffect } from "react";
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
  TrendingDown,
  Minus,
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
  const [selectedHighFlag, setSelectedHighFlag] = useState<string | null>(null);
  const [selectedMediumFlag, setSelectedMediumFlag] = useState<string | null>(null);
  const [selectedLowFlag, setSelectedLowFlag] = useState<string | null>(null);
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

  const formatAverageTrend = (trend: number | undefined | null) => {
    if (trend === undefined || trend === null || isNaN(trend)) {
      return '0.00';
    }
    const sign = trend > 0 ? '+' : '';
    return `${sign}${trend.toFixed(2)}`;
  };

  const getTrendLabel = (trend: number | undefined | null) => {
    if (trend === undefined || trend === null || isNaN(trend)) {
      return '→ Neutral';
    }
    if (trend > 0) return '↑ Positive';
    if (trend < 0) return '↓ Negative';
    return '→ Neutral';
  };

  const getTrendIcon = (trend: number | undefined | null, className?: string) => {
    const iconClass = className || "w-4 h-4";
    if (trend === undefined || trend === null || isNaN(trend) || trend === 0) {
      return <Minus className={iconClass} />;
    }
    if (trend > 0) {
      return <TrendingUp className={iconClass} />;
    }
    return <TrendingDown className={iconClass} />;
  };

  const getTrendIconColor = (trend: number | undefined | null) => {
    if (trend === undefined || trend === null || isNaN(trend) || trend === 0) {
      return "text-muted-foreground";
    }
    if (trend > 0) {
      return "text-green-500";
    }
    return "text-red-500";
  };

  const topContributor = dashboardData?.contributors
    ?.sort((a, b) => b.average_trend - a.average_trend)[0];

  const selectedContributorData = useMemo(() => {
    if (!selectedContributor || !dashboardData?.contributors) return null;
    return dashboardData.contributors.find(c => c.login === selectedContributor);
  }, [selectedContributor, dashboardData?.contributors]);

  const sortedContributors = useMemo(() => {
    if (!dashboardData?.contributors) return [];
    return [...dashboardData.contributors].sort((a, b) => b.average_trend - a.average_trend);
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
        averageTrend: selectedContributorData.average_trend ?? 0,
        internalPercentage,
        externalPercentage,
        isIndividual: true,
      };
    }
    
    // Team-wide data
    return {
      totalCommits: dashboardData?.team_summary.total_commits || 0,
      averageTrend: dashboardData?.team_summary.average_trend || 0,
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

  // Group risk flags by severity
  const riskFlagsBySeverity = useMemo(() => {
    const grouped = {
      high: [] as typeof displayRiskFlags,
      medium: [] as typeof displayRiskFlags,
      low: [] as typeof displayRiskFlags,
    };
    
    displayRiskFlags.forEach(flag => {
      grouped[flag.severity].push(flag);
    });
    
    return grouped;
  }, [displayRiskFlags]);

  // Get selected flag for preview
  const getSelectedFlag = (severity: 'high' | 'medium' | 'low') => {
    const flags = riskFlagsBySeverity[severity];
    if (flags.length === 0) return null;
    
    const selectedIndex = severity === 'high' 
      ? selectedHighFlag 
      : severity === 'medium' 
      ? selectedMediumFlag 
      : selectedLowFlag;
    
    if (selectedIndex === null) return flags[0]; // Default to first flag
    return flags.find((_, idx) => idx.toString() === selectedIndex) || flags[0];
  };

  // Reset selected flags when risk flags or contributor changes
  useEffect(() => {
    setSelectedHighFlag(riskFlagsBySeverity.high.length > 0 ? "0" : null);
    setSelectedMediumFlag(riskFlagsBySeverity.medium.length > 0 ? "0" : null);
    setSelectedLowFlag(riskFlagsBySeverity.low.length > 0 ? "0" : null);
  }, [riskFlagsBySeverity, selectedContributor]);

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

  // Process daily commits data to fill in missing dates
  const processedDailyCommits = useMemo(() => {
    if (!dailyCommitsData?.daily_commits || dailyCommitsData.daily_commits.length === 0) {
      return null;
    }

    const commits = dailyCommitsData.daily_commits;
    
    // Create a map of existing dates
    const commitMap = new Map(
      commits.map(c => [c.date, c.commits])
    );

    // Determine the date range
    let startDate: Date;
    let endDate: Date = new Date();
    endDate.setHours(0, 0, 0, 0);

    if (rangeDays === null) {
      // For "All time", use the earliest commit date
      const dates = commits.map(c => new Date(c.date));
      startDate = new Date(Math.min(...dates.map(d => d.getTime())));
      startDate.setHours(0, 0, 0, 0);
    } else {
      // For specific ranges, use rangeDays
      startDate = new Date();
      startDate.setDate(startDate.getDate() - rangeDays + 1);
      startDate.setHours(0, 0, 0, 0);
    }

    // Fill in all dates in the range
    const filledData: Array<{ date: string; commits: number }> = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      filledData.push({
        date: dateStr,
        commits: commitMap.get(dateStr) || 0
      });
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return filledData;
  }, [dailyCommitsData, rangeDays]);

  // Prepare pie chart data for contribution split
  const pieChartData = useMemo(() => {
    return [
      { name: "Internal", value: displayMetrics.internalPercentage },
      { name: "External", value: displayMetrics.externalPercentage },
    ];
  }, [displayMetrics.internalPercentage, displayMetrics.externalPercentage]);

  // Sort and prepare repository contributions data
  const sortedRepoContributions = useMemo(() => {
    if (!dailyCommitsData || !('repo_contributions' in dailyCommitsData) || !Array.isArray(dailyCommitsData.repo_contributions)) {
      return null;
    }
    
    // Sort by value (commit count) descending - most to least
    const sorted = [...dailyCommitsData.repo_contributions].sort((a, b) => b.value - a.value);
    
    // Get accent color HSL values
    const baseHsl = getAccentColorHsl();
    const baseHue = parseInt(baseHsl.split(' ')[0]);
    const baseSaturation = parseInt(baseHsl.split(' ')[1].replace('%', ''));
    const baseLightness = baseHsl.split(' ')[2];
    
    // Add color information to each entry
    // Use same hue (accent color) for all, vary only saturation to distinguish
    return sorted.map((entry, index) => {
      // Vary saturation smoothly between 50% and 75% to create distinction
      // More commits = higher saturation (more vibrant)
      // Fewer commits = lower saturation (less vibrant)
      const totalRepos = sorted.length;
      if (totalRepos === 1) {
        // Single repo uses base saturation
        return {
          ...entry,
          hue: baseHue,
          saturation: baseHsl.split(' ')[1],
          lightness: baseLightness,
        };
      }
      
      // Distribute saturation from 75% (most commits) to 50% (least commits)
      const saturationRange = 75 - 50;
      const saturation = 75 - (index / (totalRepos - 1)) * saturationRange;
      
      return {
        ...entry,
        hue: baseHue, // Same hue for all - accent color
        saturation: `${Math.round(saturation)}%`,
        lightness: baseLightness,
      };
    });
  }, [dailyCommitsData, accentColor]);

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
                {processedDailyCommits && processedDailyCommits.length > 0 ? (
                  <div className="flex-1 min-h-[120px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={processedDailyCommits}>
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
                      <Minus className="w-6 h-6 mx-auto mb-1 opacity-50 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground">No trend data</p>
                    </div>
                  </div>
                )}
                <div className="mt-3 flex items-center gap-2">
                  <span className={getTrendIconColor(displayMetrics.averageTrend)}>
                    {getTrendIcon(displayMetrics.averageTrend)}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Average Trend: {formatAverageTrend(displayMetrics.averageTrend)}
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
                    <div className="flex items-center gap-2">
                      <span className={getTrendIconColor((selectedContributorData || topContributor)?.average_trend)}>
                        {getTrendIcon((selectedContributorData || topContributor)?.average_trend, "w-5 h-5")}
                      </span>
                      <div className="text-lg font-bold accent-text">
                        {formatAverageTrend((selectedContributorData || topContributor)?.average_trend)}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">Average Trend</p>
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
                {processedDailyCommits && processedDailyCommits.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={processedDailyCommits}>
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

            {/* Contribution Split Pie Chart */}
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
                    ? `${selectedContributor}'s contributions by repository` 
                    : "Team contributions broken down by repository"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {sortedRepoContributions && sortedRepoContributions.length > 0 ? (
                  <div className="flex items-start gap-6">
                    <div className="shrink-0" style={{ width: 200, height: 200 }}>
                      <PieChart width={200} height={200}>
                          <defs>
                            {sortedRepoContributions.map((entry, index) => {
                              const opacity = 0.85;
                              return (
                                <linearGradient key={`gradient-${index}`} id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="0%" stopColor={`hsl(${entry.hue} ${entry.saturation} ${entry.lightness} / ${opacity})`} />
                                  <stop offset="100%" stopColor={`hsl(${entry.hue} ${entry.saturation} ${entry.lightness} / ${opacity * 0.5})`} />
                                </linearGradient>
                              );
                            })}
                          </defs>
                          <Pie
                            data={sortedRepoContributions}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={70}
                            innerRadius={30}
                            paddingAngle={2}
                            dataKey="value"
                          >
                            {sortedRepoContributions.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={`url(#gradient-${index})`} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: 'black', 
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '8px',
                              padding: '8px 12px'
                            }}
                            content={({ active, payload }) => {
                              if (active && payload && payload.length > 0) {
                                const data = payload[0].payload;
                                const repoName = data?.name || '';
                                // Extract repo name (remove organization prefix if present)
                                const displayName = repoName.includes('/') ? repoName.split('/')[1] : repoName;
                                const value = payload[0].value as number;
                                
                                return (
                                  <div style={{ 
                                    backgroundColor: 'black', 
                                    color: 'white', 
                                    fontSize: '12px', 
                                    fontWeight: 'bold',
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    border: '1px solid hsl(var(--border))'
                                  }}>
                                    {`${displayName}: ${value} commits`}
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                        </PieChart>
                    </div>
                    <div className="flex-1 space-y-2 max-h-[200px] overflow-y-auto">
                      {sortedRepoContributions.map((entry, index) => {
                        const color = `hsl(${entry.hue} ${entry.saturation} ${entry.lightness})`;
                        // Extract repo name (remove organization prefix if present)
                        const repoName = entry.name.includes('/') ? entry.name.split('/')[1] : entry.name;
                        
                        return (
                          <div key={index} className="flex items-center justify-between p-2 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <div 
                                className="w-3 h-3 rounded-full shrink-0" 
                                style={{ backgroundColor: color }}
                              />
                              <span className="text-sm truncate">
                                {repoName}
                              </span>
                            </div>
                            <span className="text-sm font-semibold accent-text ml-2">
                              {entry.value}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
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
                    {selectedContributor ? "Individual contributor details" : "Top contributors sorted by average trend"}
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
                          <span className={getTrendIconColor(selectedContributorData?.average_trend)}>
                            {getTrendIcon(selectedContributorData?.average_trend)}
                          </span>
                          <span>Average Trend: {formatAverageTrend(selectedContributorData?.average_trend)}</span>
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
                        <span className="text-muted-foreground">Average Trend:</span>
                        <span className="font-semibold accent-text">
                          {formatAverageTrend(selectedContributorData?.average_trend)}
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
                            <div className="flex items-center justify-end gap-1">
                              <span className={getTrendIconColor(contributor?.average_trend)}>
                                {getTrendIcon(contributor?.average_trend, "w-4 h-4")}
                              </span>
                              <span className="font-bold accent-text text-lg">
                                {formatAverageTrend(contributor?.average_trend)}
                              </span>
                            </div>
                            <div className="text-xs text-muted-foreground">trend</div>
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
                  <div className="space-y-4">
                    {/* High Severity Dropdown */}
                    {riskFlagsBySeverity.high.length > 0 && (
                      <div className="space-y-2">
                        <Select
                          value={selectedHighFlag || "0"}
                          onValueChange={setSelectedHighFlag}
                        >
                          <SelectTrigger>
                            <SelectValue>
                              <div className="flex items-center gap-2">
                                <Badge variant="destructive">High</Badge>
                                <span>{riskFlagsBySeverity.high.length} flag{riskFlagsBySeverity.high.length !== 1 ? 's' : ''}</span>
                              </div>
                            </SelectValue>
                          </SelectTrigger>
                          <SelectContent>
                            {riskFlagsBySeverity.high.map((flag, index) => (
                              <SelectItem key={index} value={index.toString()}>
                                {flag.title}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {getSelectedFlag('high') && (
                          <div className="p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                            <p className="text-sm text-muted-foreground mb-2">
                              {getSelectedFlag('high')!.description}
                            </p>
                            {getSelectedFlag('high')!.repo && (
                              <div className="text-xs text-muted-foreground">
                                Repo: <span className="font-mono">{getSelectedFlag('high')!.repo}</span>
                              </div>
                            )}
                            {getSelectedFlag('high')!.contributor && !selectedContributor && (
                              <div className="text-xs text-muted-foreground mt-1">
                                Contributor: <span className="font-mono">{getSelectedFlag('high')!.contributor}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Medium Severity Dropdown */}
                    {riskFlagsBySeverity.medium.length > 0 && (
                      <div className="space-y-2">
                        <Select
                          value={selectedMediumFlag || "0"}
                          onValueChange={setSelectedMediumFlag}
                        >
                          <SelectTrigger>
                            <SelectValue>
                              <div className="flex items-center gap-2">
                                <Badge variant="default">Medium</Badge>
                                <span>{riskFlagsBySeverity.medium.length} flag{riskFlagsBySeverity.medium.length !== 1 ? 's' : ''}</span>
                              </div>
                            </SelectValue>
                          </SelectTrigger>
                          <SelectContent>
                            {riskFlagsBySeverity.medium.map((flag, index) => (
                              <SelectItem key={index} value={index.toString()}>
                                {flag.title}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {getSelectedFlag('medium') && (
                          <div className="p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                            <p className="text-sm text-muted-foreground mb-2">
                              {getSelectedFlag('medium')!.description}
                            </p>
                            {getSelectedFlag('medium')!.repo && (
                              <div className="text-xs text-muted-foreground">
                                Repo: <span className="font-mono">{getSelectedFlag('medium')!.repo}</span>
                              </div>
                            )}
                            {getSelectedFlag('medium')!.contributor && !selectedContributor && (
                              <div className="text-xs text-muted-foreground mt-1">
                                Contributor: <span className="font-mono">{getSelectedFlag('medium')!.contributor}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Low Severity Dropdown */}
                    {riskFlagsBySeverity.low.length > 0 && (
                      <div className="space-y-2">
                        <Select
                          value={selectedLowFlag || "0"}
                          onValueChange={setSelectedLowFlag}
                        >
                          <SelectTrigger>
                            <SelectValue>
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary">Low</Badge>
                                <span>{riskFlagsBySeverity.low.length} flag{riskFlagsBySeverity.low.length !== 1 ? 's' : ''}</span>
                              </div>
                            </SelectValue>
                          </SelectTrigger>
                          <SelectContent>
                            {riskFlagsBySeverity.low.map((flag, index) => (
                              <SelectItem key={index} value={index.toString()}>
                                {flag.title}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {getSelectedFlag('low') && (
                          <div className="p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                            <p className="text-sm text-muted-foreground mb-2">
                              {getSelectedFlag('low')!.description}
                            </p>
                            {getSelectedFlag('low')!.repo && (
                              <div className="text-xs text-muted-foreground">
                                Repo: <span className="font-mono">{getSelectedFlag('low')!.repo}</span>
                              </div>
                            )}
                            {getSelectedFlag('low')!.contributor && !selectedContributor && (
                              <div className="text-xs text-muted-foreground mt-1">
                                Contributor: <span className="font-mono">{getSelectedFlag('low')!.contributor}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
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
