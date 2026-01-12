"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Settings as SettingsIcon, Save, RotateCcw, AlertTriangle, TrendingUp } from "lucide-react";
import { ThemeSelectorCard } from "@/components/theme-selector";

interface SettingItem {
  key: string;
  label: string;
  description: string;
  defaultValue: number;
  min: number;
  max: number;
  unit?: string;
}

const THRESHOLD_SETTINGS: SettingItem[] = [
  {
    key: "threshold_no_activity_days",
    label: "No Activity Threshold",
    description: "Days without commits before flagging as inactive",
    defaultValue: 3,
    min: 1,
    max: 30,
    unit: "days"
  },
  {
    key: "threshold_stale_pr_days",
    label: "Stale PR Threshold",
    description: "Days before an open PR is considered stale",
    defaultValue: 7,
    min: 1,
    max: 60,
    unit: "days"
  },
  {
    key: "threshold_single_contributor_pct",
    label: "Single Contributor Risk %",
    description: "Percentage of work by one person before flagging",
    defaultValue: 70,
    min: 50,
    max: 95,
    unit: "%"
  },
];

const WEIGHT_SETTINGS: SettingItem[] = [
  {
    key: "weight_commits",
    label: "Commits Weight",
    description: "Weight for commits in average trend calculation",
    defaultValue: 1.0,
    min: 0,
    max: 5,
  },
  {
    key: "weight_prs_opened",
    label: "PRs Opened Weight",
    description: "Weight for opened PRs in average trend calculation",
    defaultValue: 1.5,
    min: 0,
    max: 5,
  },
  {
    key: "weight_prs_merged",
    label: "PRs Merged Weight",
    description: "Weight for merged PRs in average trend calculation",
    defaultValue: 2.0,
    min: 0,
    max: 5,
  },
  {
    key: "weight_issues_closed",
    label: "Issues Closed Weight",
    description: "Weight for closed issues in average trend calculation",
    defaultValue: 1.0,
    min: 0,
    max: 5,
  },
];

export default function SettingsPage() {
  const [values, setValues] = useState<Record<string, number>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: () => api.getSettings(),
  });

  const updateMutation = useMutation({
    mutationFn: async (updates: Record<string, number>) => {
      // Update all settings
      for (const [key, value] of Object.entries(updates)) {
        await api.updateSetting(key, value.toString());
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setHasChanges(false);
    },
  });

  // Initialize values from server
  useEffect(() => {
    if (settings?.settings) {
      const newValues: Record<string, number> = {};
      
      [...THRESHOLD_SETTINGS, ...WEIGHT_SETTINGS].forEach((setting) => {
        const value = settings.settings[setting.key];
        newValues[setting.key] = value ? parseFloat(value) : setting.defaultValue;
      });
      
      setValues(newValues);
    }
  }, [settings]);

  const handleChange = (key: string, value: number) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleIncrement = (key: string, setting: SettingItem) => {
    const current = values[key] || setting.defaultValue;
    const step = setting.unit === "%" || setting.key.startsWith("weight") ? 1 : 1;
    const newValue = Math.min(current + step, setting.max);
    handleChange(key, newValue);
  };

  const handleDecrement = (key: string, setting: SettingItem) => {
    const current = values[key] || setting.defaultValue;
    const step = setting.unit === "%" || setting.key.startsWith("weight") ? 1 : 1;
    const newValue = Math.max(current - step, setting.min);
    handleChange(key, newValue);
  };

  const handleReset = () => {
    const defaults: Record<string, number> = {};
    [...THRESHOLD_SETTINGS, ...WEIGHT_SETTINGS].forEach((setting) => {
      defaults[setting.key] = setting.defaultValue;
    });
    setValues(defaults);
    setHasChanges(true);
  };

  const handleSave = () => {
    updateMutation.mutate(values);
  };

  const renderSettingControl = (setting: SettingItem) => {
    const value = values[setting.key] ?? setting.defaultValue;

    return (
      <div key={setting.key} className="p-4 rounded-lg bg-[hsl(0_0%_8%)] border border-border">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h4 className="font-semibold mb-1">{setting.label}</h4>
            <p className="text-sm text-muted-foreground">{setting.description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="icon"
            onClick={() => handleDecrement(setting.key, setting)}
            disabled={value <= setting.min}
          >
            -
          </Button>
          
          <div className="flex-1 flex items-center gap-2">
            <Input
              type="number"
              value={value}
              onChange={(e) => {
                const newValue = parseFloat(e.target.value) || setting.defaultValue;
                const clamped = Math.max(setting.min, Math.min(setting.max, newValue));
                handleChange(setting.key, clamped);
              }}
              min={setting.min}
              max={setting.max}
              step={setting.key.startsWith("weight") ? 0.1 : 1}
              className="text-center font-semibold"
            />
            {setting.unit && (
              <span className="text-sm text-muted-foreground min-w-[40px]">
                {setting.unit}
              </span>
            )}
          </div>
          
          <Button
            variant="outline"
            size="icon"
            onClick={() => handleIncrement(setting.key, setting)}
            disabled={value >= setting.max}
          >
            +
          </Button>
        </div>
        
        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>Min: {setting.min}</span>
          <span>Default: {setting.defaultValue}</span>
          <span>Max: {setting.max}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Navigation />
      
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold accent-text mb-2">Settings</h1>
              <p className="text-muted-foreground">
                Configure risk thresholds and average trend calculation weights
              </p>
            </div>

            <div className="flex gap-2">
              {hasChanges && (
                <Button
                  variant="outline"
                  onClick={handleReset}
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Reset to Defaults
                </Button>
              )}
              <Button
                onClick={handleSave}
                disabled={!hasChanges || updateMutation.isPending}
              >
                <Save className="w-4 h-4 mr-2" />
                {updateMutation.isPending ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </div>

          {isLoading ? (
            <div className="space-y-6">
              <div className="h-40 bg-[hsl(0_0%_8%)] rounded-lg animate-pulse" />
              <div className="h-40 bg-[hsl(0_0%_8%)] rounded-lg animate-pulse" />
            </div>
          ) : (
            <>
              {/* Theme Selector */}
              <ThemeSelectorCard className="mb-8" />
              
              {/* Risk Flag Thresholds */}
              <Card className="glass-card mb-8">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Risk Flag Thresholds
                  </CardTitle>
                  <CardDescription>
                    Configure when alerts should be triggered based on team activity
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {THRESHOLD_SETTINGS.map(renderSettingControl)}
                </CardContent>
              </Card>

              {/* Average Trend Weights */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Average Trend Weights
                  </CardTitle>
                  <CardDescription>
                    Adjust the importance of different metrics in the average trend calculation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {WEIGHT_SETTINGS.map(renderSettingControl)}
                  
                  <div className="mt-6 p-4 rounded-lg accent-bg accent-border border">
                    <h4 className="font-semibold accent-text mb-2">How Average Trend Works</h4>
                    <p className="text-sm text-muted-foreground">
                      Daily Weighted Score = (Commits × {values.weight_commits || 1.0}) + 
                      (PRs Opened × {values.weight_prs_opened || 1.5}) + 
                      (PRs Merged × {values.weight_prs_merged || 2.0}) + 
                      (Issues Closed × {values.weight_issues_closed || 1.0})
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      The average trend is calculated using least squares regression on daily weighted scores over time.
                      A positive trend indicates increasing activity, negative indicates decreasing activity.
                      Higher weights give more importance to that metric. Merged PRs typically have the highest weight
                      as they represent completed, reviewed work.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

