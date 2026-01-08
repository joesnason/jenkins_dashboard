"""Dashboard state service for the Jenkins Dashboard."""

from datetime import datetime

from src.models.job import JenkinsJob, JobStatus
from src.models.state import DashboardState


def calculate_statistics(jobs: list[JenkinsJob]) -> dict:
    """Calculate statistics from a list of Jenkins jobs.

    Args:
        jobs: List of JenkinsJob objects

    Returns:
        Dictionary with statistics including:
        - total: Total number of jobs
        - success: Count of successful jobs
        - failure: Count of failed jobs
        - building: Count of building jobs
        - disabled: Count of disabled jobs
        - unstable: Count of unstable jobs
        - success_rate: Percentage of successful jobs
        - health: Overall health indicator ('healthy', 'warning', 'critical')
    """
    if not jobs:
        return {
            "total": 0,
            "success": 0,
            "failure": 0,
            "building": 0,
            "disabled": 0,
            "unstable": 0,
            "not_built": 0,
            "aborted": 0,
            "unknown": 0,
            "success_rate": 0.0,
            "health": "healthy",
        }

    status_counts: dict[str, int] = {
        "success": 0,
        "failure": 0,
        "building": 0,
        "disabled": 0,
        "unstable": 0,
        "not_built": 0,
        "aborted": 0,
        "unknown": 0,
    }

    for job in jobs:
        status_key = job.status.value
        if status_key in status_counts:
            status_counts[status_key] += 1

    total = len(jobs)
    success = status_counts["success"]
    failure = status_counts["failure"]

    # Calculate success rate (exclude disabled, not_built, and currently building)
    countable_jobs = total - status_counts["disabled"] - status_counts["not_built"] - status_counts["building"]
    success_rate = (success / countable_jobs * 100) if countable_jobs > 0 else 0.0

    # Determine health based on failure count
    if failure == 0:
        health = "healthy"
    elif failure <= 2:
        health = "warning"
    else:
        health = "critical"

    return {
        "total": total,
        "success": success,
        "failure": failure,
        "building": status_counts["building"],
        "disabled": status_counts["disabled"],
        "unstable": status_counts["unstable"],
        "not_built": status_counts["not_built"],
        "aborted": status_counts["aborted"],
        "unknown": status_counts["unknown"],
        "success_rate": round(success_rate, 1),
        "health": health,
    }


class DashboardService:
    """Service for managing dashboard state."""

    def __init__(
        self,
        jobs: list[JenkinsJob] | None = None,
        is_available: bool = True,
        error_message: str | None = None,
    ) -> None:
        """Initialize dashboard service.

        Args:
            jobs: List of Jenkins jobs (default: empty list)
            is_available: Whether Jenkins is available (default: True)
            error_message: Error message if Jenkins is unavailable
        """
        self._jobs = jobs if jobs is not None else []
        self._is_available = is_available
        self._error_message = error_message
        self._last_refresh = datetime.now()

    def get_dashboard_state(self) -> DashboardState:
        """Get the current dashboard state.

        Returns:
            DashboardState object with current jobs and statistics
        """
        stats = calculate_statistics(self._jobs)

        return DashboardState(
            jobs=self._jobs,
            last_refresh=self._last_refresh,
            is_jenkins_available=self._is_available,
            error_message=self._error_message,
            total_jobs=stats["total"],
            success_count=stats["success"],
            failure_count=stats["failure"],
            building_count=stats["building"],
        )

    def update_jobs(self, jobs: list[JenkinsJob]) -> None:
        """Update the job list and refresh timestamp.

        Args:
            jobs: New list of Jenkins jobs
        """
        self._jobs = jobs
        self._last_refresh = datetime.now()
        self._is_available = True
        self._error_message = None

    def set_error(self, error_message: str) -> None:
        """Set an error state for the dashboard.

        Args:
            error_message: Error message to display
        """
        self._is_available = False
        self._error_message = error_message

    def clear_error(self) -> None:
        """Clear the error state."""
        self._is_available = True
        self._error_message = None
