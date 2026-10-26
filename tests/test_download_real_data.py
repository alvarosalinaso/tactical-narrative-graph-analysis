"""Tests for download_real_data module."""

from download_real_data import compute_opponent


def test_compute_opponent_home_team():
    """Pass by a home-team player: opponent is the away team."""
    assert compute_opponent("Morocco", "Morocco", "Canada") == "Canada"


def test_compute_opponent_away_team():
    """Pass by an away-team player: opponent is the home team."""
    assert compute_opponent("Canada", "Morocco", "Canada") == "Morocco"


def test_compute_opponent_not_hardcoded():
    """Logic must be generic, no hardcoded club name."""
    assert compute_opponent("Wolves", "Liverpool", "Wolves") == "Liverpool"
    assert compute_opponent("Liverpool", "Liverpool", "Wolves") == "Wolves"
