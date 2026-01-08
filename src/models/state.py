"""Dashboard state model for the Jenkins Dashboard."""

from dataclasses import dataclass
from datetime import datetime

from models.job import JenkinsJob


@dataclass
class DashboardState:
    """Represents the current state of the dashboard."""

    jobs: list[JenkinsJob]
    last_refresh: datetime
    is_jenkins_available: bool
    error_message: str | None
    total_jobs: int
    success_count: int
    failure_count: int
    building_count: int
