"""Jenkins API service for the Dashboard."""

import os
from datetime import datetime

import jenkins

from models.exceptions import (
    JenkinsConnectionError,
    JenkinsJobNotFoundError,
)
from models.job import JenkinsJob, JobStatus


def color_to_status(color: str) -> JobStatus:
    """Map Jenkins color code to JobStatus enum.

    Args:
        color: Jenkins color string (e.g., 'blue', 'red', 'blue_anime')

    Returns:
        Corresponding JobStatus enum value
    """
    color_mapping: dict[str, JobStatus] = {
        "blue": JobStatus.SUCCESS,
        "red": JobStatus.FAILURE,
        "yellow": JobStatus.UNSTABLE,
        "blue_anime": JobStatus.BUILDING,
        "red_anime": JobStatus.BUILDING,
        "yellow_anime": JobStatus.BUILDING,
        "disabled": JobStatus.DISABLED,
        "notbuilt": JobStatus.NOT_BUILT,
        "aborted": JobStatus.ABORTED,
    }
    return color_mapping.get(color, JobStatus.UNKNOWN)


class JenkinsService:
    """Service for interacting with Jenkins API."""

    def __init__(self) -> None:
        """Initialize Jenkins service with environment configuration."""
        self._url = os.environ.get("JENKINS_URL", "")
        self._user = os.environ.get("JENKINS_USER", "")
        self._token = os.environ.get("JENKINS_API_TOKEN", "")
        self._server: jenkins.Jenkins | None = None

    def _get_server(self) -> jenkins.Jenkins:
        """Get or create Jenkins server connection.

        Returns:
            Jenkins server instance
        """
        if self._server is None:
            self._server = jenkins.Jenkins(
                self._url,
                username=self._user,
                password=self._token,
            )
        return self._server

    def get_all_jobs(self) -> list[JenkinsJob]:
        """Fetch all Jenkins jobs with their current status.

        Returns:
            List of JenkinsJob objects

        Raises:
            JenkinsConnectionError: If unable to connect to Jenkins
        """
        try:
            server = self._get_server()
            raw_jobs = server.get_all_jobs()

            jobs: list[JenkinsJob] = []
            for raw_job in raw_jobs:
                try:
                    job = self._parse_job(raw_job)
                    jobs.append(job)
                except Exception:
                    # Skip jobs that fail to parse
                    continue

            return jobs
        except Exception as e:
            raise JenkinsConnectionError(f"Failed to connect to Jenkins: {e}") from e

    def get_job_details(self, job_name: str) -> JenkinsJob:
        """Fetch detailed information for a specific job.

        Args:
            job_name: Name of the Jenkins job

        Returns:
            JenkinsJob object with full details

        Raises:
            JenkinsJobNotFoundError: If the job does not exist
            JenkinsConnectionError: If unable to connect to Jenkins
        """
        try:
            server = self._get_server()
            job_info = server.get_job_info(job_name)
            return self._parse_job_info(job_info)
        except jenkins.NotFoundException as e:
            raise JenkinsJobNotFoundError(f"Job '{job_name}' not found") from e
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JenkinsJobNotFoundError(f"Job '{job_name}' not found") from e
            raise JenkinsConnectionError(f"Failed to get job details: {e}") from e

    def _parse_job(self, raw_job: dict) -> JenkinsJob:
        """Parse raw job data from get_all_jobs into JenkinsJob.

        Args:
            raw_job: Raw job dictionary from Jenkins API

        Returns:
            Parsed JenkinsJob object
        """
        name = raw_job.get("name", "")
        url = raw_job.get("url", "")
        color = raw_job.get("color", "")

        status = color_to_status(color)
        is_building = "_anime" in color

        # Get full job info for build details
        try:
            job_info = self._get_server().get_job_info(name)
            return self._parse_job_info(job_info)
        except Exception:
            # Return basic info if we can't get full details
            return JenkinsJob(
                name=name,
                url=url,
                status=status,
                last_build_number=None,
                last_build_result=None,
                last_build_timestamp=None,
                last_build_duration_ms=None,
                is_building=is_building,
            )

    def _parse_job_info(self, job_info: dict) -> JenkinsJob:
        """Parse full job info into JenkinsJob.

        Args:
            job_info: Full job info dictionary from Jenkins API

        Returns:
            Parsed JenkinsJob object
        """
        name = job_info.get("name", "")
        url = job_info.get("url", "")
        color = job_info.get("color", "")

        status = color_to_status(color)
        is_building = "_anime" in color

        last_build = job_info.get("lastBuild")
        last_build_number: int | None = None
        last_build_result: str | None = None
        last_build_timestamp: datetime | None = None
        last_build_duration_ms: int | None = None

        if last_build:
            last_build_number = last_build.get("number")

            # Get build details
            try:
                build_info = self._get_server().get_build_info(name, last_build_number)
                last_build_result = build_info.get("result")
                is_building = build_info.get("building", False)

                timestamp_ms = build_info.get("timestamp")
                if timestamp_ms:
                    last_build_timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

                last_build_duration_ms = build_info.get("duration")
            except Exception:
                # Continue with partial info if build details fail
                pass

        return JenkinsJob(
            name=name,
            url=url,
            status=status,
            last_build_number=last_build_number,
            last_build_result=last_build_result,
            last_build_timestamp=last_build_timestamp,
            last_build_duration_ms=last_build_duration_ms,
            is_building=is_building,
        )
