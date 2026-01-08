"""Job table component for the Jenkins Dashboard."""

import streamlit as st

from src.components.job_card import get_status_emoji, render_job_details
from src.models.job import JenkinsJob, JobStatus


def render_job_table(jobs: list[JenkinsJob]) -> None:
    """Render a table of all Jenkins jobs.

    Args:
        jobs: List of JenkinsJob objects to display
    """
    if not jobs:
        st.info("No jobs found.")
        return

    # Sort options
    sort_option = st.selectbox(
        "Sort by",
        options=["Name", "Status", "Last Build"],
        index=0,
    )

    # Sort jobs
    sorted_jobs = _sort_jobs(jobs, sort_option)

    # Filter options
    filter_status = st.multiselect(
        "Filter by status",
        options=[s.value for s in JobStatus],
        default=[],
    )

    # Apply filter
    if filter_status:
        filtered_jobs = [j for j in sorted_jobs if j.status.value in filter_status]
    else:
        filtered_jobs = sorted_jobs

    st.markdown(f"Showing {len(filtered_jobs)} of {len(jobs)} jobs")
    st.markdown("---")

    # Render each job as an expandable item
    for job in filtered_jobs:
        status_emoji = get_status_emoji(job.status)
        build_info = f"#{job.last_build_number}" if job.last_build_number else "No builds"

        with st.expander(f"{status_emoji} {job.name} - {job.status.value.upper()} ({build_info})"):
            render_job_details(job)


def _sort_jobs(jobs: list[JenkinsJob], sort_by: str) -> list[JenkinsJob]:
    """Sort jobs by the specified criteria.

    Args:
        jobs: List of jobs to sort
        sort_by: Sort criteria ('Name', 'Status', 'Last Build')

    Returns:
        Sorted list of jobs
    """
    if sort_by == "Name":
        return sorted(jobs, key=lambda j: j.name.lower())
    elif sort_by == "Status":
        # Sort by status priority: FAILURE first, then BUILDING, then others
        status_priority = {
            JobStatus.FAILURE: 0,
            JobStatus.BUILDING: 1,
            JobStatus.UNSTABLE: 2,
            JobStatus.SUCCESS: 3,
            JobStatus.ABORTED: 4,
            JobStatus.NOT_BUILT: 5,
            JobStatus.DISABLED: 6,
            JobStatus.UNKNOWN: 7,
        }
        return sorted(jobs, key=lambda j: status_priority.get(j.status, 99))
    elif sort_by == "Last Build":
        # Sort by last build number, newest first
        return sorted(
            jobs,
            key=lambda j: j.last_build_number if j.last_build_number else 0,
            reverse=True,
        )
    return jobs


def render_job_grid(jobs: list[JenkinsJob], columns: int = 3) -> None:
    """Render jobs in a grid layout.

    Args:
        jobs: List of JenkinsJob objects to display
        columns: Number of columns in the grid
    """
    if not jobs:
        st.info("No jobs found.")
        return

    # Create grid
    cols = st.columns(columns)

    for idx, job in enumerate(jobs):
        col_idx = idx % columns
        with cols[col_idx]:
            _render_grid_card(job)


def _render_grid_card(job: JenkinsJob) -> None:
    """Render a compact job card for grid display.

    Args:
        job: JenkinsJob object to display
    """
    status_emoji = get_status_emoji(job.status)

    with st.container():
        st.markdown(f"### {status_emoji} {job.name}")
        st.markdown(f"**Status:** {job.status.value.upper()}")

        if job.last_build_number:
            st.markdown(f"**Build:** #{job.last_build_number}")
            if job.last_build_timestamp:
                st.caption(job.last_build_timestamp.strftime("%m/%d %H:%M"))
        else:
            st.markdown("*No builds yet*")

        if job.url:
            st.markdown(f"[View]({job.url})")

        st.markdown("---")
