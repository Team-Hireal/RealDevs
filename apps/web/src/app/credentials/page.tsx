"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { useLanguage } from "@/contexts/language-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { 
  Key, 
  CheckCircle, 
  AlertCircle, 
  Trash2, 
  UserPlus,
  Eye,
  EyeOff,
  Users,
  Github,
  Search,
  Loader2,
  Building2,
  ChevronDown,
  ChevronUp
} from "lucide-react";

export default function CredentialsPage() {
  const { t } = useLanguage();
  const [authMode, setAuthMode] = useState<"pat" | "username">("pat");
  const [pat, setPat] = useState("");
  const [username, setUsername] = useState("");
  const [showPat, setShowPat] = useState(false);
  const [newMember, setNewMember] = useState("");
  const [members, setMembers] = useState<string[]>([]);
  const [newExternalContributor, setNewExternalContributor] = useState("");
  const [externalContributors, setExternalContributors] = useState<string[]>([]);
  const [internalOrgs, setInternalOrgs] = useState<string[]>([]);
  const [internalRepos, setInternalRepos] = useState<string[]>([]);
  const [expandedOrgs, setExpandedOrgs] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();

  const { data: authStatus } = useQuery({
    queryKey: ["auth-status"],
    queryFn: () => api.getAuthStatus(),
  });

  const { data: teamMembers } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => api.getTeamMembers(),
  });

  const { data: externalContributorsData } = useQuery({
    queryKey: ["external-contributors"],
    queryFn: () => api.getExternalContributors(),
  });

  const { data: selectedRepos } = useQuery({
    queryKey: ["selected-repos"],
    queryFn: () => api.getSelectedRepos(),
    enabled: authStatus?.configured,
  });

  const { data: availableRepos } = useQuery({
    queryKey: ["available-repos"],
    queryFn: () => api.listRepos(),
    enabled: authStatus?.configured,
  });

  const { data: internalOrgsConfig } = useQuery({
    queryKey: ["internal-orgs"],
    queryFn: () => api.getInternalOrgs(),
    enabled: authStatus?.configured,
  });

  const [selectedRepoFullNames, setSelectedRepoFullNames] = useState<Set<string>>(new Set());

  const selectReposMutation = useMutation({
    mutationFn: (repoFullNames: string[]) => api.selectRepos(repoFullNames),
    onSuccess: (_, variables) => {
      // Update local state to match what was saved
      setSelectedRepoFullNames(new Set(variables));
      queryClient.invalidateQueries({ queryKey: ["selected-repos"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const [isAutoSyncing, setIsAutoSyncing] = useState(false);
  const [autoSyncStatus, setAutoSyncStatus] = useState<string>("");

  const syncMutation = useMutation({
    mutationFn: (rangeDays: number | null) => api.syncRepos(rangeDays),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["selected-repos"] });
      // Don't clear status here - let the parent handler manage it with delay
    },
    onError: (error) => {
      setIsAutoSyncing(false);
      setAutoSyncStatus(`Sync failed: ${error.message}`);
    },
  });

  const usernameMutation = useMutation({
    mutationFn: (data: { username: string }) => api.submitUsername(data.username),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ["auth-status"] });
      setUsername("");
      
      // Wait a bit for auth status to update
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setIsAutoSyncing(true);
      setAutoSyncStatus("Username validated successfully! Note: Username-only mode can only access public repositories. Please select repositories manually from the list above.");
      
      // In username-only mode, we can now list repos but user must manually select them
      // Invalidate queries to trigger repo list refresh
      queryClient.invalidateQueries({ queryKey: ["available-repos"] });
      
      setTimeout(() => {
        setIsAutoSyncing(false);
        setAutoSyncStatus("");
      }, 5000);
    },
    onError: (error: any) => {
      const errorMessage = error.message || "Failed to validate username";
      setAutoSyncStatus(`Username validation failed: ${errorMessage}`);
    },
  });

  const patMutation = useMutation({
    mutationFn: (data: { pat: string }) => api.submitPat(data.pat),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ["auth-status"] });
      setPat("");
      
      // Wait a bit for auth status to update
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setIsAutoSyncing(true);
      
      // Check if repos are selected
      const selectedReposData = await queryClient.fetchQuery({
        queryKey: ["selected-repos"],
        queryFn: () => api.getSelectedRepos(),
      });
      
      // If no repos selected, auto-select all available repos
      if (!selectedReposData?.repos || selectedReposData.repos.length === 0) {
        setAutoSyncStatus("Selecting all available repositories...");
        
        try {
          // Fetch available repos
          const availableReposData = await queryClient.fetchQuery({
            queryKey: ["available-repos"],
            queryFn: () => api.listRepos(),
          });
          
          if (availableReposData?.repos && availableReposData.repos.length > 0) {
            // Select all repos
            await api.selectRepos(availableReposData.repos.map(r => r.full_name));
            queryClient.invalidateQueries({ queryKey: ["selected-repos"] });
            setAutoSyncStatus(`Selected ${availableReposData.repos.length} repositories. Starting sync...`);
            
            // Wait a bit for repos to be saved
            await new Promise(resolve => setTimeout(resolve, 500));
          } else {
            setAutoSyncStatus("No repositories found. Please check your PAT permissions.");
            setIsAutoSyncing(false);
            return;
          }
        } catch (error) {
          console.error("Error auto-selecting repos:", error);
          setAutoSyncStatus("Failed to auto-select repositories. Please select them manually.");
          setIsAutoSyncing(false);
          return;
        }
      } else {
        setAutoSyncStatus("Starting sync for all commits and team members...");
      }
      
      // Always trigger sync for "all time" (null = all time) after PAT setup
      setAutoSyncStatus("Syncing all commits and team members (this may take a while)...");
      
      try {
        await syncMutation.mutateAsync(null); // null = all time
        setAutoSyncStatus("Initial sync completed successfully!");
      } catch (error: any) {
        setAutoSyncStatus(`Sync failed: ${error.message || "Unknown error"}`);
      } finally {
        // Keep status visible for a few seconds, then clear
        setTimeout(() => {
          setIsAutoSyncing(false);
          setAutoSyncStatus("");
        }, 5000);
      }
    },
    onError: (error: any) => {
      // Provide helpful error message
      const errorMessage = error.message || "Failed to validate PAT";
      if (errorMessage.includes("401") || errorMessage.includes("Bad credentials")) {
        setAutoSyncStatus("Invalid PAT. Please check your token and try again.");
      } else if (errorMessage.includes("403") || errorMessage.includes("Forbidden")) {
        setAutoSyncStatus("PAT lacks required permissions. Please create a new token with read-only access.");
      } else {
        setAutoSyncStatus(`PAT validation failed: ${errorMessage}`);
      }
    },
  });

  const resetMutation = useMutation({
    mutationFn: () => api.resetAll(),
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
  });

  const teamMembersMutation = useMutation({
    mutationFn: (logins: string[]) => api.updateTeamMembers(logins),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const externalContributorsMutation = useMutation({
    mutationFn: (logins: string[]) => api.updateExternalContributors(logins),
    onSuccess: async () => {
      // Refresh cached data
      queryClient.invalidateQueries({ queryKey: ["external-contributors"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });

      // Automatically trigger a sync so new external contributors are reflected in metrics
      if (authStatus?.configured) {
        try {
          // null = all time, to ensure we fetch full external contribution history
          await syncMutation.mutateAsync(null);
        } catch (error) {
          // Swallow errors here – the main update succeeded, sync is best-effort
          console.error("Error auto-syncing after external contributor update:", error);
        }
      }
    },
  });

  const internalOrgsMutation = useMutation({
    mutationFn: ({ organizations, repos }: { organizations: string[], repos: string[] }) => 
      api.updateInternalOrgs(organizations, repos),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["internal-orgs"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  // Initialize members from server
  useEffect(() => {
    if (teamMembers?.members) {
      setMembers(teamMembers.members.map(m => m.github_login));
    }
  }, [teamMembers]);

  // Initialize external contributors from server
  useEffect(() => {
    if (externalContributorsData?.contributors) {
      setExternalContributors(externalContributorsData.contributors.map((c: { github_login: string }) => c.github_login));
    }
  }, [externalContributorsData]);

  // Initialize internal organizations from server
  useEffect(() => {
    if (internalOrgsConfig) {
      setInternalOrgs(internalOrgsConfig.organizations || []);
      setInternalRepos(internalOrgsConfig.repos || []);
    }
  }, [internalOrgsConfig]);

  const handleAddMember = () => {
    if (newMember && !members.includes(newMember)) {
      const updated = [...members, newMember];
      setMembers(updated);
      setNewMember("");
      teamMembersMutation.mutate(updated);
    }
  };

  const handleRemoveMember = (login: string) => {
    const updated = members.filter(m => m !== login);
    setMembers(updated);
    teamMembersMutation.mutate(updated);
  };

  const handleAddExternalContributor = () => {
    if (newExternalContributor && !externalContributors.includes(newExternalContributor)) {
      const updated = [...externalContributors, newExternalContributor];
      setExternalContributors(updated);
      setNewExternalContributor("");
      externalContributorsMutation.mutate(updated);
    }
  };

  const handleRemoveExternalContributor = (login: string) => {
    const updated = externalContributors.filter(c => c !== login);
    setExternalContributors(updated);
    externalContributorsMutation.mutate(updated);
  };

  const handleToggleRepo = (fullName: string) => {
    const updated = new Set(selectedRepoFullNames);
    if (updated.has(fullName)) {
      updated.delete(fullName);
    } else {
      updated.add(fullName);
    }
    setSelectedRepoFullNames(updated);
  };

  const handleSelectAllRepos = () => {
    if (availableRepos?.repos) {
      const allRepoNames = new Set(availableRepos.repos.map(r => r.full_name));
      setSelectedRepoFullNames(allRepoNames);
    }
  };

  const handleDeselectAllRepos = () => {
    setSelectedRepoFullNames(new Set());
  };

  const handleSaveRepos = () => {
    selectReposMutation.mutate(Array.from(selectedRepoFullNames));
  };

  const handleToggleOrg = (org: string) => {
    const updated = [...internalOrgs];
    const index = updated.indexOf(org);
    if (index >= 0) {
      updated.splice(index, 1);
      // Also remove all repos from this org
      const updatedRepos = internalRepos.filter(r => !r.startsWith(`${org}/`));
      setInternalRepos(updatedRepos);
    } else {
      updated.push(org);
    }
    setInternalOrgs(updated);
  };

  const handleToggleInternalRepo = (repoFullName: string) => {
    const updated = [...internalRepos];
    const index = updated.indexOf(repoFullName);
    if (index >= 0) {
      updated.splice(index, 1);
    } else {
      updated.push(repoFullName);
    }
    setInternalRepos(updated);
  };

  const handleSelectAllOrgRepos = (org: string) => {
    const orgRepos = reposByOrg[org] || [];
    const orgRepoFullNames = orgRepos.map(r => r.full_name);
    const updated = [...new Set([...internalRepos, ...orgRepoFullNames])];
    setInternalRepos(updated);
  };

  const handleDeselectAllOrgRepos = (org: string) => {
    const orgRepos = reposByOrg[org] || [];
    const orgRepoFullNames = new Set(orgRepos.map(r => r.full_name));
    const updated = internalRepos.filter(r => !orgRepoFullNames.has(r));
    setInternalRepos(updated);
  };

  const handleSaveInternalOrgs = () => {
    internalOrgsMutation.mutate({ organizations: internalOrgs, repos: internalRepos });
  };

  const toggleOrgExpansion = (org: string) => {
    const updated = new Set(expandedOrgs);
    if (updated.has(org)) {
      updated.delete(org);
    } else {
      updated.add(org);
    }
    setExpandedOrgs(updated);
  };

  // Extract unique organizations from available repos
  const uniqueOrgs = availableRepos 
    ? Array.from(new Set(availableRepos.repos.map(r => r.owner))).sort()
    : [];

  // Group repos by organization
  const reposByOrg = availableRepos 
    ? availableRepos.repos.reduce((acc, repo) => {
        if (!acc[repo.owner]) acc[repo.owner] = [];
        acc[repo.owner].push(repo);
        return acc;
      }, {} as Record<string, typeof availableRepos.repos>)
    : {};

  // Update selected repos when data loads from server (initial load only)
  useEffect(() => {
    if (selectedRepos?.repos && selectedRepoFullNames.size === 0) {
      setSelectedRepoFullNames(new Set(selectedRepos.repos.map(r => r.full_name)));
    }
  }, [selectedRepos]);

  return (
    <div className="flex h-screen bg-background">
      <Navigation />
      
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold accent-text mb-2">Credentials</h1>
          <p className="text-muted-foreground mb-8">
            Configure your GitHub access and manage team members
          </p>

          {/* 2-column layout (PAT on left, Internal/External + members + external contributors on right) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-1 lg:gap-1 items-start">
            {/* Left column: PAT only */}
            <div className="space-y-8 lg:space-y-0 lg:pr-4">
          {/* GitHub PAT Configuration */}
              <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="w-5 h-5" />
                {t.credentials.githubPat}
              </CardTitle>
              <CardDescription>
                {t.credentials.githubPatDescription}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {authStatus?.configured ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 rounded-lg accent-bg accent-border border">
                    <CheckCircle className="w-5 h-5 accent-text" />
                    <div className="flex-1">
                      <div className="font-semibold accent-text">{t.credentials.patConfigured}</div>
                      <div className="text-sm text-muted-foreground">
                        {t.credentials.authenticatedAs} <span className="font-mono">{authStatus.user?.login}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold">{t.credentials.selectedRepositories}</h4>
                        {availableRepos && availableRepos.repos.length > 0 && (
                          <div className="flex gap-2">
                            {selectedRepoFullNames.size < availableRepos.repos.length ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleSelectAllRepos}
                                className="text-xs"
                              >
                                {t.common.select} {t.common.all} ({availableRepos.repos.length})
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleDeselectAllRepos}
                                className="text-xs"
                              >
                                Deselect All
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                      {availableRepos ? (
                        <div className="space-y-3">
                          <div className="max-h-64 overflow-y-auto space-y-2 border rounded-lg p-3">
                            {availableRepos.repos.length === 0 ? (
                              <p className="text-sm text-muted-foreground text-center py-4">
                                {t.dashboard.noRepositories}
                              </p>
                            ) : (
                              availableRepos.repos.map((repo) => {
                                const isSelected = selectedRepoFullNames.has(repo.full_name);
                                return (
                                  <label
                                    key={repo.id}
                                    className="flex items-center gap-3 p-2 rounded hover:bg-[hsl(0_0%_10%)] cursor-pointer"
                                  >
                                    <input
                                      type="checkbox"
                                      checked={isSelected}
                                      onChange={() => handleToggleRepo(repo.full_name)}
                                      className="w-4 h-4 accent-primary"
                                    />
                                    <div className="flex-1 flex items-center gap-2">
                                      <Github className="w-4 h-4" />
                                      <span className="font-mono text-sm">{repo.full_name}</span>
                                      {repo.private && (
                                        <Badge variant="secondary" className="text-xs">Private</Badge>
                                      )}
                                    </div>
                                  </label>
                                );
                              })
                            )}
                          </div>
                          <Button
                            onClick={handleSaveRepos}
                            disabled={selectReposMutation.isPending}
                            className="w-full"
                          >
                            {selectReposMutation.isPending ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                {t.common.saving}
                              </>
                            ) : (
                              <>
                                {t.common.save} {t.credentials.selectedRepositories} ({selectedRepoFullNames.size})
                              </>
                            )}
                          </Button>
                          {selectReposMutation.isError && (
                            <p className="text-sm text-destructive">
                              Failed to save repository selection
                            </p>
                          )}
                        </div>
                      ) : (
                        <div className="text-sm text-muted-foreground">
                          Loading repositories...
                        </div>
                      )}
                    </div>

                    {selectedRepos && selectedRepos.repos.length > 0 ? (
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Currently Selected</h4>
                        <div className="space-y-2">
                          {selectedRepos.repos.map((repo) => (
                            <div
                              key={repo.id}
                                  className="p-3 rounded-lg bg-[hsl(0_0%_8%)]"
                            >
                                  <div className="flex flex-col gap-1">
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <Github className="w-4 h-4" />
                                      <span className="font-mono text-sm">{repo.full_name}</span>
                                      {repo.private && (
                                        <Badge variant="secondary" className="text-xs">Private</Badge>
                                      )}
                                    </div>
                                    {repo.last_synced_at && (
                                      <span className="text-xs text-muted-foreground">
                                        Synced {new Date(repo.last_synced_at).toLocaleString()}
                                      </span>
                                    )}
                                  </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : selectedRepos && selectedRepos.repos.length === 0 ? (
                      <div className="text-sm text-muted-foreground text-center py-2">
                        {t.credentials.noRepositoriesSelected}. {t.credentials.selectRepositories} {t.dashboard.syncNow.toLowerCase()}.
                      </div>
                    ) : null}
                  </div>

                  <Button
                    variant="destructive"
                    onClick={() => {
                      if (confirm("Are you sure? This will delete all local data including your PAT.")) {
                        resetMutation.mutate();
                      }
                    }}
                    className="w-full"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {t.credentials.deletePat} & {t.common.reset} {t.common.all} {t.dashboard.title}
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 rounded-lg accent-bg accent-border border">
                    <AlertCircle className="w-5 h-5 accent-text" />
                    <div className="text-sm">
                      <div className="font-semibold accent-text">Authentication Not Configured</div>
                      <div className="text-muted-foreground">
                        Choose to authenticate with a PAT for full access, or use a GitHub username for public data only.
                      </div>
                    </div>
                  </div>

                  {/* Auth Mode Selector */}
                  <div className="flex gap-2 p-1 rounded-lg bg-[hsl(0_0%_8%)] border">
                    <button
                      onClick={() => setAuthMode("pat")}
                      className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        authMode === "pat"
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Key className="w-4 h-4" />
                        <span>PAT (Full Access)</span>
                      </div>
                    </button>
                    <button
                      onClick={() => setAuthMode("username")}
                      className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        authMode === "username"
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Github className="w-4 h-4" />
                        <span>Username (Public Only)</span>
                      </div>
                    </button>
                  </div>

                  {authMode === "pat" ? (
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        {t.credentials.githubPat}
                      </label>
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <Input
                            type={showPat ? "text" : "password"}
                            value={pat}
                            onChange={(e) => setPat(e.target.value)}
                            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                            className="pr-10 font-mono"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPat(!showPat)}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                          >
                            {showPat ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        <Button
                          onClick={() => patMutation.mutate({ pat })}
                          disabled={!pat || patMutation.isPending}
                        >
                          {patMutation.isPending ? "Validating..." : "Submit"}
                        </Button>
                      </div>
                      {patMutation.isError && (
                        <p className="text-sm text-destructive mt-2">
                          Failed to validate PAT. Please check and try again.
                        </p>
                      )}

                      <div className="space-y-2 text-sm text-muted-foreground mt-4">
                        <p className="font-semibold">How to create a PAT:</p>
                        <ol className="list-decimal list-inside space-y-1 ml-2">
                          <li>Go to GitHub → Settings → Developer settings</li>
                          <li>Personal access tokens → Fine-grained tokens</li>
                          <li>Generate new token</li>
                          <li>
                            Grant <span className="font-mono bg-secondary px-1 rounded">read-only</span> permissions:
                            <ul className="list-disc list-inside ml-4 mt-1">
                              <li>Repository contents</li>
                              <li>Pull requests</li>
                              <li>Issues</li>
                              <li>Metadata</li>
                            </ul>
                          </li>
                          <li>Copy the token and paste it above</li>
                        </ol>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        GitHub Username
                      </label>
                      <div className="flex gap-2">
                        <Input
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="octocat"
                          className="flex-1"
                        />
                        <Button
                          onClick={() => usernameMutation.mutate({ username })}
                          disabled={!username || usernameMutation.isPending}
                        >
                          {usernameMutation.isPending ? "Validating..." : "Submit"}
                        </Button>
                      </div>
                      {usernameMutation.isError && (
                        <p className="text-sm text-destructive mt-2">
                          Failed to validate username. Please check and try again.
                        </p>
                      )}

                      <div className="space-y-2 text-sm text-muted-foreground mt-4">
                        <p className="font-semibold">Username-only mode:</p>
                        <ul className="list-disc list-inside space-y-1 ml-2">
                          <li>Access public repositories only</li>
                          <li>No authentication required</li>
                          <li>Limited by GitHub&apos;s unauthenticated rate limits</li>
                          <li>Cannot access private repositories</li>
                        </ul>
                      </div>
                    </div>
                  )}

                  {(isAutoSyncing || autoSyncStatus) && (
                    <div className="mt-4 p-4 rounded-lg accent-bg accent-border border">
                      <div className="flex items-center gap-3">
                        {isAutoSyncing ? (
                          <Loader2 className="w-5 h-5 accent-text animate-spin" />
                        ) : (
                          <CheckCircle className="w-5 h-5 accent-text" />
                        )}
                        <div className="flex-1">
                          <div className="font-semibold accent-text">
                            {isAutoSyncing ? "Setting up..." : "Setup Complete"}
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {autoSyncStatus || "Initializing automatic sync..."}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
            </div>

            {/* Right column: Internal/External + Internal team + External contributors stacked */}
            <div className="space-y-8 lg:pl-4">
              {/* Internal/External Organizations */}
              {authStatus?.configured && (
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Building2 className="w-5 h-5" />
                      {t.credentials.internalOrganizations}
                    </CardTitle>
                    <CardDescription>
                      {t.credentials.internalOrganizationsDescription}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {uniqueOrgs.length > 0 ? (
                      <>
                        <div className="space-y-3">
                          <h4 className="text-sm font-semibold">{t.credentials.internalOrganizations}</h4>
                          <div className="max-h-96 overflow-y-auto space-y-2 border rounded-lg p-3">
                            {uniqueOrgs.map((org) => {
                              const isOrgInternal = internalOrgs.includes(org);
                              const orgRepos = reposByOrg[org] || [];
                              const isExpanded = expandedOrgs.has(org);
                              
                              return (
                                <div key={org} className="space-y-2">
                                  <div className="flex items-center gap-3 p-2 rounded hover:bg-[hsl(0_0%_10%)]">
                                    <input
                                      type="checkbox"
                                      checked={isOrgInternal}
                                      onChange={() => handleToggleOrg(org)}
                                      className="w-4 h-4 accent-primary"
                                    />
                                    <div className="flex-1 flex items-center gap-2">
                                      <Building2 className="w-4 h-4" />
                                      <span className="font-mono text-sm font-semibold">{org}</span>
                                      <Badge variant={isOrgInternal ? "default" : "secondary"} className="text-xs">
                                        {isOrgInternal ? "Internal" : "External"}
                                      </Badge>
                                      <span className="text-xs text-muted-foreground">
                                        ({orgRepos.length} {orgRepos.length === 1 ? 'repo' : 'repos'})
                                      </span>
                                    </div>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => toggleOrgExpansion(org)}
                                      className="h-6 w-6 p-0"
                                    >
                                      {isExpanded ? (
                                        <ChevronUp className="w-4 h-4" />
                                      ) : (
                                        <ChevronDown className="w-4 h-4" />
                                      )}
                                    </Button>
                                  </div>
                                  
                                  {/* Collapsible repo selection */}
                                  {isExpanded && orgRepos.length > 0 && (
                                    <div className="ml-6 pl-4 border-l-2 border-secondary space-y-1">
                                      <div className="flex items-center justify-between mb-2 pb-2 border-b border-secondary">
                                        <span className="text-xs text-muted-foreground">
                                          {orgRepos.filter(r => internalRepos.includes(r.full_name)).length} of {orgRepos.length} selected
                                        </span>
                                        <div className="flex gap-1">
                                          {orgRepos.filter(r => internalRepos.includes(r.full_name)).length < orgRepos.length ? (
                                            <Button
                                              variant="ghost"
                                              size="sm"
                                              onClick={() => handleSelectAllOrgRepos(org)}
                                              className="text-xs h-6 px-2"
                                            >
                                              {t.common.select} {t.common.all}
                                            </Button>
                                          ) : (
                                            <Button
                                              variant="ghost"
                                              size="sm"
                                              onClick={() => handleDeselectAllOrgRepos(org)}
                                              className="text-xs h-6 px-2"
                                            >
                                              {t.common.remove} {t.common.all}
                                            </Button>
                                          )}
                                        </div>
                                      </div>
                                      {orgRepos.map((repo) => {
                                        const isRepoInternal = internalRepos.includes(repo.full_name);
                                        
                                        return (
                                          <label
                                            key={repo.id}
                                            className="flex items-center gap-3 p-2 rounded hover:bg-[hsl(0_0%_8%)] cursor-pointer"
                                          >
                                            <input
                                              type="checkbox"
                                              checked={isRepoInternal}
                                              onChange={() => handleToggleInternalRepo(repo.full_name)}
                                              className="w-3.5 h-3.5 accent-primary"
                                            />
                                            <div className="flex-1 flex items-center gap-2">
                                              <Github className="w-3.5 h-3.5" />
                                              <span className="font-mono text-xs">{repo.name}</span>
                                              {repo.private && (
                                                <Badge variant="secondary" className="text-xs">Private</Badge>
                                              )}
                                            </div>
                                            <Badge 
                                              variant={isRepoInternal ? "default" : "outline"} 
                                              className="text-xs"
                                            >
                                              {isRepoInternal ? "Internal" : "External"}
                                            </Badge>
                                          </label>
                                        );
                                      })}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        <Button
                          onClick={handleSaveInternalOrgs}
                          disabled={internalOrgsMutation.isPending}
                          className="w-full"
                        >
                          {internalOrgsMutation.isPending ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              Save Internal Configuration ({internalOrgs.length} orgs, {internalRepos.length} specific repos)
                            </>
                          )}
                        </Button>

                        {internalOrgsMutation.isError && (
                          <p className="text-sm text-destructive">
                            Failed to save internal configuration
                          </p>
                        )}

                        {internalOrgsMutation.isSuccess && (
                          <p className="text-sm text-green-600 dark:text-green-400">
                            Internal configuration saved successfully
                          </p>
                        )}

                        {internalOrgs.length > 0 && (
                          <div className="p-4 rounded-lg bg-[hsl(0_0%_8%)] border border-secondary">
                            <h4 className="text-sm font-semibold mb-2">Current Configuration</h4>
                            <div className="space-y-2 text-sm">
                              <div>
                                <span className="text-muted-foreground">{t.credentials.internalOrganizations}: </span>
                                <span className="font-mono">{internalOrgs.join(', ')}</span>
                              </div>
                              {internalRepos.length > 0 && (
                                <div>
                                  <span className="text-muted-foreground">Specific Internal Repos: </span>
                                  <span className="font-mono">{internalRepos.length} selected</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <Building2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No organizations found</p>
                        <p className="text-sm">Select repositories first to configure internal/external settings</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

          {/* Internal Team Members Management */}
              <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                {t.credentials.teamMembers}
              </CardTitle>
              <CardDescription>
                {t.credentials.teamMembersDescription}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newMember}
                  onChange={(e) => setNewMember(e.target.value)}
                  placeholder={t.credentials.enterUsername}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleAddMember();
                    }
                  }}
                />
                <Button
                  onClick={handleAddMember}
                  disabled={!newMember || teamMembersMutation.isPending}
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  {t.common.add}
                </Button>
              </div>

              {members.length > 0 ? (
                <div className="space-y-2">
                  {members.map((login) => (
                    <div
                      key={login}
                      className="flex items-center justify-between p-3 rounded-lg bg-[hsl(0_0%_8%)]"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-sm font-bold">
                          {login[0].toUpperCase()}
                        </div>
                        <span className="font-mono">{login}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveMember(login)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>{t.credentials.teamMembers} {t.common.none.toLowerCase()}</p>
                  <p className="text-sm">{t.credentials.addTeamMember}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* External Contributors Management */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="w-5 h-5" />
                {t.credentials.externalContributors}
              </CardTitle>
              <CardDescription>
                {t.credentials.externalContributorsDescription}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newExternalContributor}
                  onChange={(e) => setNewExternalContributor(e.target.value)}
                  placeholder={t.credentials.enterUsername}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleAddExternalContributor();
                    }
                  }}
                />
                <Button
                  onClick={handleAddExternalContributor}
                  disabled={!newExternalContributor || externalContributorsMutation.isPending}
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  {t.common.add}
                </Button>
              </div>

              {externalContributors.length > 0 ? (
                <div className="space-y-2">
                  {externalContributors.map((login) => (
                    <div
                      key={login}
                      className="flex items-center justify-between p-3 rounded-lg bg-[hsl(0_0%_8%)]"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-sm font-bold">
                          {login[0].toUpperCase()}
                        </div>
                        <span className="font-mono">{login}</span>
                        <Badge variant="outline" className="text-xs">{t.dashboard.external}</Badge>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveExternalContributor(login)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <UserPlus className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>{t.credentials.externalContributors} {t.common.none.toLowerCase()}</p>
                  <p className="text-sm">{t.credentials.addExternalContributor}</p>
                </div>
              )}

              {externalContributorsMutation.isError && (
                <p className="text-sm text-destructive">
                  Failed to update external contributors
                </p>
              )}

              {externalContributorsMutation.isSuccess && (
                <p className="text-sm text-green-600 dark:text-green-400">
                  External contributors updated! Run a sync to fetch their commits.
                </p>
              )}
            </CardContent>
          </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

