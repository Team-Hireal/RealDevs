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


def test_calculate_trendline_slope_upward():
    """Test trendline slope calculation for upward trend."""
    # Simple upward trend: [1, 2, 3, 4, 5]
    daily_scores = [1.0, 2.0, 3.0, 4.0, 5.0]
    slope = MetricsService._calculate_trendline_slope(daily_scores)
    # Should be positive (approximately 1.0 for this linear progression)
    assert slope > 0
    assert abs(slope - 1.0) < 0.01


def test_calculate_trendline_slope_downward():
    """Test trendline slope calculation for downward trend."""
    # Simple downward trend: [5, 4, 3, 2, 1]
    daily_scores = [5.0, 4.0, 3.0, 2.0, 1.0]
    slope = MetricsService._calculate_trendline_slope(daily_scores)
    # Should be negative (approximately -1.0 for this linear progression)
    assert slope < 0
    assert abs(slope - (-1.0)) < 0.01


def test_calculate_trendline_slope_flat():
    """Test trendline slope calculation for flat trend."""
    # Flat trend: all same values
    daily_scores = [3.0, 3.0, 3.0, 3.0, 3.0]
    slope = MetricsService._calculate_trendline_slope(daily_scores)
    # Should be approximately 0
    assert abs(slope) < 0.01


def test_calculate_trendline_slope_insufficient_data():
    """Test trendline slope with insufficient data."""
    # Less than 2 data points
    slope = MetricsService._calculate_trendline_slope([1.0])
    assert slope == 0.0
    
    slope = MetricsService._calculate_trendline_slope([])
    assert slope == 0.0


def test_calculate_trendline_slope_realistic():
    """Test trendline slope with realistic weighted scores."""
    # Simulate realistic daily weighted scores with upward trend
    # Day 1: 10, Day 2: 12, Day 3: 15, Day 4: 18, Day 5: 20
    daily_scores = [10.0, 12.0, 15.0, 18.0, 20.0]
    slope = MetricsService._calculate_trendline_slope(daily_scores)
    # Should be positive
    assert slope > 0
    # Should be around 2.5-2.6 (average increase per day)
    assert abs(slope - 2.5) < 0.15

