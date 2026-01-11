"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request schemas
class PatSubmission(BaseModel):
    pat: str = Field(..., min_length=1)
    store_mode: str = Field(default="encrypted", pattern="^(encrypted|memory)$")


class RepoSelection(BaseModel):
    repo_full_names: List[str] = Field(..., min_items=1)


class SyncRequest(BaseModel):
    range_days: int = Field(default=7, ge=1, le=90)


class TeamMemberUpdate(BaseModel):
    github_logins: List[str]


class SettingsUpdate(BaseModel):
    key: str
    value: str


# Response schemas
class UserInfo(BaseModel):
    login: str
    id: int
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthResponse(BaseModel):
    ok: bool
    user: Optional[UserInfo] = None
    error: Optional[str] = None


class RepoInfo(BaseModel):
    id: int
    full_name: str
    owner: str
    name: str
    private: bool
    default_branch: str
    updated_at: Optional[str] = None


class ReposListResponse(BaseModel):
    repos: List[RepoInfo]


class SyncResponse(BaseModel):
    ok: bool
    synced_repos: List[str]
    stats: Dict[str, Any]


class DashboardResponse(BaseModel):
    team_summary: Dict[str, Any]
    repo_summaries: List[Dict[str, Any]]
    risk_flags: List[Dict[str, Any]]
    contributors: List[Dict[str, Any]]
    last_synced: Optional[str]
    range_days: int


class WeeklyRecapResponse(BaseModel):
    text: str


class GenericResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
    error: Optional[str] = None

