# Tasks: Jenkins Build Status Dashboard

**Input**: Design documents from `/specs/001-jenkins-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included as per Constitution principle II (Testing Standards - 80%+ coverage for critical paths).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md (src/models/, src/services/, src/components/, tests/)
- [X] T002 Initialize Python project with pyproject.toml (Python 3.11+, project metadata, dependencies)
- [X] T003 [P] Create requirements.txt with runtime dependencies (streamlit>=1.32.0, python-jenkins>=1.8.0, python-dotenv>=1.0.0)
- [X] T004 [P] Create requirements-dev.txt with dev dependencies (pytest, pytest-cov, pytest-mock, ruff, mypy)
- [X] T005 [P] Configure ruff.toml for linting and formatting
- [X] T006 [P] Configure mypy.ini for type checking
- [X] T007 [P] Create .env.example with environment variable template (JENKINS_URL, JENKINS_USER, JENKINS_API_TOKEN)
- [X] T008 [P] Create .gitignore (Python, venv, .env, .streamlit/secrets.toml, __pycache__)

**Checkpoint**: Project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create base exception classes in src/models/exceptions.py (JenkinsConnectionError, JenkinsAuthError, JenkinsJobNotFoundError, AuthorizationError)
- [X] T010 [P] Create JobStatus enum in src/models/job.py with all status values (SUCCESS, FAILURE, UNSTABLE, BUILDING, DISABLED, NOT_BUILT, ABORTED, UNKNOWN)
- [X] T011 [P] Create AuditAction and AuditResult enums in src/models/audit.py
- [X] T012 [P] Create src/models/__init__.py to export all models
- [X] T013 Create src/services/__init__.py to export all services
- [X] T014 [P] Create src/components/__init__.py to export all components
- [X] T015 Create tests/conftest.py with shared pytest fixtures (mock Jenkins server, mock user, mock jobs)
- [X] T016 [P] Create .streamlit/config.toml with basic Streamlit configuration

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View All Job Status Overview (Priority: P1) 🎯 MVP

**Goal**: Display all Jenkins build jobs with their current status on a single dashboard page

**Independent Test**: Login and verify all Jenkins jobs are displayed with status (success/failure/building) and last build version

### Tests for User Story 1

- [X] T017 [P] [US1] Unit test for JenkinsJob model in tests/unit/test_models.py
- [X] T018 [P] [US1] Unit test for DashboardState model in tests/unit/test_models.py
- [X] T019 [P] [US1] Unit test for color_to_status mapping in tests/unit/test_jenkins_service.py
- [X] T020 [P] [US1] Unit test for get_all_jobs service in tests/unit/test_jenkins_service.py
- [X] T021 [P] [US1] Unit test for calculate_statistics in tests/unit/test_dashboard_service.py
- [X] T022 [US1] Integration test for Jenkins API connection in tests/integration/test_jenkins_integration.py

### Implementation for User Story 1

- [X] T023 [P] [US1] Create JenkinsJob dataclass in src/models/job.py with all fields from data-model.md
- [X] T024 [P] [US1] Create DashboardState dataclass in src/models/state.py with all fields from data-model.md
- [X] T025 [US1] Implement color_to_status() mapping function in src/services/jenkins.py
- [X] T026 [US1] Implement JenkinsService class with get_all_jobs() in src/services/jenkins.py (uses python-jenkins, @st.cache_data TTL=30s)
- [X] T027 [US1] Implement get_job_details() method in src/services/jenkins.py
- [X] T028 [US1] Implement DashboardService class with get_dashboard_state() in src/services/dashboard.py
- [X] T029 [US1] Implement calculate_statistics() in src/services/dashboard.py
- [X] T030 [US1] Implement refresh_jobs() with cache clearing in src/services/dashboard.py
- [X] T031 [P] [US1] Create StatusBar component in src/components/status_bar.py (shows total/success/failure/building counts)
- [X] T032 [P] [US1] Create JobCard component in src/components/job_card.py (shows job name, status color, last build number)
- [X] T033 [US1] Create JobTable component in src/components/job_table.py (displays all jobs in grid/table layout)
- [X] T034 [US1] Add error handling for Jenkins connection failures in src/services/jenkins.py (graceful degradation with cached data)
- [X] T035 [US1] Create main app entry point src/app.py with basic Streamlit layout (title, status bar, job table, refresh button)
- [X] T036 [US1] Implement auto-refresh using st.rerun() with 30-second interval in src/app.py
- [X] T037 [US1] Add last refresh timestamp display in src/app.py

**Checkpoint**: Dashboard displays all Jenkins jobs with status - MVP functional (without auth)

---

## Phase 4: User Story 2 - User Authentication and Access Control (Priority: P2)

**Goal**: Ensure only authorized users (PM and RD Managers) can access the dashboard via company SSO

**Independent Test**: Attempt access with valid/invalid credentials and verify access is granted/denied appropriately

### Tests for User Story 2

- [X] T038 [P] [US2] Unit test for User model in tests/unit/test_models.py
- [X] T039 [P] [US2] Unit test for AuditLogEntry model in tests/unit/test_models.py
- [X] T040 [P] [US2] Unit test for check_authorization() in tests/unit/test_auth.py
- [X] T041 [P] [US2] Unit test for log_event() in tests/unit/test_audit.py
- [X] T042 [US2] Integration test for SSO authentication flow in tests/integration/test_auth_integration.py

### Implementation for User Story 2

- [X] T043 [P] [US2] Create User dataclass in src/models/user.py with fields from data-model.md
- [X] T044 [P] [US2] Create AuditLogEntry dataclass in src/models/audit.py with fields from data-model.md
- [X] T045 [US2] Implement AuditService with log_event() in src/services/audit.py (writes to JSON lines file)
- [X] T046 [US2] Implement authenticate_user() in src/services/auth.py (uses st.user for SSO)
- [X] T047 [US2] Implement check_authorization() in src/services/auth.py (validates PM/RD_Manager roles)
- [X] T048 [US2] Implement logout_user() in src/services/auth.py (calls st.logout(), logs event)
- [X] T049 [US2] Create .streamlit/secrets.toml.example with SSO configuration template
- [X] T050 [US2] Update src/app.py to require authentication before showing dashboard
- [X] T051 [US2] Add login button and redirect for unauthenticated users in src/app.py
- [X] T052 [US2] Add logout button in dashboard header in src/app.py
- [X] T053 [US2] Add welcome message showing user name in src/app.py
- [X] T054 [US2] Implement access denied page for unauthorized roles in src/app.py
- [X] T055 [US2] Log LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, ACCESS_DENIED events in src/services/auth.py

**Checkpoint**: Dashboard requires SSO login, only PM/RD Manager roles can access

---

## Phase 5: User Story 3 - View Detailed Job Information (Priority: P3)

**Goal**: Display detailed information about a specific job including last build version number and timestamp

**Independent Test**: Click on a job and verify version number and build details are displayed

### Tests for User Story 3

- [X] T056 [P] [US3] Unit test for job detail display logic in tests/unit/test_components.py
- [X] T057 [US3] Integration test for job details fetch in tests/integration/test_jenkins_integration.py

### Implementation for User Story 3

- [X] T058 [US3] Enhance JobCard component to show expandable details in src/components/job_card.py
- [X] T059 [US3] Add job detail section showing: last build number, timestamp, duration, result in src/components/job_card.py
- [X] T060 [US3] Handle "No builds yet" state for jobs that have never been built in src/components/job_card.py
- [X] T061 [US3] Add job URL link to Jenkins in job detail view in src/components/job_card.py
- [X] T062 [US3] Update JobTable to support row expansion/selection in src/components/job_table.py

**Checkpoint**: All user stories complete - full feature delivered

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T063 [P] Add type hints to all Python files and verify with mypy
- [X] T064 [P] Run ruff format on all Python files
- [X] T065 [P] Run ruff check and fix all linting issues
- [ ] T066 Run pytest with coverage report, ensure 80%+ coverage for critical paths
- [X] T067 [P] Create README.md with project overview and setup instructions
- [X] T068 [P] Create Dockerfile for containerized deployment
- [X] T069 [P] Create docker-compose.yml for local development
- [ ] T070 Validate quickstart.md instructions work end-to-end
- [ ] T071 Performance test: verify page load <3 seconds with 100 jobs
- [ ] T072 Security review: ensure no secrets in code, proper error messages

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2
  - US2 (P2): Can start after Phase 2 (independent of US1)
  - US3 (P3): Depends on US1 components (JobCard, JobTable)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - delivers core dashboard MVP
- **User Story 2 (P2)**: No dependencies on other stories - adds authentication layer
- **User Story 3 (P3)**: Depends on US1 components - extends JobCard and JobTable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before components
- Components before app integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003-T008: All setup config files can be created in parallel
- T010-T016: All foundational tasks marked [P] can run in parallel
- T017-T022: All US1 tests can be written in parallel
- T023-T024, T031-T032: Models and components within US1 can run in parallel
- T038-T041: All US2 tests can be written in parallel
- T043-T044: US2 models can be created in parallel
- US1 and US2: Can be developed in parallel by different developers after Phase 2

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T017 "Unit test for JenkinsJob model in tests/unit/test_models.py"
Task: T018 "Unit test for DashboardState model in tests/unit/test_models.py"
Task: T019 "Unit test for color_to_status mapping in tests/unit/test_jenkins_service.py"
Task: T020 "Unit test for get_all_jobs service in tests/unit/test_jenkins_service.py"
Task: T021 "Unit test for calculate_statistics in tests/unit/test_dashboard_service.py"

# Launch models in parallel:
Task: T023 "Create JenkinsJob dataclass in src/models/job.py"
Task: T024 "Create DashboardState dataclass in src/models/state.py"

# Launch components in parallel:
Task: T031 "Create StatusBar component in src/components/status_bar.py"
Task: T032 "Create JobCard component in src/components/job_card.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test dashboard displays jobs without auth
5. Deploy/demo for initial feedback

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy with auth
4. Add User Story 3 → Test independently → Full feature complete
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (dashboard)
   - Developer B: User Story 2 (authentication)
3. Developer A continues to User Story 3 after US1 complete
4. Stories integrate at app.py level

---

## Summary

| Phase | Task Count | Parallel Tasks |
|-------|------------|----------------|
| Phase 1: Setup | 8 | 6 |
| Phase 2: Foundational | 8 | 6 |
| Phase 3: US1 (P1 MVP) | 21 | 9 |
| Phase 4: US2 (P2) | 18 | 6 |
| Phase 5: US3 (P3) | 7 | 1 |
| Phase 6: Polish | 10 | 6 |
| **Total** | **72** | **34** |

**MVP Scope**: Phases 1-3 (37 tasks) delivers functional dashboard without authentication

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance: 80%+ test coverage, ruff linting, mypy type checking
