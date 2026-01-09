"""Main Streamlit application for Jenkins Build Status Dashboard."""

import os
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from components.job_table import render_job_table
from components.status_bar import render_connection_status, render_status_bar
from models.exceptions import JenkinsConnectionError
from models.user import User
from services.audit import AuditService
from services.dashboard import DashboardService

# Load environment variables
load_dotenv()

# Check if running in demo mode
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    from services.mock_auth import (
        check_authorization,
        get_client_ip,
        mock_authenticate_user as authenticate_user,
        mock_logout_user as logout_user,
        render_access_denied_page,
        render_demo_login_page as render_login_page,
    )
    from services.mock_jenkins import MockJenkinsService
else:
    from services.auth import (
        authenticate_user,
        check_authorization,
        get_client_ip,
        logout_user,
        render_access_denied_page,
        render_login_page,
    )
    from services.jenkins import JenkinsService

# Page configuration
st.set_page_config(
    page_title="Jenkins Dashboard",
    page_icon=":hammer_and_wrench:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Constants
REFRESH_INTERVAL = 30  # seconds

# Audit service
audit_service = AuditService()


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if "cached_jobs" not in st.session_state:
        st.session_state.cached_jobs = []
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = True
    if "login_logged" not in st.session_state:
        st.session_state.login_logged = False


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_jobs() -> tuple[list, bool, str | None]:
    """Fetch all Jenkins jobs with caching.

    Returns:
        Tuple of (jobs list, is_available, error_message)
    """
    try:
        if DEMO_MODE:
            service = MockJenkinsService()
        else:
            service = JenkinsService()
        jobs = service.get_all_jobs()
        return jobs, True, None
    except JenkinsConnectionError as e:
        return [], False, str(e)


def refresh_jobs() -> None:
    """Force refresh jobs by clearing cache."""
    fetch_jobs.clear()
    st.session_state.last_refresh = datetime.now()


def render_header(user: User) -> None:
    """Render the dashboard header.

    Args:
        user: The authenticated user
    """
    if DEMO_MODE:
        st.info("**Demo Mode** - Using mock data for demonstration")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.title("Jenkins Build Status Dashboard")
        st.caption(f"Welcome, {user.name}")

    with col2:
        # Refresh button
        if st.button("Refresh Now", type="primary"):
            refresh_jobs()
            st.rerun()

    with col3:
        # Logout button
        if st.button("Logout"):
            logout_user(user, get_client_ip())
            st.rerun()


def render_refresh_controls() -> None:
    """Render auto-refresh controls."""
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        st.session_state.auto_refresh = st.checkbox(
            "Auto-refresh",
            value=st.session_state.auto_refresh,
        )

    with col2:
        if st.session_state.auto_refresh:
            st.caption(f"Refreshing every {REFRESH_INTERVAL}s")


def render_dashboard(user: User) -> None:
    """Render the main dashboard.

    Args:
        user: The authenticated user
    """
    # Render header with user info
    render_header(user)

    # Fetch jobs
    jobs, is_available, error_message = fetch_jobs()

    # Update cached jobs if available
    if is_available and jobs:
        st.session_state.cached_jobs = jobs

    # Use cached jobs if Jenkins is unavailable
    display_jobs = jobs if is_available else st.session_state.cached_jobs

    # Create dashboard service with current state
    dashboard_service = DashboardService(
        jobs=display_jobs,
        is_available=is_available,
        error_message=error_message,
    )
    state = dashboard_service.get_dashboard_state()

    # Render connection status
    render_connection_status(state)

    # Render status bar
    render_status_bar(state)

    st.markdown("---")

    # Render refresh controls
    render_refresh_controls()

    st.markdown("---")

    # Render job table
    render_job_table(display_jobs)

    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
        if time_since_refresh >= REFRESH_INTERVAL:
            refresh_jobs()
            st.rerun()
        else:
            # Show countdown
            remaining = REFRESH_INTERVAL - time_since_refresh
            st.caption(f"Next refresh in {remaining}s")

            # Use a placeholder to trigger rerun after interval
            time.sleep(1)
            st.rerun()


def main() -> None:
    """Main application entry point."""
    init_session_state()

    # Check authentication
    user = authenticate_user()

    if user is None:
        # User is not logged in
        render_login_page()
        st.stop()

    # Log login if not already logged
    if not st.session_state.login_logged:
        audit_service.log_login_success(user, get_client_ip())
        st.session_state.login_logged = True

    # Check authorization
    if not check_authorization(user):
        # User is logged in but not authorized
        audit_service.log_access_denied(user, get_client_ip())
        render_access_denied_page(user)
        st.stop()

    # User is authenticated and authorized - render dashboard
    render_dashboard(user)


if __name__ == "__main__":
    main()
