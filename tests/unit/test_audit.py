"""Unit tests for audit service."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from models.audit import AuditAction, AuditResult
from models.user import User
from services.audit import AuditService, log_event


class TestLogEvent:
    """Tests for log_event function."""

    def test_log_event_creates_entry(self, mock_user: User) -> None:
        """Test that log_event creates an audit entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"

            with patch("services.audit.AUDIT_LOG_PATH", log_file):
                log_event(
                    action=AuditAction.LOGIN_SUCCESS,
                    result=AuditResult.SUCCESS,
                    user=mock_user,
                    ip_address="192.168.1.100",
                )

                # Verify log file was created
                assert log_file.exists()

                # Read and parse the log entry
                with open(log_file) as f:
                    line = f.readline()
                    entry = json.loads(line)

                assert entry["action"] == "login_success"
                assert entry["result"] == "success"
                assert entry["user_id"] == "user123"
                assert entry["user_email"] == "pm@company.com"
                assert entry["ip_address"] == "192.168.1.100"

    def test_log_event_without_user(self) -> None:
        """Test log_event for unauthenticated actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"

            with patch("services.audit.AUDIT_LOG_PATH", log_file):
                log_event(
                    action=AuditAction.LOGIN_FAILURE,
                    result=AuditResult.FAILURE,
                    user=None,
                    ip_address="192.168.1.100",
                    details={"reason": "Invalid credentials"},
                )

                with open(log_file) as f:
                    line = f.readline()
                    entry = json.loads(line)

                assert entry["action"] == "login_failure"
                assert entry["result"] == "failure"
                assert entry["user_id"] is None
                assert entry["details"]["reason"] == "Invalid credentials"

    def test_log_event_with_details(self, mock_user: User) -> None:
        """Test log_event with additional details."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"

            with patch("services.audit.AUDIT_LOG_PATH", log_file):
                log_event(
                    action=AuditAction.ACCESS_DENIED,
                    result=AuditResult.BLOCKED,
                    user=mock_user,
                    ip_address="192.168.1.100",
                    details={"required_role": "Admin", "user_role": "Developer"},
                )

                with open(log_file) as f:
                    line = f.readline()
                    entry = json.loads(line)

                assert entry["action"] == "access_denied"
                assert entry["result"] == "blocked"
                assert entry["details"]["required_role"] == "Admin"


class TestAuditService:
    """Tests for AuditService class."""

    def test_audit_service_log_login(self, mock_user: User) -> None:
        """Test AuditService logging login events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            service = AuditService(log_path=log_file)

            service.log_login_success(mock_user, "192.168.1.100")

            with open(log_file) as f:
                line = f.readline()
                entry = json.loads(line)

            assert entry["action"] == "login_success"
            assert entry["user_id"] == "user123"

    def test_audit_service_log_logout(self, mock_user: User) -> None:
        """Test AuditService logging logout events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            service = AuditService(log_path=log_file)

            service.log_logout(mock_user, "192.168.1.100")

            with open(log_file) as f:
                line = f.readline()
                entry = json.loads(line)

            assert entry["action"] == "logout"
            assert entry["user_id"] == "user123"

    def test_audit_service_log_access_denied(self, mock_unauthorized_user: User) -> None:
        """Test AuditService logging access denied events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            service = AuditService(log_path=log_file)

            service.log_access_denied(mock_unauthorized_user, "192.168.1.100")

            with open(log_file) as f:
                line = f.readline()
                entry = json.loads(line)

            assert entry["action"] == "access_denied"
            assert entry["result"] == "blocked"
