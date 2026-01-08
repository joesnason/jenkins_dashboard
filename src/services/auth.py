"""Authentication service for the Jenkins Dashboard."""

from datetime import datetime

import streamlit as st

from src.models.audit import AuditAction, AuditResult
from src.models.user import User
from src.services.audit import log_event

# Allowed roles for dashboard access
ALLOWED_ROLES = {"PM", "RD_Manager", "Admin"}


def authenticate_user() -> User | None:
    """Authenticate the current user from Streamlit SSO.

    Returns:
        User object if authenticated, None otherwise
    """
    if not hasattr(st, "user") or not st.user.is_logged_in:
        return None

    user_id = st.user.get("sub", "")
    email = st.user.get("email", "")
    name = st.user.get("name", "")
    groups = st.user.get("groups", [])

    return User(
        id=user_id,
        email=email,
        name=name,
        roles=groups,
        login_time=datetime.now(),
    )


def check_authorization(user: User) -> bool:
    """Check if a user is authorized to access the dashboard.

    Args:
        user: The user to check

    Returns:
        True if the user has an allowed role, False otherwise
    """
    user_roles = set(user.roles)
    return bool(user_roles & ALLOWED_ROLES)


def logout_user(user: User, ip_address: str = "") -> None:
    """Log out the current user.

    Args:
        user: The user to log out
        ip_address: The IP address for audit logging
    """
    # Log the logout event
    log_event(
        action=AuditAction.LOGOUT,
        result=AuditResult.SUCCESS,
        user=user,
        ip_address=ip_address,
    )

    # Call Streamlit logout
    st.logout()


def get_client_ip() -> str:
    """Get the client IP address from the request.

    Returns:
        Client IP address string
    """
    # In Streamlit, we can try to get this from headers
    # This is a simplified version - in production you'd want to check
    # X-Forwarded-For header for proxied requests
    try:
        # Streamlit doesn't directly expose client IP
        # This is a placeholder for proper implementation
        return "unknown"
    except Exception:
        return "unknown"


def render_login_page() -> None:
    """Render the login page for unauthenticated users."""
    st.title("Jenkins Dashboard")
    st.markdown("---")
    st.markdown("### Please log in to continue")
    st.markdown("Use your company SSO credentials to access the dashboard.")

    if st.button("Login with Company SSO", type="primary"):
        st.login()


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
    st.markdown("This dashboard is only accessible to PM and RD Manager roles.")
    st.markdown(f"Your current roles: {', '.join(user.roles) or 'None'}")
    st.markdown("---")
    st.markdown("Please contact your administrator if you believe this is an error.")

    if st.button("Logout"):
        logout_user(user, get_client_ip())
        st.rerun()
