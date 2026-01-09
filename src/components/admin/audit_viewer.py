"""Audit log viewer component for admin dashboard."""

import json
from datetime import datetime, timedelta

import streamlit as st

from services.audit import AUDIT_LOG_PATH


def render_audit_viewer() -> None:
    """Render audit log viewer interface."""
    st.header("Audit Logs")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        days_filter = st.selectbox(
            "Time Range",
            options=[1, 7, 30, 90],
            format_func=lambda x: f"Last {x} day(s)",
        )
    with col2:
        action_filter = st.multiselect(
            "Action Types",
            options=[
                "login_success",
                "login_failure",
                "logout",
                "access_denied",
                "admin_action",
            ],
            default=None,
        )
    with col3:
        user_filter = st.text_input("Filter by Email", placeholder="user@company.com")

    st.markdown("---")

    # Load and display logs
    logs = _load_audit_logs(days=days_filter)

    # Apply filters
    if action_filter:
        logs = [log for log in logs if log.get("action") in action_filter]
    if user_filter:
        logs = [
            log
            for log in logs
            if user_filter.lower() in (log.get("user_email") or "").lower()
        ]

    if not logs:
        st.info("No audit logs found matching filters")
        return

    # Display logs in table format
    st.subheader(f"Showing {len(logs)} log entries")

    for log in logs:
        _render_log_entry(log)


def _load_audit_logs(days: int = 7) -> list[dict]:
    """Load audit logs from file.

    Args:
        days: Number of days to look back.

    Returns:
        List of log entry dictionaries.
    """
    if not AUDIT_LOG_PATH.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    logs = []

    with open(AUDIT_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff:
                    logs.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue

    # Sort by timestamp descending (most recent first)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return logs


def _render_log_entry(log: dict) -> None:
    """Render a single log entry.

    Args:
        log: Log entry dictionary.
    """
    action = log.get("action", "unknown")
    timestamp = log.get("timestamp", "")
    user_email = log.get("user_email", "N/A")
    details = log.get("details")

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        formatted_time = timestamp

    # Action color
    action_colors = {
        "login_success": ":green[LOGIN]",
        "login_failure": ":red[LOGIN FAILED]",
        "logout": ":blue[LOGOUT]",
        "access_denied": ":orange[ACCESS DENIED]",
        "admin_action": ":violet[ADMIN]",
    }
    action_display = action_colors.get(action, f":gray[{action.upper()}]")

    # Render entry
    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        st.write(f"**{formatted_time}**")
    with col2:
        st.write(action_display)
    with col3:
        st.write(user_email)

    # Show details if present
    if details:
        with st.expander("Details"):
            st.json(details)
