"""Unit tests for Jenkins service."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.models.exceptions import JenkinsAuthError, JenkinsConnectionError
from src.models.job import JenkinsJob, JobStatus
from src.services.jenkins import JenkinsService, color_to_status


class TestColorToStatus:
    """Tests for color_to_status mapping function."""

    def test_blue_maps_to_success(self) -> None:
        """Test blue color maps to SUCCESS status."""
        assert color_to_status("blue") == JobStatus.SUCCESS

    def test_red_maps_to_failure(self) -> None:
        """Test red color maps to FAILURE status."""
        assert color_to_status("red") == JobStatus.FAILURE

    def test_yellow_maps_to_unstable(self) -> None:
        """Test yellow color maps to UNSTABLE status."""
        assert color_to_status("yellow") == JobStatus.UNSTABLE

    def test_anime_colors_map_to_building(self) -> None:
        """Test anime colors map to BUILDING status."""
        assert color_to_status("blue_anime") == JobStatus.BUILDING
        assert color_to_status("red_anime") == JobStatus.BUILDING
        assert color_to_status("yellow_anime") == JobStatus.BUILDING

    def test_disabled_maps_to_disabled(self) -> None:
        """Test disabled color maps to DISABLED status."""
        assert color_to_status("disabled") == JobStatus.DISABLED

    def test_notbuilt_maps_to_not_built(self) -> None:
        """Test notbuilt color maps to NOT_BUILT status."""
        assert color_to_status("notbuilt") == JobStatus.NOT_BUILT

    def test_aborted_maps_to_aborted(self) -> None:
        """Test aborted color maps to ABORTED status."""
        assert color_to_status("aborted") == JobStatus.ABORTED

    def test_unknown_color_maps_to_unknown(self) -> None:
        """Test unknown color maps to UNKNOWN status."""
        assert color_to_status("some_random_color") == JobStatus.UNKNOWN
        assert color_to_status("") == JobStatus.UNKNOWN
        assert color_to_status("grey") == JobStatus.UNKNOWN


class TestJenkinsService:
    """Tests for JenkinsService class."""

    @pytest.fixture
    def jenkins_service(self) -> JenkinsService:
        """Create a JenkinsService instance with mock config."""
        with patch.dict(
            "os.environ",
            {
                "JENKINS_URL": "https://jenkins.test.com",
                "JENKINS_USER": "testuser",
                "JENKINS_API_TOKEN": "testtoken",
            },
        ):
            return JenkinsService()

    def test_get_all_jobs_returns_job_list(
        self,
        jenkins_service: JenkinsService,
        mock_jenkins_server: MagicMock,
    ) -> None:
        """Test get_all_jobs returns a list of JenkinsJob objects."""
        jenkins_service._server = mock_jenkins_server

        # Mock get_job_info to return job details
        mock_jenkins_server.get_job_info.return_value = {
            "name": "frontend-build",
            "url": "https://jenkins.company.com/job/frontend-build/",
            "color": "blue",
            "lastBuild": {"number": 142},
        }

        mock_jenkins_server.get_build_info.return_value = {
            "number": 142,
            "result": "SUCCESS",
            "timestamp": 1704708600000,
            "duration": 45000,
            "building": False,
        }

        jobs = jenkins_service.get_all_jobs()

        assert isinstance(jobs, list)
        assert len(jobs) == 3
        for job in jobs:
            assert isinstance(job, JenkinsJob)

    def test_get_all_jobs_handles_connection_error(
        self,
        jenkins_service: JenkinsService,
        mock_jenkins_server: MagicMock,
    ) -> None:
        """Test get_all_jobs raises JenkinsConnectionError on connection failure."""
        jenkins_service._server = mock_jenkins_server
        mock_jenkins_server.get_all_jobs.side_effect = Exception("Connection refused")

        with pytest.raises(JenkinsConnectionError):
            jenkins_service.get_all_jobs()

    def test_get_job_details_returns_job(
        self,
        jenkins_service: JenkinsService,
        mock_jenkins_server: MagicMock,
        mock_job_info: dict,
        mock_build_info: dict,
    ) -> None:
        """Test get_job_details returns a JenkinsJob object."""
        jenkins_service._server = mock_jenkins_server
        mock_jenkins_server.get_job_info.return_value = mock_job_info
        mock_jenkins_server.get_build_info.return_value = mock_build_info

        job = jenkins_service.get_job_details("frontend-build")

        assert isinstance(job, JenkinsJob)
        assert job.name == "frontend-build"
        assert job.status == JobStatus.SUCCESS
        assert job.last_build_number == 142

    def test_color_detection_for_building(
        self,
        jenkins_service: JenkinsService,
        mock_jenkins_server: MagicMock,
    ) -> None:
        """Test that anime colors are correctly detected as building."""
        jenkins_service._server = mock_jenkins_server

        mock_jenkins_server.get_job_info.return_value = {
            "name": "building-job",
            "url": "https://jenkins.test.com/job/building-job/",
            "color": "blue_anime",
            "lastBuild": {"number": 100},
        }

        mock_jenkins_server.get_build_info.return_value = {
            "number": 100,
            "result": None,
            "timestamp": 1704708600000,
            "duration": 0,
            "building": True,
        }

        job = jenkins_service.get_job_details("building-job")

        assert job.status == JobStatus.BUILDING
        assert job.is_building is True
