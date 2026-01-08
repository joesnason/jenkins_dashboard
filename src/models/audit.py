"""Audit-related models for the Jenkins Dashboard."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class AuditAction(Enum):
    """Enumeration of audit log action types."""

    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    SESSION_EXPIRED = "session_expired"


class AuditResult(Enum):
    """Enumeration of audit action results."""

    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"


@dataclass
class AuditLogEntry:
    """Represents an audit log entry for security tracking."""

    timestamp: datetime
    action: AuditAction
    result: AuditResult
    user_id: str | None = None
    user_email: str | None = None
    ip_address: str = ""
    user_agent: str | None = None
    details: dict[str, str] | None = None
    id: UUID = field(default_factory=uuid4)
