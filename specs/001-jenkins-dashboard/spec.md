# Feature Specification: Jenkins Build Status Dashboard

**Feature Branch**: `001-jenkins-dashboard`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "建立一個網頁讓使用者查看 Jenkins 最新 build job status 及最後一個 build job 的版本，需要權限管理，目標使用者為 PM 及 RD 主管"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View All Job Status Overview (Priority: P1)

As a PM or RD Manager, I want to see an overview of all Jenkins build jobs on a single dashboard page, so I can quickly understand the current state of all projects without logging into Jenkins directly.

**Why this priority**: This is the core value proposition - providing a consolidated view of all job statuses is the primary reason users will access this dashboard.

**Independent Test**: Can be fully tested by logging in and verifying that all Jenkins jobs are displayed with their current status (success/failure/in-progress) and delivers immediate visibility into build health.

**Acceptance Scenarios**:

1. **Given** a logged-in user with valid permissions, **When** they access the dashboard, **Then** they see a list of all Jenkins build jobs with their current status (success, failure, building, or disabled)
2. **Given** a logged-in user viewing the dashboard, **When** a job status changes in Jenkins, **Then** the dashboard reflects the updated status within the configured refresh interval
3. **Given** multiple jobs exist, **When** the user views the dashboard, **Then** jobs are organized in a clear, scannable layout showing job name, status, and last build version

---

### User Story 2 - User Authentication and Access Control (Priority: P2)

As a system administrator, I want to ensure only authorized users (PM and RD Managers) can access the dashboard, so that build information is protected from unauthorized access.

**Why this priority**: Security and access control is essential for production use but the dashboard functionality must work first to have something worth protecting.

**Independent Test**: Can be fully tested by attempting to access the dashboard with valid/invalid credentials and verifying access is granted/denied appropriately.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user, **When** they attempt to access the dashboard URL, **Then** they are redirected to a login page
2. **Given** a user with valid credentials, **When** they submit correct login information, **Then** they are granted access to the dashboard
3. **Given** a user with invalid credentials, **When** they submit incorrect login information, **Then** they see an error message and remain on the login page
4. **Given** a logged-in user, **When** they choose to log out, **Then** their session is terminated and they are redirected to the login page

---

### User Story 3 - View Detailed Job Information (Priority: P3)

As a PM or RD Manager, I want to see detailed information about a specific job including its last build version number, so I can track which version is currently deployed or ready for release.

**Why this priority**: Detailed version information adds value beyond status but is secondary to the core dashboard overview functionality.

**Independent Test**: Can be fully tested by clicking on a job and verifying the version number and additional details are displayed correctly.

**Acceptance Scenarios**:

1. **Given** a logged-in user viewing the dashboard, **When** they select a specific job, **Then** they see the last build version/number for that job
2. **Given** a job with build history, **When** the user views job details, **Then** they see the timestamp of the last build
3. **Given** a job that has never been built, **When** the user views that job, **Then** they see an appropriate "No builds yet" message

---

### Edge Cases

- What happens when Jenkins server is unreachable? System displays a clear error message indicating connectivity issues and shows cached data if available with a timestamp of when data was last refreshed
- What happens when a user's session expires? User is prompted to re-authenticate and redirected to login page
- What happens when Jenkins returns an error for a specific job? That job displays an error indicator while other jobs continue to show correctly
- What happens when there are no jobs configured in Jenkins? Dashboard displays an empty state message explaining no jobs are available
- How does the system handle users who are removed from the authorized list while logged in? Their next request results in access denied and session termination

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a list of all Jenkins build jobs with their current status (success, failure, building, disabled, or unknown)
- **FR-002**: System MUST show the last build version/number for each job
- **FR-003**: System MUST require user authentication before displaying any dashboard content
- **FR-004**: System MUST support role-based access where only authorized users (PM, RD Manager roles) can view the dashboard
- **FR-005**: System MUST refresh job status data automatically at a configurable interval (default: 30 seconds)
- **FR-006**: System MUST display the timestamp of the last successful data refresh
- **FR-007**: System MUST provide visual distinction between different job statuses (e.g., color coding: green for success, red for failure, yellow for building)
- **FR-008**: System MUST allow users to manually trigger a data refresh
- **FR-009**: System MUST display user-friendly error messages when Jenkins connectivity fails
- **FR-010**: System MUST log authentication attempts for security auditing
- **FR-011**: System MUST provide a logout functionality that terminates the user session
- **FR-012**: System MUST authenticate users via company SSO (Single Sign-On), allowing PM and RD Managers to log in using their existing corporate credentials

### Key Entities

- **User**: Represents an authorized person who can access the dashboard; has username, role (PM or RD Manager), and authentication credentials
- **Jenkins Job**: Represents a build job from Jenkins; has name, current status, last build number/version, last build timestamp, and job URL
- **Session**: Represents an authenticated user's active session; has user reference, creation time, and expiration time
- **Audit Log Entry**: Represents a security-relevant event; has timestamp, user, action type, and result

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the status of all Jenkins jobs within 3 seconds of page load
- **SC-002**: Dashboard data refreshes automatically without requiring page reload
- **SC-003**: 100% of unauthorized access attempts are blocked and logged
- **SC-004**: Users can identify job status at a glance through visual indicators without reading text
- **SC-005**: System correctly reflects Jenkins job status changes within 60 seconds of occurrence
- **SC-006**: Users can complete login and reach the dashboard in under 30 seconds
- **SC-007**: Dashboard remains usable and displays cached data even when Jenkins is temporarily unavailable

## Assumptions

- Jenkins server exposes a standard API that provides job status and build information
- The number of Jenkins jobs to display is manageable on a single page view (typically under 100 jobs)
- Users have network access to reach both the dashboard application and the Jenkins server
- PM and RD Manager roles are predefined and users are assigned to these roles through an administrative process
- Automatic refresh interval of 30 seconds is acceptable for most use cases
