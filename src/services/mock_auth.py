"""Mock authentication service for demo purposes."""

from datetime import datetime

import streamlit as st

from models.audit import AuditAction, AuditResult
from models.user import User
from services.audit import log_event
from services.mock_ldap import MockLDAPService
from services.whitelist import WhitelistService

# Services
ldap_service = MockLDAPService()
whitelist_service = WhitelistService()


def mock_authenticate_user() -> User | None:
    """Authenticate user via demo login.

    Returns:
        User object if authenticated, None otherwise.
    """
    if "demo_user_email" in st.session_state and st.session_state.demo_user_email:
        email = st.session_state.demo_user_email
        ldap_user = ldap_service.lookup_user(email)
        is_admin = whitelist_service.is_admin(email)

        name = ldap_user.display_name if ldap_user else email.split("@")[0].title()

        return User(
            id=f"demo-{email.split('@')[0]}",
            email=email,
            name=name,
            roles=ldap_user.groups if ldap_user else ["User"],
            login_time=datetime.now(),
            is_admin=is_admin,
        )
    return None


def check_authorization(user: User) -> bool:
    """Check if user is in the whitelist.

    Args:
        user: The user to check.

    Returns:
        True if user is whitelisted, False otherwise.
    """
    return whitelist_service.is_user_allowed(user.email)


def mock_logout_user(user: User, ip_address: str = "") -> None:
    """Log out the demo user.

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

    # Clear session state
    if "demo_user_email" in st.session_state:
        del st.session_state.demo_user_email
    if "login_logged" in st.session_state:
        del st.session_state.login_logged


def get_client_ip() -> str:
    """Get mock client IP address.

    Returns:
        Mock client IP address string.
    """
    return "192.168.1.100"


def render_demo_login_page() -> None:
    """Render the demo login page with email/password form."""
    st.title("Jenkins Dashboard")
    st.markdown("---")

    # Demo mode banner
    st.info("**Demo Mode** - Enter credentials to login")

    st.markdown("### Login")

    # Login form
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="user@demo.company.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                # Authenticate via mock LDAP
                ldap_user = ldap_service.authenticate(email, password)
                if ldap_user:
                    st.session_state.demo_user_email = email
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.markdown("---")
    st.markdown("##### Demo Accounts")
    st.markdown("""
| Email | Password | Type |
|-------|----------|------|
| user@demo.company.com | demo123 | User |
| admin@demo.company.com | admin123 | Admin |
""")


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

    if st.button("Back to Login"):
        mock_logout_user(user, get_client_ip())
        st.rerun()
