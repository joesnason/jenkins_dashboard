"""Job card component for the Jenkins Dashboard."""

import streamlit as st

from src.models.job import JenkinsJob, JobStatus


def get_status_color(status: JobStatus) -> str:
    """Get the display color for a job status.

    Args:
        status: JobStatus enum value

    Returns:
        Color name for display
    """
    color_map = {
        JobStatus.SUCCESS: "green",
        JobStatus.FAILURE: "red",
        JobStatus.UNSTABLE: "orange",
        JobStatus.BUILDING: "blue",
        JobStatus.DISABLED: "gray",
        JobStatus.NOT_BUILT: "gray",
        JobStatus.ABORTED: "gray",
        JobStatus.UNKNOWN: "gray",
    }
    return color_map.get(status, "gray")


def get_status_emoji(status: JobStatus) -> str:
    """Get the display emoji for a job status.

    Args:
        status: JobStatus enum value

    Returns:
        Emoji string for display
    """
    emoji_map = {
        JobStatus.SUCCESS: ":white_check_mark:",
        JobStatus.FAILURE: ":x:",
        JobStatus.UNSTABLE: ":warning:",
        JobStatus.BUILDING: ":hourglass_flowing_sand:",
        JobStatus.DISABLED: ":no_entry:",
        JobStatus.NOT_BUILT: ":grey_question:",
        JobStatus.ABORTED: ":stop_sign:",
        JobStatus.UNKNOWN: ":question:",
    }
    return emoji_map.get(status, ":question:")


def render_job_card(job: JenkinsJob, show_details: bool = False) -> None:
    """Render a job card with status information.

    Args:
        job: JenkinsJob object to display
        show_details: Whether to show expanded details
    """
    status_emoji = get_status_emoji(job.status)
    status_text = job.status.value.upper()

    # Main job info
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"{status_emoji} **{job.name}**")

        with col2:
            st.markdown(f"`{status_text}`")

        with col3:
            if job.last_build_number:
                st.markdown(f"#{job.last_build_number}")
            else:
                st.markdown("No builds")

        if show_details:
            render_job_details(job)


def render_job_details(job: JenkinsJob) -> None:
    """Render detailed job information.

    Args:
        job: JenkinsJob object to display details for
    """
    st.markdown("---")

    if job.last_build_number is None:
        st.info("This job has never been built.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Last Build:** #{job.last_build_number}")
        if job.last_build_result:
            st.markdown(f"**Result:** {job.last_build_result}")

    with col2:
        if job.last_build_timestamp:
            st.markdown(
                f"**Time:** {job.last_build_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        if job.last_build_duration_ms:
            duration_s = job.last_build_duration_ms / 1000
            if duration_s < 60:
                duration_str = f"{duration_s:.1f}s"
            else:
                duration_str = f"{duration_s / 60:.1f}m"
            st.markdown(f"**Duration:** {duration_str}")

    # Link to Jenkins
    if job.url:
        st.markdown(f"[View in Jenkins]({job.url})")
