"""Database models for RealDevs."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

db = SQLAlchemy()


class AuthToken(db.Model):
    """Stores encrypted GitHub PAT."""
    __tablename__ = 'auth_tokens'
    
    id = Column(Integer, primary_key=True)
    encrypted_token = Column(Text, nullable=False)
    github_user_login = Column(String(255), nullable=False)
    github_user_id = Column(Integer, nullable=False)
    store_mode = Column(String(20), default='encrypted')  # 'encrypted' or 'memory'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Repository(db.Model):
    """Stores selected repositories."""
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    private = Column(Boolean, default=False)
    default_branch = Column(String(100), default='main')
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    contributors = relationship('Contributor', back_populates='repository', cascade='all, delete-orphan')
    daily_stats = relationship('DailyStats', back_populates='repository', cascade='all, delete-orphan')


class Contributor(db.Model):
    """Stores contributors (team members)."""
    __tablename__ = 'contributors'
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, nullable=False, index=True)
    login = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    is_team_member = Column(Boolean, default=False)  # Marked by user as internal team
    repo_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    linkedin_url = Column(String(512), nullable=True)
    twitter_url = Column(String(512), nullable=True)
    website_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    repository = relationship('Repository', back_populates='contributors')
    daily_stats = relationship('DailyStats', back_populates='contributor', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('repo_id', 'github_id', name='uix_repo_contributor'),
    )


class DailyStats(db.Model):
    """Stores daily aggregated stats per repo per contributor."""
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, index=True)
    repo_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    contributor_id = Column(Integer, ForeignKey('contributors.id'), nullable=False)
    
    # Metrics
    commits_count = Column(Integer, default=0)
    prs_opened = Column(Integer, default=0)
    prs_merged = Column(Integer, default=0)
    prs_closed = Column(Integer, default=0)
    issues_closed = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    repository = relationship('Repository', back_populates='daily_stats')
    contributor = relationship('Contributor', back_populates='daily_stats')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('date', 'repo_id', 'contributor_id', name='uix_daily_repo_contributor'),
    )


class TeamMember(db.Model):
    """Stores manually configured team members."""
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True)
    github_login = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Settings(db.Model):
    """Stores user preferences and thresholds."""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExternalCommit(db.Model):
    """Stores commits made by team members to external (non-tracked) repositories."""
    __tablename__ = 'external_commits'
    
    id = Column(Integer, primary_key=True)
    github_user_login = Column(String(255), nullable=False, index=True)
    github_user_id = Column(Integer, nullable=False, index=True)
    repo_full_name = Column(String(255), nullable=False, index=True)
    repo_owner = Column(String(255), nullable=False)
    commit_sha = Column(String(40), unique=True, nullable=False, index=True)
    commit_date = Column(DateTime, nullable=False, index=True)
    commit_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExternalContributor(db.Model):
    """Stores manually configured external contributors to track."""
    __tablename__ = 'external_contributors'
    
    id = Column(Integer, primary_key=True)
    github_login = Column(String(255), unique=True, nullable=False, index=True)
    github_user_id = Column(Integer, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

