"""Whitelist-related models for user access control."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WhitelistEntry:
    """Represents a user entry in the access whitelist."""

    email: str
    name: str
    added_at: datetime
    added_by: str
    active: bool = True


@dataclass
class Whitelist:
    """Represents the complete access whitelist."""

    version: str
    last_updated: datetime
    updated_by: str
    users: list[WhitelistEntry] = field(default_factory=list)
    admins: list[WhitelistEntry] = field(default_factory=list)
