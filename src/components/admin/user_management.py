"""User management component for admin dashboard."""

import streamlit as st

from models.user import User
from services.audit import AuditService
from services.whitelist import WhitelistService


def render_user_management(
    admin_user: User,
    whitelist_service: WhitelistService,
    audit_service: AuditService,
) -> None:
    """Render user management interface.

    Args:
        admin_user: The current admin user.
        whitelist_service: Whitelist service instance.
        audit_service: Audit service instance.
    """
    st.header("User Management")

    # Add new user section
    st.subheader("Add New User")

    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_email = st.text_input("Email", placeholder="user@company.com")
        with col2:
            new_name = st.text_input("Name", placeholder="User Name")

        submitted = st.form_submit_button("Add User", type="primary")

        if submitted:
            if new_email and new_name:
                success = whitelist_service.add_user(
                    email=new_email,
                    name=new_name,
                    added_by=admin_user.email,
                )
                if success:
                    audit_service.log_admin_action(
                        admin=admin_user,
                        action="add_user",
                        details={"email": new_email, "name": new_name},
                    )
                    st.success(f"Added {new_email} to whitelist")
                    st.rerun()
                else:
                    st.error("Failed to add user (may already exist)")
            else:
                st.warning("Please fill in both email and name")

    st.markdown("---")

    # Current users list
    st.subheader("Whitelisted Users")
    users = whitelist_service.list_users()

    if not users:
        st.info("No users in whitelist yet")
    else:
        for user in users:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{user.email}**")
            with col2:
                st.write(user.name)
            with col3:
                st.caption(f"Added: {user.added_at.strftime('%Y-%m-%d')}")
            with col4:
                if st.button("Remove", key=f"remove_{user.email}"):
                    whitelist_service.remove_user(user.email, admin_user.email)
                    audit_service.log_admin_action(
                        admin=admin_user,
                        action="remove_user",
                        details={"email": user.email},
                    )
                    st.rerun()

    st.markdown("---")

    # Admin users list (read-only display)
    st.subheader("Admin Users")
    admins = whitelist_service.list_admins()

    if not admins:
        st.info("No admin users configured")
    else:
        for admin in admins:
            st.write(f"- **{admin.name}** ({admin.email})")

    st.caption("Admin users are managed via configuration file")
