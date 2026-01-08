"""Audit logging service for the Jenkins Dashboard."""

import json
from datetime import datetime
from pathlib import Path

from models.audit import AuditAction, AuditLogEntry, AuditResult
from models.user import User

# Default audit log path
AUDIT_LOG_PATH = Path("audit_logs/audit.log")


def log_event(
    action: AuditAction,
    result: AuditResult,
    user: User | None = None,
    ip_address: str = "",
    user_agent: str | None = None,
    details: dict[str, str] | None = None,
) -> None:
    """Log an audit event.

    Args:
        action: The type of action being logged
        result: The result of the action
        user: The user who performed the action (if authenticated)
        ip_address: The IP address of the request
        user_agent: The user agent of the request
        details: Additional details to log
    """
    entry = AuditLogEntry(
        timestamp=datetime.now(),
        action=action,
        result=result,
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )

    _write_log_entry(entry)


def _write_log_entry(entry: AuditLogEntry) -> None:
    """Write an audit log entry to the log file.

    Args:
        entry: The audit log entry to write
    """
    # Ensure log directory exists
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    log_data = {
        "id": str(entry.id),
        "timestamp": entry.timestamp.isoformat(),
        "action": entry.action.value,
        "result": entry.result.value,
        "user_id": entry.user_id,
        "user_email": entry.user_email,
        "ip_address": entry.ip_address,
        "user_agent": entry.user_agent,
        "details": entry.details,
    }

    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(log_data) + "\n")


class AuditService:
    """Service for managing audit logging."""

    def __init__(self, log_path: Path | None = None) -> None:
        """Initialize audit service.

        Args:
            log_path: Path to the audit log file
        """
        global AUDIT_LOG_PATH
        if log_path:
            AUDIT_LOG_PATH = log_path

    def log_login_success(self, user: User, ip_address: str) -> None:
        """Log a successful login event.

        Args:
            user: The user who logged in
            ip_address: The IP address of the login
        """
        log_event(
            action=AuditAction.LOGIN_SUCCESS,
            result=AuditResult.SUCCESS,
            user=user,
            ip_address=ip_address,
        )

    def log_login_failure(
        self, ip_address: str, details: dict[str, str] | None = None
    ) -> None:
        """Log a failed login event.

        Args:
            ip_address: The IP address of the login attempt
            details: Additional details about the failure
        """
        log_event(
            action=AuditAction.LOGIN_FAILURE,
            result=AuditResult.FAILURE,
            user=None,
            ip_address=ip_address,
            details=details,
        )

    def log_logout(self, user: User, ip_address: str) -> None:
        """Log a logout event.

        Args:
            user: The user who logged out
            ip_address: The IP address
        """
        log_event(
            action=AuditAction.LOGOUT,
            result=AuditResult.SUCCESS,
            user=user,
            ip_address=ip_address,
        )

    def log_access_denied(self, user: User, ip_address: str) -> None:
        """Log an access denied event.

        Args:
            user: The user who was denied access
            ip_address: The IP address
        """
        log_event(
            action=AuditAction.ACCESS_DENIED,
            result=AuditResult.BLOCKED,
            user=user,
            ip_address=ip_address,
            details={"roles": ",".join(user.roles)},
        )
