"""Status bar component for the Jenkins Dashboard."""

import streamlit as st

from src.models.state import DashboardState
from src.services.dashboard import calculate_statistics


def render_status_bar(state: DashboardState) -> None:
    """Render the status bar showing job statistics.

    Args:
        state: Current dashboard state
    """
    stats = calculate_statistics(state.jobs)

    # Create columns for metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Jobs",
            value=stats["total"],
        )

    with col2:
        st.metric(
            label="Success",
            value=stats["success"],
            delta=None,
        )

    with col3:
        st.metric(
            label="Failed",
            value=stats["failure"],
            delta=None,
        )

    with col4:
        st.metric(
            label="Building",
            value=stats["building"],
            delta=None,
        )

    with col5:
        # Show health indicator
        health = stats["health"]
        health_icons = {
            "healthy": "Healthy",
            "warning": "Warning",
            "critical": "Critical",
        }
        st.metric(
            label="Health",
            value=health_icons.get(health, "Unknown"),
        )

    # Show success rate as a progress bar
    success_rate = stats["success_rate"]
    st.progress(
        success_rate / 100,
        text=f"Success Rate: {success_rate}%",
    )


def render_connection_status(state: DashboardState) -> None:
    """Render connection status warning if Jenkins is unavailable.

    Args:
        state: Current dashboard state
    """
    if not state.is_jenkins_available:
        st.warning(
            f"Unable to connect to Jenkins. Showing cached data. "
            f"Error: {state.error_message}"
        )

    # Show last refresh time
    st.caption(f"Last updated: {state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
