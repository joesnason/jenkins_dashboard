"""Services package for the Jenkins Dashboard."""

import os

from services.audit import AuditService, log_event
from services.dashboard import DashboardService, calculate_statistics

# Conditionally import based on demo mode
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    from services.mock_auth import (
        check_authorization,
        mock_authenticate_user as authenticate_user,
        mock_logout_user as logout_user,
    )
    from services.mock_jenkins import MockJenkinsService as JenkinsService
else:
    from services.auth import authenticate_user, check_authorization, logout_user
    from services.jenkins import JenkinsService, color_to_status

__all__ = [
    "AuditService",
    "DashboardService",
    "JenkinsService",
    "authenticate_user",
    "calculate_statistics",
    "check_authorization",
    "log_event",
    "logout_user",
]
