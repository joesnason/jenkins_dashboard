# Jenkins Build Status Dashboard

A Streamlit-based dashboard for monitoring Jenkins build jobs status, designed for PM and RD Managers.

## Features

- Real-time view of all Jenkins job statuses
- Auto-refresh every 30 seconds
- SSO authentication with role-based access control
- Job filtering and sorting
- Expandable job details with build history
- Graceful degradation when Jenkins is unavailable

## Requirements

- Python 3.11+
- Jenkins server with API access
- Company SSO (OIDC-compatible)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd jenkins_dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:

```bash
cp .env.example .env
# Edit .env with your Jenkins credentials
```

Create `.streamlit/secrets.toml`:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your SSO configuration
```

### 3. Run Locally

```bash
streamlit run src/app.py
```

Open http://localhost:8501 in your browser.

## Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

## Docker

### Build and Run

```bash
# Build image
docker build -t jenkins-dashboard .

# Run container
docker run -p 8501:8501 \
  -e JENKINS_URL=https://jenkins.company.com \
  -e JENKINS_USER=service-account \
  -e JENKINS_API_TOKEN=your-token \
  jenkins-dashboard
```

### Docker Compose

```bash
docker-compose up -d
```

## Project Structure

```
jenkins_dashboard/
├── src/
│   ├── app.py              # Streamlit application entry point
│   ├── models/             # Data models
│   ├── services/           # Business logic services
│   └── components/         # UI components
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Shared fixtures
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
└── pyproject.toml          # Project configuration
```

## Architecture

- **Streamlit** - Web framework with built-in SSO support
- **python-jenkins** - Jenkins API client
- **python-dotenv** - Environment variable management

## Security

- SSO authentication required for all users
- Role-based access control (PM, RD_Manager, Admin roles)
- Audit logging for all authentication events
- API tokens stored securely in secrets

## License

MIT
