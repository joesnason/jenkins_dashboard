# jenkins_dashboard Development Guidelines

Last updated: 2026-01-09

## Active Technologies

- Python 3.11+
- Streamlit 1.32+
- python-jenkins
- python-dotenv
- Authlib

## Project Structure

```text
src/
├── app.py                  # Main Streamlit application
├── models/                 # Data models
│   ├── user.py             # User model (with is_admin flag)
│   ├── whitelist.py        # Whitelist entry models
│   ├── audit.py            # Audit log models
│   ├── job.py              # Jenkins job models
│   └── state.py            # Dashboard state model
├── services/               # Business logic
│   ├── auth.py             # SSO authentication
│   ├── jenkins.py          # Jenkins API client
│   ├── whitelist.py        # Whitelist management (JSON-based)
│   ├── audit.py            # Audit logging
│   ├── dashboard.py        # Dashboard state management
│   ├── mock_auth.py        # Mock auth for demo mode
│   ├── mock_jenkins.py     # Mock Jenkins for demo mode
│   └── mock_ldap.py        # Mock LDAP for demo mode
├── components/             # UI components
│   ├── job_table.py        # Job table component
│   ├── job_card.py         # Job card component
│   ├── status_bar.py       # Status bar component
│   └── admin/              # Admin UI components
│       ├── user_management.py
│       └── audit_viewer.py
├── pages/                  # Streamlit multipage
│   └── Admin.py            # Admin backend page
└── data/                   # Data files
    └── allowed_users.json  # User whitelist
tests/
├── unit/
├── integration/
└── conftest.py
```

## Commands

```bash
# Run application (demo mode)
DEMO_MODE=true streamlit run src/app.py

# Run application (production)
streamlit run src/app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Lint code
ruff check src tests

# Format code
ruff format src tests
```

## Code Style

- Python 3.11+: Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Use dataclasses for data models
- Docstrings in Google style

## Authentication & Authorization

- **Authentication**: SSO (production) or Mock LDAP (demo mode)
- **Authorization**: Whitelist-based access control
  - Users must be in `allowed_users.json` to access dashboard
  - Admins are defined in the `admins` array and can access Admin backend
- **Admin Backend**: `/Admin` page for user management and audit logs

## Demo Mode

Set `DEMO_MODE=true` in environment or `.env` file:

| Email | Password | Type |
|-------|----------|------|
| user@demo.company.com | demo123 | User |
| admin@demo.company.com | admin123 | Admin |

## Key Files

| File | Purpose |
|------|---------|
| `src/services/whitelist.py` | User whitelist CRUD operations |
| `src/services/mock_ldap.py` | Mock LDAP service for demo |
| `src/data/allowed_users.json` | Whitelist data storage |
| `src/pages/Admin.py` | Admin backend page |

## Recent Changes

- Simplified login: Single login button (no PM/RD role distinction)
- Whitelist-based access control (replaces role-based)
- Admin backend for user management and audit log viewing
- Mock LDAP service for demo mode
- Extended audit logging for admin actions

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
