"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { useTheme } from "@/contexts/theme-context";
import { Contributor } from "@/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
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
  Key,
  Copy,
  Calendar,
  ExternalLink,
  Loader2,
  BarChart3,
  Linkedin,
  Twitter,
  Globe
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

const DASHBOARD_STATE_KEY = "dashboard-state";

interface DashboardState {
  rangeDays: number | null;
  selectedContributor: string | null;
  isCustomRange: boolean;
}

export default function DashboardPage() {
  // Initialize state from localStorage or defaults
  const [rangeDays, setRangeDays] = useState<number | null>(() => {
    if (typeof window === "undefined") return 7;
    try {
      const saved = localStorage.getItem(DASHBOARD_STATE_KEY);
      if (saved) {
        const state: DashboardState = JSON.parse(saved);
        // Explicitly preserve null for "all-time" selection
        // Check if rangeDays exists in the state (even if null)
        if ('rangeDays' in state) {
          return state.rangeDays;
        }
      }
    } catch (e) {
      // Ignore parse errors
    }
    return 7;
  });
  
  const [copied, setCopied] = useState(false);
  
  const [selectedContributor, setSelectedContributor] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const saved = localStorage.getItem(DASHBOARD_STATE_KEY);
      if (saved) {
        const state: DashboardState = JSON.parse(saved);
        return state.selectedContributor ?? null;
      }
    } catch (e) {
      // Ignore parse errors
    }
    return null;
  });
  
  const [selectedHighFlag, setSelectedHighFlag] = useState<string | null>(null);
  const [selectedMediumFlag, setSelectedMediumFlag] = useState<string | null>(null);
  const [selectedLowFlag, setSelectedLowFlag] = useState<string | null>(null);
  const [isCustomDateOpen, setIsCustomDateOpen] = useState(false);
  const [customDaysInput, setCustomDaysInput] = useState<string>("");
  
  const [isCustomRange, setIsCustomRange] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    try {
      const saved = localStorage.getItem(DASHBOARD_STATE_KEY);
      if (saved) {
        const state: DashboardState = JSON.parse(saved);
        return state.isCustomRange ?? false;
      }
    } catch (e) {
      // Ignore parse errors
    }
    return false;
  });
  
  const [dismissedPatPrompt, setDismissedPatPrompt] = useState(false);
  const customDatePopupRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { accentColor } = useTheme();
  const router = useRouter();

  // Save dashboard state to localStorage whenever it changes
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const state: DashboardState = {
        rangeDays,
        selectedContributor,
        isCustomRange,
      };
      localStorage.setItem(DASHBOARD_STATE_KEY, JSON.stringify(state));
    } catch (e) {
      // Ignore storage errors (e.g., quota exceeded)
      console.warn("Failed to save dashboard state to localStorage:", e);
    }
  }, [rangeDays, selectedContributor, isCustomRange]);

  const { data: authStatus, isLoading: isLoadingAuth, isSuccess: isAuthStatusSuccess } = useQuery({
    queryKey: ["auth-status"],
    queryFn: () => api.getAuthStatus(),
  });

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

  const handleCustomDateRange = () => {
    if (customDaysInput.trim()) {
      // Parse input like "60d", "120d", "360d" or just "60", "120", "360"
      const input = customDaysInput.trim().toLowerCase();
      const match = input.match(/^(\d+)\s*d\s*$/i) || input.match(/^(\d+)$/);
      
      if (match) {
        const days = parseInt(match[1], 10);
        if (days > 0) {
          setRangeDays(days);
          setIsCustomRange(true);
          setIsCustomDateOpen(false);
          setCustomDaysInput("");
        }
      }
    }
  };

  const handlePresetRange = (days: number | null) => {
    setRangeDays(days);
    setIsCustomRange(false);
    setCustomDaysInput("");
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

  // Helper function to truncate text to 15 words
  const truncateTo15Words = (text: string): string => {
    const words = text.trim().split(/\s+/);
    if (words.length <= 15) return text;
    return words.slice(0, 15).join(' ') + '...';
  };

  // Helper function to extract repo name from full path
  const getRepoName = (repo?: string): string => {
    if (!repo) return 'N/A';
    if (repo.includes('/')) {
      return repo.split('/').pop() || repo;
    }
    return repo;
  };

  const topContributor = dashboardData?.contributors
    ?.sort((a, b) => b.average_trend - a.average_trend)[0];

  const top3Contributors = useMemo(() => {
    if (!dashboardData?.contributors) return [];
    return [...dashboardData.contributors]
      .sort((a, b) => b.commits - a.commits)
      .slice(0, 4);
  }, [dashboardData?.contributors]);

  const selectedContributorData = useMemo((): Contributor | null => {
    if (!selectedContributor || !dashboardData?.contributors) return null;
    const contributor = dashboardData.contributors.find(c => c.login === selectedContributor);
    if (!contributor) return null;
    // Type assertion to ensure all optional properties are available
    return contributor as Contributor;
  }, [selectedContributor, dashboardData?.contributors]);

  const sortedContributors = useMemo(() => {
    if (!dashboardData?.contributors) return [];
    return [...dashboardData.contributors].sort((a, b) => b.average_trend - a.average_trend);
  }, [dashboardData?.contributors]);

  // Computed metrics that switch between team and individual contributor data
  const displayMetrics = useMemo(() => {
    if (selectedContributorData) {
      // Use internal_external_split from dailyCommitsData for accurate individual contributor split
      const split = dailyCommitsData?.internal_external_split || [];
      const internalData = split.find(s => s.category === "Internal");
      const externalData = split.find(s => s.category === "External");
      const totalCommits = (internalData?.count || 0) + (externalData?.count || 0);
      
      const internalPercentage = totalCommits > 0 
        ? ((internalData?.count || 0) / totalCommits) * 100 
        : 0;
      const externalPercentage = totalCommits > 0 
        ? ((externalData?.count || 0) / totalCommits) * 100 
        : 0;
      
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
  }, [selectedContributorData, dashboardData, dailyCommitsData]);

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

  // Close custom date popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        customDatePopupRef.current &&
        !customDatePopupRef.current.contains(event.target as Node)
      ) {
        setIsCustomDateOpen(false);
      }
    };

    if (isCustomDateOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isCustomDateOpen]);

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
    
    // Create maps of existing dates for commits, internal, and external
    const commitMap = new Map(
      commits.map(c => [c.date, c.commits])
    );
    const internalMap = new Map(
      commits.map(c => [c.date, c.internal || 0])
    );
    const externalMap = new Map(
      commits.map(c => [c.date, c.external || 0])
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
    const filledData: Array<{ date: string; commits: number; internal: number; external: number }> = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      filledData.push({
        date: dateStr,
        commits: commitMap.get(dateStr) || 0,
        internal: internalMap.get(dateStr) || 0,
        external: externalMap.get(dateStr) || 0
      });
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return filledData;
  }, [dailyCommitsData, rangeDays]);

  // Check if selected contributor has commits in the selected time period
  const hasSelectedContributorCommits = useMemo(() => {
    if (!selectedContributor) return true; // Show top contributors if none selected
    if (!processedDailyCommits || processedDailyCommits.length === 0) return false;
    // Check if there are any commits greater than 0
    return processedDailyCommits.some(day => day.commits > 0);
  }, [selectedContributor, processedDailyCommits]);

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
    
    // Separate internal and external repos
    const internalRepos = dailyCommitsData.repo_contributions.filter(r => r.type === 'internal');
    const externalRepos = dailyCommitsData.repo_contributions.filter(r => r.type === 'external');
    
    // Get total external commits from repo_contributions
    const externalCommitsFromRepos = externalRepos.reduce((sum, repo) => sum + repo.value, 0);
    
    // Also check internal_external_split to get the complete external commit count
    // This includes external commits to tracked repos that aren't in repo_contributions
    const internalExternalSplit = dailyCommitsData?.internal_external_split || [];
    const externalData = internalExternalSplit.find(s => s.category === "External");
    const totalExternalCommits = externalData?.count || externalCommitsFromRepos;
    
    // Get accent color HSL values
    const baseHsl = getAccentColorHsl();
    const baseHue = parseInt(baseHsl.split(' ')[0]);
    const baseSaturation = parseInt(baseHsl.split(' ')[1].replace('%', ''));
    const baseLightness = baseHsl.split(' ')[2];
    
    // Sort internal repos by value (commit count) descending
    const sortedInternal = [...internalRepos].sort((a, b) => b.value - a.value);
    
    // Add color information to internal repos
    const coloredInternal = sortedInternal.map((entry, index) => {
      const totalRepos = sortedInternal.length;
      if (totalRepos === 1) {
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
        hue: baseHue,
        saturation: `${Math.round(saturation)}%`,
        lightness: baseLightness,
      };
    });
    
    // Add aggregated External entry with grey color
    // Always include External category if there are any external commits
    const result = [...coloredInternal];
    if (totalExternalCommits > 0) {
      result.push({
        name: "External",
        value: totalExternalCommits,
        type: "external" as const,
        hue: 0, // Grey hue
        saturation: "0%", // No saturation for grey
        lightness: "50%", // Medium grey
      });
    }
    
    // Sort by value descending (External will be included in sort)
    return result.sort((a, b) => b.value - a.value);
  }, [dailyCommitsData, accentColor]);

  const shouldShowPatPrompt = useMemo(() => {
    // Don't show if user dismissed it
    if (dismissedPatPrompt) return false;
    // Wait for auth status to finish loading
    if (isLoadingAuth) return false;
    // Only show if query succeeded and we have a response
    if (isAuthStatusSuccess && authStatus) {
      return !authStatus.configured;
    }
    // Don't show if query hasn't completed yet or failed
    return false;
  }, [authStatus, dismissedPatPrompt, isLoadingAuth, isAuthStatusSuccess]);

  if (isLoading) {
    return (
      <div className="flex h-screen bg-background">
        <Navigation />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <div className="space-y-4 sm:space-y-6">
              <div className="h-10 sm:h-12 bg-[hsl(0_0%_8%)] rounded-lg animate-pulse" />
              <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
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
    <>
      {shouldShowPatPrompt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="max-w-lg w-full px-4">
            <Card className="glass-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  Welcome to RealDevs
                </CardTitle>
                <CardDescription>
                  To unlock the full dashboard, connect a GitHub Personal Access Token (PAT).
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3 text-sm text-muted-foreground">
                  <p className="font-semibold text-foreground">
                    You can either:
                  </p>
                  <div className="space-y-2">
                    <p>
                      <span className="font-semibold text-foreground">Configure a PAT now</span> for full analytics and automatic syncing, or
                    </p>
                    <p>
                      <span className="font-semibold text-foreground">Continue without a PAT</span> with limited GitHub rate limits — you&apos;ll need to manually add users by GitHub username in <span className="font-semibold text-foreground">Settings → Credentials</span>.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:justify-end pt-2">
                  <Button
                    variant="ghost"
                    className="sm:flex-1"
                    onClick={() => setDismissedPatPrompt(true)}
                  >
                    Continue without PAT
                  </Button>
                  <Button
                    className="sm:flex-1"
                    onClick={() => router.push("/credentials")}
                  >
                    Configure PAT
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      <div className="flex h-screen bg-background">
        <Navigation />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
          {/* Header with Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 sm:mb-8">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold accent-text mb-2">Dashboard</h1>
              <p className="text-sm sm:text-base text-muted-foreground">
                Your Team's Productivity at a Glance
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4 w-full sm:w-auto">
              {/* Date Range Selector */}
              <div className="relative flex items-center justify-center gap-1 sm:gap-2 bg-[hsl(0_0%_8%)] rounded-lg p-1 flex-wrap">
                <Button
                  variant={rangeDays === 7 && !isCustomRange ? "default" : "ghost"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => handlePresetRange(7)}
                >
                  7d
                </Button>
                <Button
                  variant={rangeDays === 14 && !isCustomRange ? "default" : "ghost"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => handlePresetRange(14)}
                >
                  14d
                </Button>
                <Button
                  variant={rangeDays === 30 && !isCustomRange ? "default" : "ghost"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => handlePresetRange(30)}
                >
                  30d
                </Button>
                <Button
                  variant={rangeDays === null && !isCustomRange ? "default" : "ghost"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => handlePresetRange(null)}
                >
                  All
                </Button>
                <Button
                  variant={isCustomRange ? "default" : "ghost"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => setIsCustomDateOpen(!isCustomDateOpen)}
                >
                  <Calendar className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-1" />
                  <span className="hidden sm:inline">Custom</span>
                </Button>
                
                {/* Custom Date Range Popup */}
                {isCustomDateOpen && (
                  <div 
                    ref={customDatePopupRef}
                    className="absolute top-full right-0 mt-2 z-50 glass-card border border-border rounded-lg shadow-lg p-3 sm:p-4 min-w-[240px] sm:min-w-[280px] max-w-[calc(100vw-2rem)]"
                  >
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs sm:text-sm font-medium mb-1 block accent-text">
                          Days from Today
                        </label>
                        <Input
                          type="text"
                          value={customDaysInput}
                          onChange={(e) => setCustomDaysInput(e.target.value)}
                          placeholder="e.g., 60d, 120d, 360d"
                          className="bg-background font-mono text-sm"
                          onKeyPress={(e) => {
                            if (e.key === "Enter") {
                              handleCustomDateRange();
                            }
                          }}
                        />
                        <p className="text-[10px] sm:text-xs text-muted-foreground mt-1">
                          Enter number of days (e.g., 60d or 60)
                        </p>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Button
                          size="sm"
                          onClick={handleCustomDateRange}
                          disabled={!customDaysInput.trim()}
                          className="flex-1 text-sm"
                        >
                          Apply
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setIsCustomDateOpen(false);
                            setCustomDaysInput("");
                          }}
                          className="text-sm"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Sync Button */}
              <Button
                onClick={() => syncMutation.mutate()}
                disabled={syncMutation.isPending}
                className="w-full sm:w-auto text-sm"
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
            <div className="mb-4 sm:mb-6 text-xs sm:text-sm text-muted-foreground flex items-center gap-2">
              <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="truncate">Last synced: {new Date(dashboardData.last_synced).toLocaleString()}</span>
            </div>
          )}

          {/* 4 Key Metric Cards */}
          <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 mb-6 sm:mb-8">
            {/* Total Code Commitment Trend */}
            <Card className="glass-card flex flex-col h-full w-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm sm:text-base font-medium text-white">
                  {selectedContributor ? `${selectedContributor}'s Commits` : "Total Code Commitment"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <div className="text-2xl sm:text-3xl font-bold accent-text mb-1">
                  {displayMetrics.totalCommits}
                </div>
                <p className="text-xs sm:text-sm text-white mb-3">Commits</p>
                {processedDailyCommits && processedDailyCommits.length > 0 ? (
                  <div className="flex-1 min-h-[108px]">
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
                  <div className="flex-1 min-h-[108px] flex items-center justify-center">
                    <div className="text-center">
                      <Minus className="w-6 h-6 mx-auto mb-1 opacity-50 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground">No trend data</p>
                    </div>
                  </div>
                )}
                <div className="mt-3 flex items-center gap-2">
                  <span className={getTrendIconColor(displayMetrics.averageTrend)}>
                    {getTrendIcon(displayMetrics.averageTrend, "w-3 h-3 sm:w-4 sm:h-4")}
                  </span>
                  <span className="text-xs sm:text-sm text-white">
                    Average Trend: {formatAverageTrend(displayMetrics.averageTrend)}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Internal vs External Split */}
            <Card className="glass-card flex flex-col w-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm sm:text-base font-medium text-white">
                  {selectedContributor ? "Contributor Type" : "Contribution Split"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <div className="flex-1 min-h-[100px] sm:min-h-[108px] flex items-center justify-center mb-3">
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
                            backgroundColor: 'black', 
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px',
                            padding: '8px 12px'
                          }}
                          content={({ active, payload }) => {
                            if (active && payload && payload.length > 0) {
                              const value = payload[0].value as number;
                              
                              return (
                                <div
                                  style={{
                                    backgroundColor: 'black',
                                    color: 'white',
                                    fontSize: '12px',
                                    fontWeight: 'bold',
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    border: '1px solid hsl(var(--border))',
                                  }}
                                >
                                  {`${value.toFixed(1)}%`}
                                </div>
                              );
                            }
                            return null;
                          }}
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
                    <span className="text-sm sm:text-base text-white">Internal</span>
                    <span className="text-base sm:text-lg font-bold accent-text">
                      {displayMetrics.internalPercentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm sm:text-base text-white">External</span>
                    <span className="text-base sm:text-lg font-bold">
                      {displayMetrics.externalPercentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Contributor / Selected Contributor */}
            <Card className="glass-card flex flex-col h-full w-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm sm:text-base font-medium text-white">
                  {selectedContributor ? "Selected Contributor" : "Top Contributors"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                {selectedContributorData && hasSelectedContributorCommits ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {selectedContributorData?.avatar_url ? (
                        <img 
                          src={selectedContributorData.avatar_url} 
                          alt={selectedContributorData.login}
                          className="w-8 h-8 rounded-full"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                          <Users className="w-4 h-4" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold truncate">{selectedContributorData.login}</div>
                        <div className="text-xs text-muted-foreground">
                          {selectedContributorData.is_internal ? "Internal" : "External"}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={getTrendIconColor(selectedContributorData?.average_trend)}>
                        {getTrendIcon(selectedContributorData?.average_trend, "w-5 h-5")}
                      </span>
                      <div className="text-lg font-bold accent-text">
                        {formatAverageTrend(selectedContributorData?.average_trend)}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">Average Trend</p>
                  </div>
                ) : selectedContributorData && !hasSelectedContributorCommits ? (
                  null
                ) : !selectedContributorData && top3Contributors.length > 0 ? (
                  <div className="space-y-3">
                    {top3Contributors.map((contributor, index) => (
                      <div key={contributor.login} className="space-y-1">
                        {/* Row 1: Avatar, Name, Type, Trend */}
                        <div className="flex items-center gap-2 flex-wrap">
                          {contributor.avatar_url ? (
                            <img 
                              src={contributor.avatar_url} 
                              alt={contributor.login}
                              className="w-6 h-6 rounded-full"
                            />
                          ) : (
                            <div className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center">
                              <Users className="w-3 h-3" />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-xs sm:text-sm truncate">{contributor.login}</div>
                          </div>
                          <Badge 
                            variant={contributor.is_internal ? "default" : "secondary"} 
                            className="text-[10px] sm:text-xs px-1 sm:px-1.5 py-0 shrink-0"
                          >
                            {contributor.is_internal ? "Internal" : "External"}
                          </Badge>
                          <div className="flex items-center gap-1 shrink-0">
                            <span className={getTrendIconColor(contributor?.average_trend)}>
                              {getTrendIcon(contributor?.average_trend, "w-3 h-3 sm:w-4 sm:h-4")}
                            </span>
                            <span className="text-xs sm:text-sm font-bold text-white">
                              {formatAverageTrend(contributor?.average_trend)}
                            </span>
                          </div>
                        </div>
                        {/* Row 2: Total Contribution */}
                        <div className="flex items-center gap-2 pl-6 sm:pl-8 flex-wrap">
                          <span className="text-[10px] sm:text-xs text-muted-foreground">Total Contribution:</span>
                          <span className="text-xs sm:text-sm font-semibold text-white">{contributor.commits} commits</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-muted-foreground text-sm">No contributors yet</div>
                )}
              </CardContent>
            </Card>

            {/* Risk Flags Counter */}
            <Card className="glass-card flex flex-col h-full w-full min-w-0">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm sm:text-base font-medium text-white">
                  {selectedContributor ? `${selectedContributor}'s Risk Flags` : "Risk Flags"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                {/* Total and badges on same row */}
                <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                  <div className="text-2xl sm:text-3xl font-bold accent-text">
                    {displayRiskFlags.length}
                  </div>
                  <div className="flex gap-1 flex-wrap">
                    {displayRiskFlags.filter(f => f.severity === "high").length > 0 && (
                      <Badge variant="destructive" className="text-[10px] sm:text-xs">
                        {displayRiskFlags.filter(f => f.severity === "high").length} High
                      </Badge>
                    )}
                    {displayRiskFlags.filter(f => f.severity === "medium").length > 0 && (
                      <Badge variant="default" className="text-[10px] sm:text-xs">
                        {displayRiskFlags.filter(f => f.severity === "medium").length} Med
                      </Badge>
                    )}
                    {displayRiskFlags.filter(f => f.severity === "low").length > 0 && (
                      <Badge variant="secondary" className="text-[10px] sm:text-xs">
                        {displayRiskFlags.filter(f => f.severity === "low").length} Low
                      </Badge>
                    )}
                    {displayRiskFlags.length === 0 && selectedContributor && (
                      <span className="text-xs text-muted-foreground">No flags</span>
                    )}
                  </div>
                </div>
                {/* Preview section with fixed height - one preview per category */}
                {displayRiskFlags.length > 0 && (
                  <div className="space-y-1.5 mt-2" style={{ height: '180px' }}>
                    {/* High priority preview */}
                    {riskFlagsBySeverity.high.length > 0 && (
                      <div className="p-2 rounded-lg border border-red-500/30 bg-red-500/10 h-[56px] flex flex-col justify-between">
                        <div className="flex items-center gap-1.5">
                          <Badge variant="destructive" className="text-xs px-1.5 py-0">High</Badge>
                          <span className="text-xs text-white truncate font-medium">
                            {getRepoName(getSelectedFlag('high')?.repo)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-1 leading-tight">
                          {getSelectedFlag('high')?.description ? truncateTo15Words(getSelectedFlag('high')!.description) : ''}
                        </p>
                      </div>
                    )}
                    {/* Medium priority preview */}
                    {riskFlagsBySeverity.medium.length > 0 && (
                      <div className="p-2 rounded-lg border border-border bg-[hsl(0_0%_8%)] h-[56px] flex flex-col justify-between">
                        <div className="flex items-center gap-1.5">
                          <Badge variant="default" className="text-xs px-1.5 py-0">Medium</Badge>
                          <span className="text-xs text-white truncate font-medium">
                            {getRepoName(getSelectedFlag('medium')?.repo)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-1 leading-tight">
                          {getSelectedFlag('medium')?.description ? truncateTo15Words(getSelectedFlag('medium')!.description) : ''}
                        </p>
                      </div>
                    )}
                    {/* Low priority preview */}
                    {riskFlagsBySeverity.low.length > 0 && (
                      <div className="p-2 rounded-lg border border-border bg-[hsl(0_0%_8%)] h-[56px] flex flex-col justify-between">
                        <div className="flex items-center gap-1.5">
                          <Badge variant="secondary" className="text-xs px-1.5 py-0">Low</Badge>
                          <span className="text-xs text-white truncate font-medium">
                            {getRepoName(getSelectedFlag('low')?.repo)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-1 leading-tight">
                          {getSelectedFlag('low')?.description ? truncateTo15Words(getSelectedFlag('low')!.description) : ''}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid gap-4 sm:gap-6 grid-cols-1 lg:grid-cols-2 mb-6 sm:mb-8">
            {/* Daily Commits Bar Chart */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                  <BarChart3 className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="truncate">Daily Commits</span>
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2 text-[10px] sm:text-xs shrink-0">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription className="text-xs sm:text-sm">
                  {selectedContributor 
                    ? `Individual commit activity for ${selectedContributor}` 
                    : "Team commit activity over time"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {processedDailyCommits && processedDailyCommits.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={processedDailyCommits}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="date" 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          date.setDate(date.getDate() + 1);
                          return `${date.getMonth() + 1}/${date.getDate()}`;
                        }}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))"
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                        width={40}
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
                      <Bar 
                        dataKey="internal" 
                        fill={`hsl(${getAccentColorHsl()})`} 
                        name="Internal" 
                        stackId="commits"
                        shape={(props: any) => {
                          const { x, y, width, height, payload } = props;
                          // Check if there's external data for this day
                          const hasExternal = payload && payload.external > 0;
                          const r = 4; // corner radius
                          
                          if (hasExternal) {
                            // Only round bottom corners when external data exists
                            return (
                              <path
                                d={`M ${x},${y} 
                                   L ${x + width},${y} 
                                   L ${x + width},${y + height - r} 
                                   Q ${x + width},${y + height} ${x + width - r},${y + height} 
                                   L ${x + r},${y + height} 
                                   Q ${x},${y + height} ${x},${y + height - r} 
                                   Z`}
                                fill={props.fill}
                              />
                            );
                          } else {
                            // Round all corners when no external data
                            return (
                              <rect
                                x={x}
                                y={y}
                                width={width}
                                height={height}
                                rx={r}
                                ry={r}
                                fill={props.fill}
                              />
                            );
                          }
                        }}
                      />
                      <Bar 
                        dataKey="external" 
                        fill="hsl(0 0% 50%)" 
                        name="External" 
                        stackId="commits"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[270px] flex items-center justify-center text-muted-foreground">
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
                <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                  <Users className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="truncate">Contribution Split</span>
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2 text-[10px] sm:text-xs shrink-0">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription className="text-xs sm:text-sm">
                  {selectedContributor 
                    ? `${selectedContributor}'s contributions by repository` 
                    : "Team contributions broken down by repository"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {sortedRepoContributions && sortedRepoContributions.length > 0 ? (
                  <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
                    <div className="shrink-0" style={{ width: '100%', maxWidth: '200px', height: 180 }}>
                      <PieChart width={200} height={180}>
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
                            innerRadius={40}
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
                                // Handle "External" category specially, otherwise extract repo name
                                const displayName = repoName === "External" 
                                  ? "External" 
                                  : repoName.includes('/') 
                                    ? repoName.split('/')[1] 
                                    : repoName;
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
                    <div className="flex-1 w-full sm:w-auto space-y-2 max-h-[300px] overflow-y-auto">
                      {sortedRepoContributions.map((entry, index) => {
                        const color = `hsl(${entry.hue} ${entry.saturation} ${entry.lightness})`;
                        // Handle "External" category specially, otherwise extract repo name
                        const displayName = entry.name === "External"
                          ? "External"
                          : entry.name.includes('/') 
                            ? entry.name.split('/')[1] 
                            : entry.name;
                        
                        return (
                          <div key={index} className="flex items-center justify-between p-2 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <div 
                                className="w-3 h-3 rounded-full shrink-0" 
                                style={{ backgroundColor: color }}
                              />
                              <span className="text-xs sm:text-sm truncate">
                                {displayName}
                              </span>
                            </div>
                            <span className="text-xs sm:text-sm font-semibold accent-text ml-2 shrink-0">
                              {entry.value}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="h-[270px] flex items-center justify-center text-muted-foreground">
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
          <Card className="glass-card mb-6 sm:mb-8">
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5" />
                    Contributors
                  </CardTitle>
                  <CardDescription className="text-xs sm:text-sm">
                    {selectedContributor ? "Individual contributor details" : "Top contributors sorted by average trend"}
                  </CardDescription>
                </div>
                <div className="w-full sm:w-64">
                  <Select 
                    value={selectedContributor || "all"} 
                    onValueChange={(value) => setSelectedContributor(value === "all" ? null : value)}
                  >
                    <SelectTrigger className="text-sm">
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
                  <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                    {selectedContributorData.avatar_url ? (
                      <img 
                        src={selectedContributorData.avatar_url} 
                        alt={selectedContributorData.login}
                        className="w-16 h-16 rounded-full shrink-0"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center shrink-0">
                        <Users className="w-8 h-8" />
                      </div>
                    )}
                    <div className="flex-1 w-full text-center sm:text-left">
                      <h3 className="text-xl sm:text-2xl font-bold break-words">{selectedContributorData.login}</h3>
                      {selectedContributorData.name && (
                        <p className="text-sm sm:text-base text-muted-foreground break-words">{selectedContributorData.name}</p>
                      )}
                      <div className="flex flex-col sm:flex-row items-center sm:items-center gap-2 mt-2">
                        <Badge variant={selectedContributorData.is_internal ? "default" : "secondary"} className="text-xs">
                          {selectedContributorData.is_internal ? "Internal" : "External"}
                        </Badge>
                        <div className="flex items-center gap-1 text-xs sm:text-sm text-muted-foreground">
                          <span className={getTrendIconColor(selectedContributorData?.average_trend)}>
                            {getTrendIcon(selectedContributorData?.average_trend, "w-3 h-3 sm:w-4 sm:h-4")}
                          </span>
                          <span>Average Trend: {formatAverageTrend(selectedContributorData?.average_trend)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 flex-wrap justify-center sm:justify-start">
                      <Button
                        variant="outline"
                        size="icon"
                        asChild
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
                      {selectedContributorData.linkedin_url && (
                        <Button
                          variant="outline"
                          size="icon"
                          asChild
                        >
                          <a
                            href={selectedContributorData.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label={`View ${selectedContributorData.login} on LinkedIn`}
                          >
                            <Linkedin className="w-5 h-5" />
                          </a>
                        </Button>
                      )}
                      {selectedContributorData.twitter_url && (
                        <Button
                          variant="outline"
                          size="icon"
                          asChild
                        >
                          <a
                            href={selectedContributorData.twitter_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label={`View ${selectedContributorData.login} on Twitter`}
                          >
                            <Twitter className="w-5 h-5" />
                          </a>
                        </Button>
                      )}
                      {selectedContributorData.website_url && (
                        <Button
                          variant="outline"
                          size="icon"
                          asChild
                        >
                          <a
                            href={selectedContributorData.website_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label={`Visit ${selectedContributorData.login}'s website`}
                          >
                            <Globe className="w-5 h-5" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Contributor Metrics Grid */}
                  <div className="grid gap-3 sm:gap-4 grid-cols-2 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="p-3 sm:p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <GitCommit className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground" />
                        <span className="text-xs sm:text-sm text-muted-foreground">Commits</span>
                      </div>
                      <div className="text-xl sm:text-2xl font-bold accent-text">
                        {selectedContributorData.commits}
                      </div>
                    </div>
                    
                    <div className="p-3 sm:p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <GitPullRequest className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground" />
                        <span className="text-xs sm:text-sm text-muted-foreground">PRs Opened</span>
                      </div>
                      <div className="text-xl sm:text-2xl font-bold accent-text">
                        {selectedContributorData.prs_opened}
                      </div>
                    </div>
                    
                    <div className="p-3 sm:p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground" />
                        <span className="text-xs sm:text-sm text-muted-foreground">PRs Merged</span>
                      </div>
                      <div className="text-xl sm:text-2xl font-bold accent-text">
                        {selectedContributorData.prs_merged}
                      </div>
                    </div>
                    
                    <div className="p-3 sm:p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground" />
                        <span className="text-xs sm:text-sm text-muted-foreground">Issues Closed</span>
                      </div>
                      <div className="text-xl sm:text-2xl font-bold accent-text">
                        {selectedContributorData.issues_closed}
                      </div>
                    </div>
                  </div>

                  {/* Contributor Performance Summary */}
                  <div className="p-3 sm:p-4 rounded-lg border border-border bg-[hsl(0_0%_8%)]">
                    <h4 className="font-semibold mb-3 text-sm sm:text-base">Performance Summary</h4>
                    <div className="space-y-2 text-xs sm:text-sm">
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
                          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4 p-3 rounded-lg border border-border bg-[hsl(0_0%_8%)] hover:bg-[hsl(0_0%_10%)] transition-colors"
                        >
                          <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
                            <div className="flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-primary/20 text-primary font-bold text-xs sm:text-sm shrink-0">
                              {index + 1}
                            </div>
                            {contributor.avatar_url ? (
                              <img 
                                src={contributor.avatar_url} 
                                alt={contributor.login}
                                className="w-8 h-8 sm:w-10 sm:h-10 rounded-full cursor-pointer shrink-0"
                                onClick={() => setSelectedContributor(contributor.login)}
                              />
                            ) : (
                              <div 
                                className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-secondary flex items-center justify-center cursor-pointer shrink-0"
                                onClick={() => setSelectedContributor(contributor.login)}
                              >
                                <Users className="w-4 h-4 sm:w-5 sm:h-5" />
                              </div>
                            )}
                            <div 
                              className="flex-1 min-w-0 cursor-pointer"
                              onClick={() => setSelectedContributor(contributor.login)}
                            >
                              <div className="font-semibold text-sm sm:text-base truncate">{contributor.login}</div>
                              <div className="flex items-center gap-2 text-[10px] sm:text-xs text-muted-foreground flex-wrap">
                                <span>{contributor.commits} commits</span>
                                <span>•</span>
                                <span>{contributor.prs_merged} PRs</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center justify-between sm:justify-end gap-2 sm:gap-4">
                            <Badge variant={contributor.is_internal ? "default" : "secondary"} className="text-[10px] sm:text-xs shrink-0">
                              {contributor.is_internal ? "Internal" : "External"}
                            </Badge>
                            <div className="text-right shrink-0">
                              <div className="flex items-center justify-end gap-1">
                                <span className={getTrendIconColor(contributor?.average_trend)}>
                                  {getTrendIcon(contributor?.average_trend, "w-3 h-3 sm:w-4 sm:h-4")}
                                </span>
                                <span className="font-bold accent-text text-base sm:text-lg">
                                  {formatAverageTrend(contributor?.average_trend)}
                                </span>
                              </div>
                              <div className="text-[10px] sm:text-xs text-muted-foreground">trend</div>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon"
                              asChild
                              className="shrink-0 h-8 w-8 sm:h-10 sm:w-10"
                            >
                            <a
                              href={`https://github.com/${contributor.login}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              aria-label={`View ${contributor.login} on GitHub`}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <GitHubIcon className="w-4 h-4 sm:w-5 sm:h-5" />
                            </a>
                            </Button>
                          </div>
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

          <div className="grid gap-4 sm:gap-6 grid-cols-1 lg:grid-cols-2 mb-6 sm:mb-8">
            {/* Risk Flags Section */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                  <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="truncate">Risk Flags</span>
                  {selectedContributor && (
                    <Badge variant="secondary" className="ml-2 text-[10px] sm:text-xs shrink-0">
                      {selectedContributor}
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription className="text-xs sm:text-sm">
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
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
                  <div>
                    <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                      <Calendar className="w-4 h-4 sm:w-5 sm:h-5" />
                      Weekly Recap
                    </CardTitle>
                    <CardDescription className="text-xs sm:text-sm">
                      Auto-generated team summary
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyReport}
                    disabled={!weeklyReport?.text}
                    className="w-full sm:w-auto text-sm"
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
                  <div className="space-y-3 text-xs sm:text-sm text-muted-foreground">
                    {weeklyReport.text
                      .trim()
                      .split(/\n{2,}/)
                      .map((block, index) => (
                        <p
                          key={index}
                          className="whitespace-pre-wrap leading-relaxed"
                        >
                          {block.trim()}
                        </p>
                      ))}
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
    </>
  );
}
