"""User model for the Jenkins Dashboard."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Represents an authenticated user from SSO."""

    id: str
    email: str
    name: str
    roles: list[str]
    login_time: datetime
