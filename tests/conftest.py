"""Shared pytest fixtures for the Jenkins Dashboard tests."""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.job import JenkinsJob, JobStatus
from models.user import User


@pytest.fixture
def mock_user() -> User:
    """Create a mock authenticated user."""
    return User(
        id="user123",
        email="pm@company.com",
        name="Test PM",
        roles=["PM"],
        login_time=datetime(2026, 1, 8, 10, 0, 0),
    )


@pytest.fixture
def mock_rd_manager() -> User:
    """Create a mock RD Manager user."""
    return User(
        id="user456",
        email="rdm@company.com",
        name="Test RD Manager",
        roles=["RD_Manager"],
        login_time=datetime(2026, 1, 8, 10, 0, 0),
    )


@pytest.fixture
def mock_unauthorized_user() -> User:
    """Create a mock user without dashboard access."""
    return User(
        id="user789",
        email="dev@company.com",
        name="Test Developer",
        roles=["Developer"],
        login_time=datetime(2026, 1, 8, 10, 0, 0),
    )


@pytest.fixture
def mock_jenkins_job_success() -> JenkinsJob:
    """Create a mock successful Jenkins job."""
    return JenkinsJob(
        name="frontend-build",
        url="https://jenkins.company.com/job/frontend-build/",
        status=JobStatus.SUCCESS,
        last_build_number=142,
        last_build_result="SUCCESS",
        last_build_timestamp=datetime(2026, 1, 8, 10, 30, 0),
        last_build_duration_ms=45000,
        is_building=False,
    )


@pytest.fixture
def mock_jenkins_job_failure() -> JenkinsJob:
    """Create a mock failed Jenkins job."""
    return JenkinsJob(
        name="backend-tests",
        url="https://jenkins.company.com/job/backend-tests/",
        status=JobStatus.FAILURE,
        last_build_number=89,
        last_build_result="FAILURE",
        last_build_timestamp=datetime(2026, 1, 8, 9, 45, 0),
        last_build_duration_ms=120000,
        is_building=False,
    )


@pytest.fixture
def mock_jenkins_job_building() -> JenkinsJob:
    """Create a mock building Jenkins job."""
    return JenkinsJob(
        name="api-deploy",
        url="https://jenkins.company.com/job/api-deploy/",
        status=JobStatus.BUILDING,
        last_build_number=56,
        last_build_result=None,
        last_build_timestamp=datetime(2026, 1, 8, 11, 0, 0),
        last_build_duration_ms=None,
        is_building=True,
    )


@pytest.fixture
def mock_jenkins_job_not_built() -> JenkinsJob:
    """Create a mock Jenkins job that has never been built."""
    return JenkinsJob(
        name="new-project",
        url="https://jenkins.company.com/job/new-project/",
        status=JobStatus.NOT_BUILT,
        last_build_number=None,
        last_build_result=None,
        last_build_timestamp=None,
        last_build_duration_ms=None,
        is_building=False,
    )


@pytest.fixture
def mock_jobs_list(
    mock_jenkins_job_success: JenkinsJob,
    mock_jenkins_job_failure: JenkinsJob,
    mock_jenkins_job_building: JenkinsJob,
) -> list[JenkinsJob]:
    """Create a list of mock Jenkins jobs."""
    return [
        mock_jenkins_job_success,
        mock_jenkins_job_failure,
        mock_jenkins_job_building,
    ]


@pytest.fixture
def mock_jenkins_server() -> MagicMock:
    """Create a mock Jenkins server instance."""
    server = MagicMock()
    server.get_version.return_value = "2.400.1"
    server.get_all_jobs.return_value = [
        {
            "name": "frontend-build",
            "url": "https://jenkins.company.com/job/frontend-build/",
            "color": "blue",
        },
        {
            "name": "backend-tests",
            "url": "https://jenkins.company.com/job/backend-tests/",
            "color": "red",
        },
        {
            "name": "api-deploy",
            "url": "https://jenkins.company.com/job/api-deploy/",
            "color": "blue_anime",
        },
    ]
    return server


@pytest.fixture
def mock_job_info() -> dict:
    """Create mock Jenkins job info response."""
    return {
        "name": "frontend-build",
        "url": "https://jenkins.company.com/job/frontend-build/",
        "color": "blue",
        "lastBuild": {"number": 142},
        "lastCompletedBuild": {"number": 142},
        "lastSuccessfulBuild": {"number": 142},
        "lastFailedBuild": {"number": 140},
    }


@pytest.fixture
def mock_build_info() -> dict:
    """Create mock Jenkins build info response."""
    return {
        "number": 142,
        "result": "SUCCESS",
        "timestamp": 1704708600000,
        "duration": 45000,
        "building": False,
        "displayName": "#142",
        "url": "https://jenkins.company.com/job/frontend-build/142/",
    }
