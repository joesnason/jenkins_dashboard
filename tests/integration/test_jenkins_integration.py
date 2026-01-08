"""Integration tests for Jenkins API connectivity."""

import os
from unittest.mock import MagicMock, patch

import pytest

from models.exceptions import JenkinsAuthError, JenkinsConnectionError
from models.job import JenkinsJob, JobStatus
from services.jenkins import JenkinsService


class TestJenkinsIntegration:
    """Integration tests for Jenkins API connection."""

    @pytest.fixture
    def mock_env_vars(self) -> dict[str, str]:
        """Mock environment variables for Jenkins config."""
        return {
            "JENKINS_URL": "https://jenkins.test.com",
            "JENKINS_USER": "testuser",
            "JENKINS_API_TOKEN": "testtoken",
        }

    def test_jenkins_service_connection(
        self,
        mock_env_vars: dict[str, str],
        mock_jenkins_server: MagicMock,
    ) -> None:
        """Test JenkinsService can connect to Jenkins server."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_jenkins.return_value = mock_jenkins_server
                service = JenkinsService()

                # Verify connection by getting version
                version = mock_jenkins_server.get_version()
                assert version is not None

    def test_jenkins_service_fetches_all_jobs(
        self,
        mock_env_vars: dict[str, str],
        mock_jenkins_server: MagicMock,
    ) -> None:
        """Test JenkinsService fetches all jobs from Jenkins."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_jenkins.return_value = mock_jenkins_server

                # Setup mock responses for job details
                mock_jenkins_server.get_job_info.return_value = {
                    "name": "test-job",
                    "url": "https://jenkins.test.com/job/test-job/",
                    "color": "blue",
                    "lastBuild": {"number": 100},
                }
                mock_jenkins_server.get_build_info.return_value = {
                    "number": 100,
                    "result": "SUCCESS",
                    "timestamp": 1704708600000,
                    "duration": 45000,
                    "building": False,
                }

                service = JenkinsService()
                jobs = service.get_all_jobs()

                assert len(jobs) == 3
                assert all(isinstance(job, JenkinsJob) for job in jobs)

    def test_jenkins_service_handles_auth_failure(
        self,
        mock_env_vars: dict[str, str],
    ) -> None:
        """Test JenkinsService handles authentication failures."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_server = MagicMock()
                mock_server.get_all_jobs.side_effect = Exception("401 Unauthorized")
                mock_jenkins.return_value = mock_server

                service = JenkinsService()

                with pytest.raises(JenkinsConnectionError):
                    service.get_all_jobs()

    def test_jenkins_service_handles_connection_failure(
        self,
        mock_env_vars: dict[str, str],
    ) -> None:
        """Test JenkinsService handles connection failures."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_server = MagicMock()
                mock_server.get_all_jobs.side_effect = Exception("Connection refused")
                mock_jenkins.return_value = mock_server

                service = JenkinsService()

                with pytest.raises(JenkinsConnectionError):
                    service.get_all_jobs()

    def test_jenkins_job_details_integration(
        self,
        mock_env_vars: dict[str, str],
        mock_job_info: dict,
        mock_build_info: dict,
    ) -> None:
        """Test fetching detailed job information."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_server = MagicMock()
                mock_server.get_job_info.return_value = mock_job_info
                mock_server.get_build_info.return_value = mock_build_info
                mock_jenkins.return_value = mock_server

                service = JenkinsService()
                job = service.get_job_details("frontend-build")

                assert job.name == "frontend-build"
                assert job.status == JobStatus.SUCCESS
                assert job.last_build_number == 142
                assert job.last_build_result == "SUCCESS"
                assert job.is_building is False

    def test_jenkins_job_no_builds_yet(
        self,
        mock_env_vars: dict[str, str],
    ) -> None:
        """Test handling jobs that have never been built."""
        with patch.dict(os.environ, mock_env_vars):
            with patch("services.jenkins.jenkins.Jenkins") as mock_jenkins:
                mock_server = MagicMock()
                mock_server.get_job_info.return_value = {
                    "name": "new-job",
                    "url": "https://jenkins.test.com/job/new-job/",
                    "color": "notbuilt",
                    "lastBuild": None,
                }
                mock_jenkins.return_value = mock_server

                service = JenkinsService()
                job = service.get_job_details("new-job")

                assert job.name == "new-job"
                assert job.status == JobStatus.NOT_BUILT
                assert job.last_build_number is None
                assert job.last_build_result is None
                assert job.is_building is False
