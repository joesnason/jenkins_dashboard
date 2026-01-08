# Quickstart: Jenkins Build Status Dashboard

**Feature**: 001-jenkins-dashboard
**Date**: 2026-01-08

## Prerequisites

- Python 3.11+
- Jenkins server with API access
- Company SSO (OIDC-compatible)

---

## 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd jenkins_dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Jenkins Configuration
JENKINS_URL=https://jenkins.company.com
JENKINS_USER=service-account
JENKINS_API_TOKEN=your-api-token

# App Configuration
REFRESH_INTERVAL=30  # seconds
```

### Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-strong-random-secret-min-32-chars"

[auth.company_sso]
client_id = "your-sso-client-id"
client_secret = "your-sso-client-secret"
server_metadata_url = "https://sso.company.com/.well-known/openid-configuration"

[jenkins]
url = "https://jenkins.company.com"
user = "service-account"
api_token = "your-jenkins-api-token"

[app]
allowed_roles = ["PM", "RD_Manager", "Admin"]
refresh_interval = 30
```

---

## 3. Run Locally

```bash
# Start the application
streamlit run src/app.py

# Open browser to http://localhost:8501
```

---

## 4. Test Authentication

1. Open http://localhost:8501
2. Click "使用公司帳號登入" button
3. Complete SSO authentication
4. Verify you see the dashboard

**Troubleshooting:**
- If redirected to error page, check SSO configuration
- Verify `redirect_uri` matches Streamlit app URL
- Check SSO application has correct callback URL configured

---

## 5. Test Jenkins Connection

```bash
# Verify Jenkins credentials
python -c "
import jenkins
import os

server = jenkins.Jenkins(
    os.environ['JENKINS_URL'],
    username=os.environ['JENKINS_USER'],
    password=os.environ['JENKINS_API_TOKEN']
)
print(f'Jenkins version: {server.get_version()}')
print(f'Jobs count: {len(server.get_all_jobs())}')
"
```

---

## 6. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_jenkins_service.py
```

---

## 7. Development Commands

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Run all checks
make check  # or: ruff format && ruff check && mypy src && pytest
```

---

## Project Structure

```
jenkins_dashboard/
├── src/
│   ├── app.py              # Streamlit application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py         # User dataclass
│   │   ├── job.py          # JenkinsJob dataclass
│   │   └── state.py        # DashboardState dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication service
│   │   ├── jenkins.py      # Jenkins API service
│   │   ├── dashboard.py    # Dashboard state service
│   │   └── audit.py        # Audit logging service
│   └── components/
│       ├── __init__.py
│       ├── job_card.py     # Job status card component
│       ├── status_bar.py   # Status summary bar
│       └── job_table.py    # Job list table
├── tests/
│   ├── unit/
│   │   ├── test_auth.py
│   │   ├── test_jenkins.py
│   │   └── test_dashboard.py
│   ├── integration/
│   │   └── test_jenkins_integration.py
│   └── conftest.py         # Pytest fixtures
├── .streamlit/
│   └── secrets.toml        # Streamlit secrets (not in git)
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Common Issues

### SSO Login Not Working

1. Check `redirect_uri` in secrets.toml matches your app URL
2. Verify SSO application is configured with correct callback URL
3. Check `server_metadata_url` is accessible

### Jenkins Connection Failed

1. Verify Jenkins URL is accessible from your network
2. Check API token is valid (not expired)
3. Verify service account has read permissions

### Jobs Not Showing

1. Check Jenkins API token permissions
2. Verify service account can view jobs
3. Check network connectivity to Jenkins

---

## Next Steps

1. Review `specs/001-jenkins-dashboard/spec.md` for full requirements
2. Review `specs/001-jenkins-dashboard/data-model.md` for data structures
3. Review `specs/001-jenkins-dashboard/contracts/` for API contracts
4. Run `/speckit.tasks` to generate implementation tasks
