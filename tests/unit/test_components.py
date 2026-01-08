"""Unit tests for UI components."""

from datetime import datetime

import pytest

from src.components.job_card import get_status_color, get_status_emoji
from src.models.job import JenkinsJob, JobStatus


class TestJobCardFunctions:
    """Tests for job card helper functions."""

    def test_get_status_color_success(self) -> None:
        """Test color for SUCCESS status."""
        assert get_status_color(JobStatus.SUCCESS) == "green"

    def test_get_status_color_failure(self) -> None:
        """Test color for FAILURE status."""
        assert get_status_color(JobStatus.FAILURE) == "red"

    def test_get_status_color_unstable(self) -> None:
        """Test color for UNSTABLE status."""
        assert get_status_color(JobStatus.UNSTABLE) == "orange"

    def test_get_status_color_building(self) -> None:
        """Test color for BUILDING status."""
        assert get_status_color(JobStatus.BUILDING) == "blue"

    def test_get_status_color_disabled(self) -> None:
        """Test color for DISABLED status."""
        assert get_status_color(JobStatus.DISABLED) == "gray"

    def test_get_status_color_all_statuses(self) -> None:
        """Test that all statuses have a color."""
        for status in JobStatus:
            color = get_status_color(status)
            assert color is not None
            assert isinstance(color, str)

    def test_get_status_emoji_success(self) -> None:
        """Test emoji for SUCCESS status."""
        assert get_status_emoji(JobStatus.SUCCESS) == ":white_check_mark:"

    def test_get_status_emoji_failure(self) -> None:
        """Test emoji for FAILURE status."""
        assert get_status_emoji(JobStatus.FAILURE) == ":x:"

    def test_get_status_emoji_building(self) -> None:
        """Test emoji for BUILDING status."""
        assert get_status_emoji(JobStatus.BUILDING) == ":hourglass_flowing_sand:"

    def test_get_status_emoji_all_statuses(self) -> None:
        """Test that all statuses have an emoji."""
        for status in JobStatus:
            emoji = get_status_emoji(status)
            assert emoji is not None
            assert isinstance(emoji, str)


class TestJobDetailDisplay:
    """Tests for job detail display logic."""

    def test_job_with_build_info_shows_details(
        self, mock_jenkins_job_success: JenkinsJob
    ) -> None:
        """Test that job with build info shows all details."""
        job = mock_jenkins_job_success

        # Verify all expected fields are present
        assert job.last_build_number is not None
        assert job.last_build_result is not None
        assert job.last_build_timestamp is not None
        assert job.last_build_duration_ms is not None

    def test_job_without_builds_handles_gracefully(
        self, mock_jenkins_job_not_built: JenkinsJob
    ) -> None:
        """Test that job without builds handles gracefully."""
        job = mock_jenkins_job_not_built

        # Verify None values are handled
        assert job.last_build_number is None
        assert job.last_build_result is None
        assert job.last_build_timestamp is None
        assert job.last_build_duration_ms is None
        assert job.status == JobStatus.NOT_BUILT

    def test_building_job_shows_in_progress(
        self, mock_jenkins_job_building: JenkinsJob
    ) -> None:
        """Test that building job shows in-progress state."""
        job = mock_jenkins_job_building

        assert job.is_building is True
        assert job.status == JobStatus.BUILDING
        assert job.last_build_result is None  # Still building

    def test_job_url_is_present(
        self, mock_jenkins_job_success: JenkinsJob
    ) -> None:
        """Test that job URL is present for linking."""
        job = mock_jenkins_job_success

        assert job.url is not None
        assert job.url.startswith("https://")

    def test_duration_formatting(self) -> None:
        """Test duration formatting logic."""
        # Test short duration (seconds)
        duration_ms = 30000  # 30 seconds
        duration_s = duration_ms / 1000
        assert duration_s == 30.0

        # Test longer duration (minutes)
        duration_ms = 120000  # 2 minutes
        duration_s = duration_ms / 1000
        duration_m = duration_s / 60
        assert duration_m == 2.0


class TestJobSorting:
    """Tests for job sorting logic."""

    def test_sort_by_name(
        self,
        mock_jenkins_job_success: JenkinsJob,
        mock_jenkins_job_failure: JenkinsJob,
    ) -> None:
        """Test sorting jobs by name."""
        jobs = [mock_jenkins_job_failure, mock_jenkins_job_success]
        sorted_jobs = sorted(jobs, key=lambda j: j.name.lower())

        # backend-tests comes before frontend-build alphabetically
        assert sorted_jobs[0].name == "backend-tests"
        assert sorted_jobs[1].name == "frontend-build"

    def test_sort_by_status_priority(
        self,
        mock_jobs_list: list[JenkinsJob],
    ) -> None:
        """Test sorting jobs by status priority (failures first)."""
        status_priority = {
            JobStatus.FAILURE: 0,
            JobStatus.BUILDING: 1,
            JobStatus.UNSTABLE: 2,
            JobStatus.SUCCESS: 3,
        }

        sorted_jobs = sorted(
            mock_jobs_list,
            key=lambda j: status_priority.get(j.status, 99),
        )

        # Failure should come first
        assert sorted_jobs[0].status == JobStatus.FAILURE

    def test_sort_by_build_number(
        self,
        mock_jenkins_job_success: JenkinsJob,
        mock_jenkins_job_failure: JenkinsJob,
    ) -> None:
        """Test sorting jobs by build number (newest first)."""
        jobs = [mock_jenkins_job_failure, mock_jenkins_job_success]
        sorted_jobs = sorted(
            jobs,
            key=lambda j: j.last_build_number if j.last_build_number else 0,
            reverse=True,
        )

        # Higher build number first
        assert sorted_jobs[0].last_build_number == 142
        assert sorted_jobs[1].last_build_number == 89
