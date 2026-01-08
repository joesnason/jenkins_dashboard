"""Job-related models for the Jenkins Dashboard."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class JobStatus(Enum):
    """Enumeration of possible Jenkins job statuses."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNSTABLE = "unstable"
    BUILDING = "building"
    DISABLED = "disabled"
    NOT_BUILT = "not_built"
    ABORTED = "aborted"
    UNKNOWN = "unknown"


@dataclass
class JenkinsJob:
    """Represents a Jenkins build job with its current status."""

    name: str
    url: str
    status: JobStatus
    last_build_number: int | None
    last_build_result: str | None
    last_build_timestamp: datetime | None
    last_build_duration_ms: int | None
    is_building: bool
