"""Unit tests for Dashboard service."""

from datetime import datetime

import pytest

from src.models.job import JenkinsJob, JobStatus
from src.models.state import DashboardState
from src.services.dashboard import DashboardService, calculate_statistics


class TestCalculateStatistics:
    """Tests for calculate_statistics function."""

    def test_calculate_statistics_with_mixed_jobs(
        self, mock_jobs_list: list[JenkinsJob]
    ) -> None:
        """Test statistics calculation with mixed job statuses."""
        stats = calculate_statistics(mock_jobs_list)

        assert stats["total"] == 3
        assert stats["success"] == 1
        assert stats["failure"] == 1
        assert stats["building"] == 1
        assert stats["disabled"] == 0
        assert "success_rate" in stats
        assert "health" in stats

    def test_calculate_statistics_empty_list(self) -> None:
        """Test statistics calculation with empty job list."""
        stats = calculate_statistics([])

        assert stats["total"] == 0
        assert stats["success"] == 0
        assert stats["failure"] == 0
        assert stats["building"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["health"] == "healthy"

    def test_calculate_statistics_all_success(
        self, mock_jenkins_job_success: JenkinsJob
    ) -> None:
        """Test statistics with all successful jobs."""
        jobs = [mock_jenkins_job_success] * 5
        stats = calculate_statistics(jobs)

        assert stats["total"] == 5
        assert stats["success"] == 5
        assert stats["failure"] == 0
        assert stats["success_rate"] == 100.0
        assert stats["health"] == "healthy"

    def test_calculate_statistics_some_failures(
        self, mock_jenkins_job_success: JenkinsJob, mock_jenkins_job_failure: JenkinsJob
    ) -> None:
        """Test statistics with some failing jobs."""
        jobs = [mock_jenkins_job_success, mock_jenkins_job_success, mock_jenkins_job_failure]
        stats = calculate_statistics(jobs)

        assert stats["total"] == 3
        assert stats["success"] == 2
        assert stats["failure"] == 1
        assert stats["health"] == "warning"

    def test_calculate_statistics_many_failures(
        self, mock_jenkins_job_failure: JenkinsJob
    ) -> None:
        """Test statistics with many failing jobs (critical health)."""
        jobs = [mock_jenkins_job_failure] * 5
        stats = calculate_statistics(jobs)

        assert stats["total"] == 5
        assert stats["failure"] == 5
        assert stats["health"] == "critical"

    def test_calculate_statistics_includes_all_status_counts(self) -> None:
        """Test that all status types are counted."""
        jobs = [
            JenkinsJob(
                name="job1",
                url="http://test/job1",
                status=JobStatus.SUCCESS,
                last_build_number=1,
                last_build_result="SUCCESS",
                last_build_timestamp=datetime.now(),
                last_build_duration_ms=1000,
                is_building=False,
            ),
            JenkinsJob(
                name="job2",
                url="http://test/job2",
                status=JobStatus.DISABLED,
                last_build_number=None,
                last_build_result=None,
                last_build_timestamp=None,
                last_build_duration_ms=None,
                is_building=False,
            ),
            JenkinsJob(
                name="job3",
                url="http://test/job3",
                status=JobStatus.UNSTABLE,
                last_build_number=2,
                last_build_result="UNSTABLE",
                last_build_timestamp=datetime.now(),
                last_build_duration_ms=2000,
                is_building=False,
            ),
        ]

        stats = calculate_statistics(jobs)

        assert stats["total"] == 3
        assert stats["success"] == 1
        assert stats["disabled"] == 1
        assert stats["unstable"] == 1


class TestDashboardService:
    """Tests for DashboardService class."""

    def test_get_dashboard_state_returns_state(
        self, mock_jobs_list: list[JenkinsJob]
    ) -> None:
        """Test get_dashboard_state returns a DashboardState object."""
        service = DashboardService(jobs=mock_jobs_list)
        state = service.get_dashboard_state()

        assert isinstance(state, DashboardState)
        assert state.total_jobs == 3
        assert state.is_jenkins_available is True

    def test_get_dashboard_state_with_empty_jobs(self) -> None:
        """Test get_dashboard_state with no jobs."""
        service = DashboardService(jobs=[])
        state = service.get_dashboard_state()

        assert state.total_jobs == 0
        assert state.success_count == 0
        assert state.failure_count == 0

    def test_get_dashboard_state_with_error(self) -> None:
        """Test get_dashboard_state with error message."""
        service = DashboardService(
            jobs=[],
            is_available=False,
            error_message="Jenkins unavailable",
        )
        state = service.get_dashboard_state()

        assert state.is_jenkins_available is False
        assert state.error_message == "Jenkins unavailable"
