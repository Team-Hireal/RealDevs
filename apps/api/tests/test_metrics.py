"""Tests for metrics service."""
import pytest
from app.services.metrics_service import MetricsService


def test_default_weights():
    """Test default weights are set correctly."""
    weights = MetricsService.DEFAULT_WEIGHTS
    assert "commits" in weights
    assert "prs_opened" in weights
    assert "prs_merged" in weights
    assert "issues_closed" in weights
    assert weights["commits"] > 0


def test_get_weights():
    """Test getting weights."""
    weights = MetricsService.get_weights()
    assert isinstance(weights, dict)
    assert len(weights) == 4


def test_weekly_recap_format():
    """Test weekly recap generates proper text."""
    # This will work even with empty data
    recap = MetricsService.get_weekly_recap(7)
    assert isinstance(recap, str)
    assert "Weekly Recap" in recap
    assert "Team Activity" in recap or "No" in recap.lower()

