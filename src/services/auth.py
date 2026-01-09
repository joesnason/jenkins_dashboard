"""Authentication service for the Jenkins Dashboard."""

from datetime import datetime

import streamlit as st

from models.audit import AuditAction, AuditResult
from models.user import User
from services.audit import log_event
from services.whitelist import WhitelistService

whitelist_service = WhitelistService()


def authenticate_user() -> User | None:
    """Authenticate the current user from Streamlit SSO.

    Returns:
        User object if authenticated, None otherwise.
    """
    if not hasattr(st, "user") or not st.user.is_logged_in:
        return None

    email = st.user.get("email", "")
    is_admin = whitelist_service.is_admin(email)

    return User(
        id=st.user.get("sub", ""),
        email=email,
        name=st.user.get("name", ""),
        roles=st.user.get("groups", []),
        login_time=datetime.now(),
        is_admin=is_admin,
    )


def check_authorization(user: User) -> bool:
    """Check if user email is in the whitelist.

    Args:
        user: The user to check.

    Returns:
        True if user is whitelisted, False otherwise.
    """
    return whitelist_service.is_user_allowed(user.email)


def logout_user(user: User, ip_address: str = "") -> None:
    """Log out the current user.

    Args:
        user: The user to log out.
        ip_address: The IP address for audit logging.
    """
    log_event(
        action=AuditAction.LOGOUT,
        result=AuditResult.SUCCESS,
        user=user,
        ip_address=ip_address,
    )

    st.logout()


def get_client_ip() -> str:
    """Get the client IP address from the request.

    Returns:
        Client IP address string.
    """
    try:
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
        user: The unauthorized user.
    """
    st.title("Access Denied")
    st.error(
        f"Sorry, {user.name}, you don't have permission to access this dashboard."
    )
    st.markdown("---")
    st.markdown("Your account is not in the allowed users list.")
    st.markdown("Please contact an administrator to request access.")

    if st.button("Logout"):
        logout_user(user, get_client_ip())
        st.rerun()
