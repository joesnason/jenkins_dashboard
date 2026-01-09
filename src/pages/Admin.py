"""Admin backend for Jenkins Dashboard."""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

from components.admin.audit_viewer import render_audit_viewer
from components.admin.user_management import render_user_management
from services.audit import AuditService
from services.whitelist import WhitelistService

# Load environment variables
load_dotenv()

# Check demo mode
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    from services.mock_auth import (
        get_client_ip,
        mock_authenticate_user as authenticate_user,
        mock_logout_user as logout_user,
        render_demo_login_page as render_login_page,
    )
else:
    from services.auth import (
        authenticate_user,
        get_client_ip,
        logout_user,
        render_login_page,
    )

# Page configuration
st.set_page_config(
    page_title="Admin - Jenkins Dashboard",
    page_icon=":gear:",
    layout="wide",
)

# Services
whitelist_service = WhitelistService()
audit_service = AuditService()


def render_admin_required_page(user) -> None:
    """Render page for non-admin users.

    Args:
        user: The non-admin user.
    """
    st.title("Admin Access Required")
    st.error(f"Sorry, {user.name}, you don't have admin privileges.")
    st.markdown("---")
    st.markdown("This page is only accessible to system administrators.")
    st.markdown("Please contact a system administrator if you need access.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Dashboard", type="primary"):
            st.switch_page("app.py")
    with col2:
        if st.button("Logout"):
            logout_user(user, get_client_ip())
            st.rerun()


def render_admin_dashboard(user) -> None:
    """Render the admin dashboard.

    Args:
        user: The admin user.
    """
    if DEMO_MODE:
        st.info("**Demo Mode** - Changes will persist in the demo environment")

    st.title("Admin Dashboard")
    st.caption(f"Logged in as: {user.name} ({user.email})")

    st.markdown("---")

    # Navigation tabs
    tab1, tab2 = st.tabs(["User Management", "Audit Logs"])

    with tab1:
        render_user_management(user, whitelist_service, audit_service)

    with tab2:
        render_audit_viewer()

    st.markdown("---")

    # Footer actions
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Back to Dashboard"):
            st.switch_page("app.py")


def main() -> None:
    """Admin page entry point."""
    user = authenticate_user()

    if user is None:
        render_login_page()
        st.stop()

    # Check admin privilege
    if not user.is_admin:
        render_admin_required_page(user)
        st.stop()

    render_admin_dashboard(user)


if __name__ == "__main__":
    main()
