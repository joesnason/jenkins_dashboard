"""Unit tests for data models."""

from datetime import datetime

import pytest

from src.models.audit import AuditAction, AuditLogEntry, AuditResult
from src.models.job import JenkinsJob, JobStatus
from src.models.state import DashboardState
from src.models.user import User


class TestJenkinsJob:
    """Tests for JenkinsJob model."""

    def test_jenkins_job_creation(self) -> None:
        """Test creating a JenkinsJob with all fields."""
        job = JenkinsJob(
            name="test-job",
            url="https://jenkins.example.com/job/test-job/",
            status=JobStatus.SUCCESS,
            last_build_number=100,
            last_build_result="SUCCESS",
            last_build_timestamp=datetime(2026, 1, 8, 10, 0, 0),
            last_build_duration_ms=30000,
            is_building=False,
        )

        assert job.name == "test-job"
        assert job.url == "https://jenkins.example.com/job/test-job/"
        assert job.status == JobStatus.SUCCESS
        assert job.last_build_number == 100
        assert job.last_build_result == "SUCCESS"
        assert job.last_build_timestamp == datetime(2026, 1, 8, 10, 0, 0)
        assert job.last_build_duration_ms == 30000
        assert job.is_building is False

    def test_jenkins_job_with_none_values(self) -> None:
        """Test creating a JenkinsJob with optional None values."""
        job = JenkinsJob(
            name="new-job",
            url="https://jenkins.example.com/job/new-job/",
            status=JobStatus.NOT_BUILT,
            last_build_number=None,
            last_build_result=None,
            last_build_timestamp=None,
            last_build_duration_ms=None,
            is_building=False,
        )

        assert job.name == "new-job"
        assert job.status == JobStatus.NOT_BUILT
        assert job.last_build_number is None
        assert job.last_build_result is None
        assert job.last_build_timestamp is None
        assert job.last_build_duration_ms is None

    def test_jenkins_job_building_status(self) -> None:
        """Test JenkinsJob with building status."""
        job = JenkinsJob(
            name="building-job",
            url="https://jenkins.example.com/job/building-job/",
            status=JobStatus.BUILDING,
            last_build_number=50,
            last_build_result=None,
            last_build_timestamp=datetime(2026, 1, 8, 11, 0, 0),
            last_build_duration_ms=None,
            is_building=True,
        )

        assert job.status == JobStatus.BUILDING
        assert job.is_building is True
        assert job.last_build_result is None


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_status_values_exist(self) -> None:
        """Test that all expected status values exist."""
        expected_statuses = [
            "SUCCESS",
            "FAILURE",
            "UNSTABLE",
            "BUILDING",
            "DISABLED",
            "NOT_BUILT",
            "ABORTED",
            "UNKNOWN",
        ]

        for status_name in expected_statuses:
            assert hasattr(JobStatus, status_name)

    def test_status_values(self) -> None:
        """Test JobStatus enum values."""
        assert JobStatus.SUCCESS.value == "success"
        assert JobStatus.FAILURE.value == "failure"
        assert JobStatus.UNSTABLE.value == "unstable"
        assert JobStatus.BUILDING.value == "building"
        assert JobStatus.DISABLED.value == "disabled"
        assert JobStatus.NOT_BUILT.value == "not_built"
        assert JobStatus.ABORTED.value == "aborted"
        assert JobStatus.UNKNOWN.value == "unknown"


class TestDashboardState:
    """Tests for DashboardState model."""

    def test_dashboard_state_creation(
        self, mock_jobs_list: list[JenkinsJob]
    ) -> None:
        """Test creating a DashboardState."""
        state = DashboardState(
            jobs=mock_jobs_list,
            last_refresh=datetime(2026, 1, 8, 11, 5, 0),
            is_jenkins_available=True,
            error_message=None,
            total_jobs=3,
            success_count=1,
            failure_count=1,
            building_count=1,
        )

        assert len(state.jobs) == 3
        assert state.is_jenkins_available is True
        assert state.error_message is None
        assert state.total_jobs == 3
        assert state.success_count == 1
        assert state.failure_count == 1
        assert state.building_count == 1

    def test_dashboard_state_with_error(self) -> None:
        """Test DashboardState when Jenkins is unavailable."""
        state = DashboardState(
            jobs=[],
            last_refresh=datetime(2026, 1, 8, 10, 0, 0),
            is_jenkins_available=False,
            error_message="Connection refused",
            total_jobs=0,
            success_count=0,
            failure_count=0,
            building_count=0,
        )

        assert state.is_jenkins_available is False
        assert state.error_message == "Connection refused"
        assert state.total_jobs == 0


class TestUser:
    """Tests for User model."""

    def test_user_creation(self) -> None:
        """Test creating a User."""
        user = User(
            id="user123",
            email="pm@company.com",
            name="Test PM",
            roles=["PM"],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )

        assert user.id == "user123"
        assert user.email == "pm@company.com"
        assert user.name == "Test PM"
        assert user.roles == ["PM"]

    def test_user_with_multiple_roles(self) -> None:
        """Test User with multiple roles."""
        user = User(
            id="admin123",
            email="admin@company.com",
            name="Admin User",
            roles=["PM", "RD_Manager", "Admin"],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )

        assert len(user.roles) == 3
        assert "PM" in user.roles
        assert "RD_Manager" in user.roles
        assert "Admin" in user.roles


class TestAuditLogEntry:
    """Tests for AuditLogEntry model."""

    def test_audit_log_entry_creation(self) -> None:
        """Test creating an AuditLogEntry."""
        entry = AuditLogEntry(
            timestamp=datetime(2026, 1, 8, 10, 0, 0),
            action=AuditAction.LOGIN_SUCCESS,
            result=AuditResult.SUCCESS,
            user_id="user123",
            user_email="pm@company.com",
            ip_address="192.168.1.100",
        )

        assert entry.action == AuditAction.LOGIN_SUCCESS
        assert entry.result == AuditResult.SUCCESS
        assert entry.user_id == "user123"
        assert entry.user_email == "pm@company.com"
        assert entry.ip_address == "192.168.1.100"
        assert entry.id is not None

    def test_audit_log_entry_with_details(self) -> None:
        """Test AuditLogEntry with additional details."""
        entry = AuditLogEntry(
            timestamp=datetime(2026, 1, 8, 10, 0, 0),
            action=AuditAction.ACCESS_DENIED,
            result=AuditResult.BLOCKED,
            user_id="user789",
            user_email="dev@company.com",
            ip_address="192.168.1.101",
            user_agent="Mozilla/5.0",
            details={"reason": "Insufficient role", "required_role": "PM"},
        )

        assert entry.action == AuditAction.ACCESS_DENIED
        assert entry.result == AuditResult.BLOCKED
        assert entry.details is not None
        assert entry.details["reason"] == "Insufficient role"
