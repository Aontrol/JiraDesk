"""
Data models for JiraDesk application.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    id: int
    key: str
    name: str
    description: str = ""
    created_at: str = ""


@dataclass
class Status:
    id: int
    name: str
    sort_order: int
    color: str = "#5f6368"
    bg_color: str = "#f1f3f4"


@dataclass
class Issue:
    id: int
    project_id: int
    issue_number: int
    title: str
    description: str = ""
    issue_type: str = "Task"  # Task, Bug, Story, Epic
    priority: str = "Medium"   # Low, Medium, High, Urgent
    status_id: int = 1
    position: int = 0
    created_at: str = ""
    updated_at: str = ""
    # Joined convenience fields
    project_key: str = ""
    status_name: str = ""
    total_minutes: int = 0

    @property
    def key(self) -> str:
        """Returns the formatted key like 'DEV-101'."""
        if self.project_key:
            return f"{self.project_key}-{self.issue_number}"
        return f"ISSUE-{self.issue_number}"

    @property
    def formatted_time(self) -> str:
        """Returns human readable time spent like '2h 15m'."""
        if not self.total_minutes or self.total_minutes <= 0:
            return ""
        hours = self.total_minutes // 60
        mins = self.total_minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{mins}m"


@dataclass
class Worklog:
    id: int
    issue_id: int
    minutes_spent: int
    notes: str = ""
    logged_at: str = ""

    @property
    def formatted_time(self) -> str:
        hours = self.minutes_spent // 60
        mins = self.minutes_spent % 60
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        return f"{mins}m"
