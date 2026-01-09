"""Mock authentication service for demo purposes."""

from datetime import datetime

import streamlit as st

from models.audit import AuditAction, AuditResult
from models.user import User
from services.audit import log_event

# Demo users
DEMO_USERS = {
    "pm_user": User(
        id="demo-pm-001",
        email="pm@demo.company.com",
        name="Alice Chen (PM)",
        roles=["PM"],
        login_time=datetime.now(),
    ),
    "rd_manager": User(
        id="demo-rd-002",
        email="rd.manager@demo.company.com",
        name="Bob Wang (RD Manager)",
        roles=["RD_Manager"],
        login_time=datetime.now(),
    ),
    "admin": User(
        id="demo-admin-003",
        email="admin@demo.company.com",
        name="Charlie Liu (Admin)",
        roles=["Admin"],
        login_time=datetime.now(),
    ),
    "developer": User(
        id="demo-dev-004",
        email="developer@demo.company.com",
        name="David Lee (Developer)",
        roles=["Developer"],
        login_time=datetime.now(),
    ),
}

# Allowed roles for dashboard access
ALLOWED_ROLES = {"PM", "RD_Manager", "Admin"}


def mock_authenticate_user() -> User | None:
    """Authenticate user via demo login selection.

    Returns:
        User object if authenticated, None otherwise
    """
    if "demo_user" in st.session_state and st.session_state.demo_user:
        user = DEMO_USERS.get(st.session_state.demo_user)
        if user:
            # Update login time
            return User(
                id=user.id,
                email=user.email,
                name=user.name,
                roles=user.roles,
                login_time=datetime.now(),
            )
    return None


def check_authorization(user: User) -> bool:
    """Check if a user is authorized to access the dashboard.

    Args:
        user: The user to check

    Returns:
        True if the user has an allowed role, False otherwise
    """
    user_roles = set(user.roles)
    return bool(user_roles & ALLOWED_ROLES)


def mock_logout_user(user: User, ip_address: str = "") -> None:
    """Log out the demo user.

    Args:
        user: The user to log out
        ip_address: The IP address for audit logging
    """
    log_event(
        action=AuditAction.LOGOUT,
        result=AuditResult.SUCCESS,
        user=user,
        ip_address=ip_address,
    )

    # Clear session state
    if "demo_user" in st.session_state:
        del st.session_state.demo_user
    if "login_logged" in st.session_state:
        del st.session_state.login_logged


def get_client_ip() -> str:
    """Get mock client IP address.

    Returns:
        Mock client IP address string
    """
    return "192.168.1.100"


def render_demo_login_page() -> None:
    """Render the demo login page with user selection."""
    st.title("Jenkins Dashboard")
    st.markdown("---")

    # Demo mode banner
    st.info("**Demo Mode** - Select a user profile to explore the dashboard")

    st.markdown("### Select Demo User")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Authorized Users")

        if st.button("Login as PM", type="primary", use_container_width=True):
            st.session_state.demo_user = "pm_user"
            st.rerun()

        if st.button("Login as RD Manager", type="primary", use_container_width=True):
            st.session_state.demo_user = "rd_manager"
            st.rerun()

        if st.button("Login as Admin", type="primary", use_container_width=True):
            st.session_state.demo_user = "admin"
            st.rerun()

    with col2:
        st.markdown("#### Unauthorized User")

        if st.button("Login as Developer", type="secondary", use_container_width=True):
            st.session_state.demo_user = "developer"
            st.rerun()

        st.caption("(Will show access denied page)")

    st.markdown("---")
    st.markdown("##### Role Permissions")
    st.markdown("""
    | Role | Access |
    |------|--------|
    | PM | Full dashboard access |
    | RD Manager | Full dashboard access |
    | Admin | Full dashboard access |
    | Developer | Access denied |
    """)


def render_access_denied_page(user: User) -> None:
    """Render the access denied page for unauthorized users.

    Args:
        user: The unauthorized user
    """
    st.title("Access Denied")
    st.error(
        f"Sorry, {user.name}, you don't have permission to access this dashboard."
    )
    st.markdown("---")
    st.markdown("This dashboard is only accessible to PM, RD Manager, and Admin roles.")
    st.markdown(f"Your current roles: {', '.join(user.roles) or 'None'}")
    st.markdown("---")
    st.markdown("Please contact your administrator if you believe this is an error.")

    if st.button("Back to Login"):
        mock_logout_user(user, get_client_ip())
        st.rerun()
