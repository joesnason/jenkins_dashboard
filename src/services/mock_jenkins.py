"""Mock Jenkins service for demo purposes."""

import random
from datetime import datetime, timedelta

from models.job import JenkinsJob, JobStatus


# Demo job configurations
DEMO_JOBS = [
    {"name": "frontend-build", "status": JobStatus.SUCCESS},
    {"name": "backend-api", "status": JobStatus.SUCCESS},
    {"name": "auth-service", "status": JobStatus.FAILURE},
    {"name": "payment-gateway", "status": JobStatus.BUILDING},
    {"name": "user-service", "status": JobStatus.SUCCESS},
    {"name": "notification-service", "status": JobStatus.UNSTABLE},
    {"name": "analytics-pipeline", "status": JobStatus.SUCCESS},
    {"name": "mobile-app-ios", "status": JobStatus.SUCCESS},
    {"name": "mobile-app-android", "status": JobStatus.FAILURE},
    {"name": "infrastructure-terraform", "status": JobStatus.SUCCESS},
    {"name": "database-migration", "status": JobStatus.DISABLED},
    {"name": "e2e-tests", "status": JobStatus.SUCCESS},
    {"name": "performance-tests", "status": JobStatus.ABORTED},
    {"name": "security-scan", "status": JobStatus.SUCCESS},
    {"name": "docker-registry-push", "status": JobStatus.NOT_BUILT},
]


def _generate_mock_job(name: str, status: JobStatus, base_build: int) -> JenkinsJob:
    """Generate a mock JenkinsJob with realistic data.

    Args:
        name: Job name
        status: Job status
        base_build: Base build number

    Returns:
        Mock JenkinsJob instance
    """
    # Random build number around the base
    build_number = base_build + random.randint(0, 50)

    # Random timestamp within last 24 hours
    hours_ago = random.randint(0, 24)
    minutes_ago = random.randint(0, 59)
    timestamp = datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)

    # Random duration between 30 seconds and 10 minutes
    duration_ms = random.randint(30_000, 600_000)

    # Map status to result string
    result_map = {
        JobStatus.SUCCESS: "SUCCESS",
        JobStatus.FAILURE: "FAILURE",
        JobStatus.UNSTABLE: "UNSTABLE",
        JobStatus.ABORTED: "ABORTED",
        JobStatus.BUILDING: None,
        JobStatus.DISABLED: None,
        JobStatus.NOT_BUILT: None,
        JobStatus.UNKNOWN: None,
    }

    return JenkinsJob(
        name=name,
        url=f"https://jenkins.demo.company.com/job/{name}/",
        status=status,
        last_build_number=build_number if status != JobStatus.NOT_BUILT else None,
        last_build_result=result_map.get(status),
        last_build_timestamp=timestamp if status != JobStatus.NOT_BUILT else None,
        last_build_duration_ms=duration_ms if status not in (
            JobStatus.BUILDING, JobStatus.NOT_BUILT, JobStatus.DISABLED
        ) else None,
        is_building=status == JobStatus.BUILDING,
    )


class MockJenkinsService:
    """Mock Jenkins service for demo/testing purposes."""

    def __init__(self, randomize: bool = False) -> None:
        """Initialize the mock service.

        Args:
            randomize: If True, randomize job statuses on each call
        """
        self._randomize = randomize
        self._base_build = 100

    def get_all_jobs(self) -> list[JenkinsJob]:
        """Get all mock Jenkins jobs.

        Returns:
            List of mock JenkinsJob objects
        """
        jobs = []
        for i, job_config in enumerate(DEMO_JOBS):
            status = job_config["status"]

            # Optionally randomize status for more dynamic demo
            if self._randomize and random.random() < 0.1:
                status = random.choice([
                    JobStatus.SUCCESS,
                    JobStatus.FAILURE,
                    JobStatus.BUILDING,
                ])

            job = _generate_mock_job(
                name=job_config["name"],
                status=status,
                base_build=self._base_build + (i * 10),
            )
            jobs.append(job)

        return jobs

    def get_job_details(self, job_name: str) -> JenkinsJob:
        """Get details for a specific mock job.

        Args:
            job_name: Name of the job

        Returns:
            Mock JenkinsJob object
        """
        for job_config in DEMO_JOBS:
            if job_config["name"] == job_name:
                return _generate_mock_job(
                    name=job_name,
                    status=job_config["status"],
                    base_build=self._base_build,
                )

        # Return a default job if not found
        return _generate_mock_job(
            name=job_name,
            status=JobStatus.UNKNOWN,
            base_build=self._base_build,
        )
