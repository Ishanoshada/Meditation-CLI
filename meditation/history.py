"""
Session history tracking for meditation practice.

Stores session data in a JSON file with timestamps, duration, and type.
Provides statistics by day, week, month, and averages.
"""

from __future__ import annotations
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
import time

HISTORY_FILE = os.path.expanduser("~/.meditation_history.json")

class Session:
    """A single meditation session record."""
    
    def __init__(self, duration_seconds: int, session_type: str = "timer", timestamp: Optional[datetime] = None):
        self.duration_seconds = duration_seconds
        self.session_type = session_type  # "timer", "breathing", or "reflection"
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration_seconds": self.duration_seconds,
            "session_type": self.session_type,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Session:
        return cls(
            duration_seconds=data["duration_seconds"],
            session_type=data["session_type"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
    
    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60.0
    
    def __str__(self) -> str:
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.duration_minutes:.1f}m ({self.session_type})"


class History:
    """Manages the meditation session history."""
    
    def __init__(self):
        self.sessions: List[Session] = []
        self._load()
    
    def _load(self) -> None:
        """Load sessions from the history file."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sessions = [Session.from_dict(s) for s in data.get("sessions", [])]
            except (json.JSONDecodeError, KeyError, ValueError):
                self.sessions = []
        else:
            self.sessions = []
    
    def _save(self) -> None:
        """Save sessions to the history file."""
        data = {
            "sessions": [s.to_dict() for s in self.sessions],
            "last_updated": datetime.now().isoformat()
        }
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, IOError):
            pass  # Silently fail - we don't want to crash over file errors
    
    def add_session(self, duration_seconds: int, session_type: str = "timer") -> None:
        """Add a new session to the history."""
        session = Session(duration_seconds, session_type)
        self.sessions.append(session)
        self._save()
    
    def get_sessions_since(self, since: datetime) -> List[Session]:
        """Get all sessions since a given date."""
        return [s for s in self.sessions if s.timestamp >= since]
    
    def get_today_sessions(self) -> List[Session]:
        """Get sessions from today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_sessions_since(today)
    
    def get_week_sessions(self) -> List[Session]:
        """Get sessions from the last 7 days."""
        week_ago = datetime.now() - timedelta(days=7)
        return self.get_sessions_since(week_ago)
    
    def get_month_sessions(self) -> List[Session]:
        """Get sessions from the last 30 days."""
        month_ago = datetime.now() - timedelta(days=30)
        return self.get_sessions_since(month_ago)
    
    def get_total_time(self, sessions: List[Session]) -> float:
        """Get total meditation time in minutes for a list of sessions."""
        return sum(s.duration_minutes for s in sessions)
    
    def get_average_time(self, sessions: List[Session]) -> float:
        """Get average session time in minutes for a list of sessions."""
        if not sessions:
            return 0.0
        return self.get_total_time(sessions) / len(sessions)
    
    def get_streak(self) -> int:
        """Calculate the current streak of consecutive days with meditation."""
        if not self.sessions:
            return 0
        
        # Get unique days with sessions
        days_with_sessions = set()
        for session in self.sessions:
            date_str = session.timestamp.strftime("%Y-%m-%d")
            days_with_sessions.add(date_str)
        
        # Sort dates
        sorted_dates = sorted(days_with_sessions, reverse=True)
        if not sorted_dates:
            return 0
        
        # Check if today has a session
        today = datetime.now().strftime("%Y-%m-%d")
        if sorted_dates[0] != today:
            # Check if yesterday has a session (streak might still be active)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if sorted_dates[0] != yesterday:
                return 0
        else:
            # Today has a session, start counting from today
            pass
        
        streak = 0
        current_date = datetime.now()
        while True:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in days_with_sessions:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_weekly_stats(self) -> Dict[str, Any]:
        """Get comprehensive weekly statistics."""
        week_sessions = self.get_week_sessions()
        total_minutes = self.get_total_time(week_sessions)
        avg_minutes = self.get_average_time(week_sessions)
        
        # Group by day of week
        daily_totals = defaultdict(float)
        for session in week_sessions:
            day_name = session.timestamp.strftime("%A")
            daily_totals[day_name] += session.duration_minutes
        
        # Get the last 7 days (including empty days)
        last_7_days = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            day_name = date.strftime("%A")
            day_total = daily_totals.get(day_name, 0.0)
            last_7_days.append((day_name, day_total))
        
        return {
            "total_minutes": total_minutes,
            "average_minutes": avg_minutes,
            "session_count": len(week_sessions),
            "daily_breakdown": last_7_days
        }
    
    def get_monthly_stats(self) -> Dict[str, Any]:
        """Get comprehensive monthly statistics."""
        month_sessions = self.get_month_sessions()
        total_minutes = self.get_total_time(month_sessions)
        avg_minutes = self.get_average_time(month_sessions)
        
        # Group by week
        weekly_totals = defaultdict(float)
        for session in month_sessions:
            week_num = session.timestamp.isocalendar()[1]
            weekly_totals[week_num] += session.duration_minutes
        
        # Get the last 4 weeks
        last_4_weeks = []
        current_week = datetime.now().isocalendar()[1]
        for i in range(3, -1, -1):
            week = current_week - i
            week_total = weekly_totals.get(week, 0.0)
            last_4_weeks.append((f"Week {i+1}", week_total))
        
        return {
            "total_minutes": total_minutes,
            "average_minutes": avg_minutes,
            "session_count": len(month_sessions),
            "weekly_breakdown": last_4_weeks
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall summary statistics."""
        total_all = self.get_total_time(self.sessions)
        avg_all = self.get_average_time(self.sessions)
        today_total = self.get_total_time(self.get_today_sessions())
        week_total = self.get_total_time(self.get_week_sessions())
        month_total = self.get_total_time(self.get_month_sessions())
        streak = self.get_streak()
        
        return {
            "total_sessions": len(self.sessions),
            "total_minutes": total_all,
            "average_minutes": avg_all,
            "today_minutes": today_total,
            "week_minutes": week_total,
            "month_minutes": month_total,
            "streak_days": streak
        }
    
    def clear_history(self) -> None:
        """Clear all history (with confirmation in CLI)."""
        self.sessions = []
        self._save()