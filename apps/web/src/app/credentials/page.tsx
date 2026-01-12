"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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
  Loader2
} from "lucide-react";

export default function CredentialsPage() {
  const [pat, setPat] = useState("");
  const [showPat, setShowPat] = useState(false);
  const [newMember, setNewMember] = useState("");
  const [members, setMembers] = useState<string[]>([]);
  const queryClient = useQueryClient();

  const { data: authStatus } = useQuery({
    queryKey: ["auth-status"],
    queryFn: () => api.getAuthStatus(),
  });

  const { data: teamMembers } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => api.getTeamMembers(),
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

  const [selectedRepoFullNames, setSelectedRepoFullNames] = useState<Set<string>>(new Set());

  const selectReposMutation = useMutation({
    mutationFn: (repoFullNames: string[]) => api.selectRepos(repoFullNames),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["selected-repos"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const patMutation = useMutation({
    mutationFn: (data: { pat: string }) => api.submitPat(data.pat),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth-status"] });
      setPat("");
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

  // Initialize members from server
  useEffect(() => {
    if (teamMembers?.members) {
      setMembers(teamMembers.members.map(m => m.github_login));
    }
  }, [teamMembers]);

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

  const handleToggleRepo = (fullName: string) => {
    const updated = new Set(selectedRepoFullNames);
    if (updated.has(fullName)) {
      updated.delete(fullName);
    } else {
      updated.add(fullName);
    }
    setSelectedRepoFullNames(updated);
  };

  const handleSaveRepos = () => {
    selectReposMutation.mutate(Array.from(selectedRepoFullNames));
  };

  // Update selected repos when data loads (only once or when it becomes available)
  useEffect(() => {
    if (selectedRepos?.repos && selectedRepoFullNames.size === 0) {
      setSelectedRepoFullNames(new Set(selectedRepos.repos.map(r => r.full_name)));
    }
  }, [selectedRepos]);

  return (
    <div className="flex min-h-screen bg-background">
      <Navigation />
      
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold accent-text mb-2">Credentials</h1>
          <p className="text-muted-foreground mb-8">
            Configure your GitHub access and manage team members
          </p>

          {/* GitHub PAT Configuration */}
          <Card className="glass-card glow mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="w-5 h-5" />
                GitHub Personal Access Token
              </CardTitle>
              <CardDescription>
                Your PAT is stored encrypted locally and never leaves your machine
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {authStatus?.configured ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 rounded-lg accent-bg accent-border border">
                    <CheckCircle className="w-5 h-5 accent-text" />
                    <div className="flex-1">
                      <div className="font-semibold accent-text">PAT Configured</div>
                      <div className="text-sm text-muted-foreground">
                        Authenticated as <span className="font-mono">{authStatus.user?.login}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-semibold mb-3">Repository Selection</h4>
                      {availableRepos ? (
                        <div className="space-y-3">
                          <div className="max-h-64 overflow-y-auto space-y-2 border rounded-lg p-3">
                            {availableRepos.repos.length === 0 ? (
                              <p className="text-sm text-muted-foreground text-center py-4">
                                No repositories found
                              </p>
                            ) : (
                              availableRepos.repos.map((repo) => {
                                const isSelected = selectedRepoFullNames.has(repo.full_name);
                                return (
                                  <label
                                    key={repo.id}
                                    className="flex items-center gap-3 p-2 rounded hover:bg-secondary/50 cursor-pointer"
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
                                Saving...
                              </>
                            ) : (
                              <>
                                Save Selected Repositories ({selectedRepoFullNames.size})
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
                              className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
                            >
                              <div className="flex items-center gap-2">
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
                          ))}
                        </div>
                      </div>
                    ) : selectedRepos && selectedRepos.repos.length === 0 ? (
                      <div className="text-sm text-muted-foreground text-center py-2">
                        No repositories selected. Select repositories above to start syncing.
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
                    Delete PAT & Reset All Data
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 rounded-lg accent-bg accent-border border">
                    <AlertCircle className="w-5 h-5 accent-text" />
                    <div className="text-sm">
                      <div className="font-semibold accent-text">PAT Not Configured</div>
                      <div className="text-muted-foreground">
                        Create a fine-grained PAT with read-only permissions
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      GitHub Personal Access Token
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
                  </div>

                  <div className="space-y-2 text-sm text-muted-foreground">
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
              )}
            </CardContent>
          </Card>

          {/* Team Members Management */}
          <Card className="glass-card glow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Team Members
              </CardTitle>
              <CardDescription>
                Add GitHub usernames of your internal team members to distinguish internal vs external contributions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newMember}
                  onChange={(e) => setNewMember(e.target.value)}
                  placeholder="GitHub username"
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
                  Add
                </Button>
              </div>

              {members.length > 0 ? (
                <div className="space-y-2">
                  {members.map((login) => (
                    <div
                      key={login}
                      className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
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
                  <p>No team members added yet</p>
                  <p className="text-sm">Add GitHub usernames above to get started</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

