"""User whitelist management service."""

import json
from datetime import datetime
from pathlib import Path

from models.whitelist import Whitelist, WhitelistEntry

DEFAULT_WHITELIST_PATH = Path(__file__).parent.parent / "data" / "allowed_users.json"


class WhitelistService:
    """Service for managing the user access whitelist."""

    def __init__(self, path: Path | None = None) -> None:
        """Initialize whitelist service.

        Args:
            path: Path to whitelist JSON file. Uses default if not provided.
        """
        self._path = path or DEFAULT_WHITELIST_PATH

    def _load(self) -> Whitelist:
        """Load whitelist from JSON file.

        Returns:
            Whitelist object with all entries.
        """
        if not self._path.exists():
            return self._create_default()

        with open(self._path, encoding="utf-8") as f:
            data = json.load(f)

        return self._parse_whitelist(data)

    def _save(self, whitelist: Whitelist) -> None:
        """Save whitelist to JSON file.

        Args:
            whitelist: Whitelist object to save.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = self._serialize_whitelist(whitelist)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _create_default(self) -> Whitelist:
        """Create a default empty whitelist.

        Returns:
            Empty Whitelist object.
        """
        return Whitelist(
            version="1.0",
            last_updated=datetime.now(),
            updated_by="system",
            users=[],
            admins=[],
        )

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO format timestamp string.

        Args:
            timestamp_str: Timestamp string in ISO format.

        Returns:
            Parsed datetime object.
        """
        # Handle 'Z' suffix for UTC timezone
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        return datetime.fromisoformat(timestamp_str)

    def _parse_whitelist(self, data: dict) -> Whitelist:
        """Parse JSON data into Whitelist object.

        Args:
            data: Raw JSON data dictionary.

        Returns:
            Parsed Whitelist object.
        """
        users = [
            WhitelistEntry(
                email=u["email"],
                name=u["name"],
                added_at=self._parse_timestamp(u["added_at"]),
                added_by=u["added_by"],
                active=u.get("active", True),
            )
            for u in data.get("users", [])
        ]

        admins = [
            WhitelistEntry(
                email=a["email"],
                name=a["name"],
                added_at=self._parse_timestamp(a["added_at"]),
                added_by=a["added_by"],
                active=a.get("active", True),
            )
            for a in data.get("admins", [])
        ]

        return Whitelist(
            version=data.get("version", "1.0"),
            last_updated=self._parse_timestamp(data["last_updated"]),
            updated_by=data.get("updated_by", "unknown"),
            users=users,
            admins=admins,
        )

    def _serialize_whitelist(self, whitelist: Whitelist) -> dict:
        """Serialize Whitelist object to JSON-compatible dict.

        Args:
            whitelist: Whitelist object to serialize.

        Returns:
            Dictionary ready for JSON serialization.
        """
        return {
            "version": whitelist.version,
            "last_updated": whitelist.last_updated.isoformat(),
            "updated_by": whitelist.updated_by,
            "users": [
                {
                    "email": u.email,
                    "name": u.name,
                    "added_at": u.added_at.isoformat(),
                    "added_by": u.added_by,
                    "active": u.active,
                }
                for u in whitelist.users
            ],
            "admins": [
                {
                    "email": a.email,
                    "name": a.name,
                    "added_at": a.added_at.isoformat(),
                    "added_by": a.added_by,
                    "active": a.active,
                }
                for a in whitelist.admins
            ],
        }

    def is_user_allowed(self, email: str) -> bool:
        """Check if user email is in whitelist.

        Args:
            email: User email to check.

        Returns:
            True if user is whitelisted and active.
        """
        whitelist = self._load()
        all_entries = whitelist.users + whitelist.admins
        return any(
            entry.email.lower() == email.lower() and entry.active
            for entry in all_entries
        )

    def is_admin(self, email: str) -> bool:
        """Check if user email is an admin.

        Args:
            email: User email to check.

        Returns:
            True if user is an active admin.
        """
        whitelist = self._load()
        return any(
            admin.email.lower() == email.lower() and admin.active
            for admin in whitelist.admins
        )

    def add_user(self, email: str, name: str, added_by: str) -> bool:
        """Add a user to the whitelist.

        Args:
            email: User email to add.
            name: User display name.
            added_by: Email of admin adding the user.

        Returns:
            True if user was added, False if already exists.
        """
        whitelist = self._load()

        # Check if user already exists
        for user in whitelist.users:
            if user.email.lower() == email.lower():
                if not user.active:
                    # Reactivate existing user
                    user.active = True
                    user.added_at = datetime.now()
                    user.added_by = added_by
                    whitelist.last_updated = datetime.now()
                    whitelist.updated_by = added_by
                    self._save(whitelist)
                    return True
                return False

        # Add new user
        new_user = WhitelistEntry(
            email=email,
            name=name,
            added_at=datetime.now(),
            added_by=added_by,
            active=True,
        )
        whitelist.users.append(new_user)
        whitelist.last_updated = datetime.now()
        whitelist.updated_by = added_by
        self._save(whitelist)
        return True

    def remove_user(self, email: str, removed_by: str) -> bool:
        """Remove (deactivate) a user from whitelist.

        Args:
            email: User email to remove.
            removed_by: Email of admin removing the user.

        Returns:
            True if user was removed, False if not found.
        """
        whitelist = self._load()

        for user in whitelist.users:
            if user.email.lower() == email.lower() and user.active:
                user.active = False
                whitelist.last_updated = datetime.now()
                whitelist.updated_by = removed_by
                self._save(whitelist)
                return True

        return False

    def list_users(self, include_inactive: bool = False) -> list[WhitelistEntry]:
        """List all whitelisted users.

        Args:
            include_inactive: Include deactivated users if True.

        Returns:
            List of WhitelistEntry objects.
        """
        whitelist = self._load()
        if include_inactive:
            return whitelist.users
        return [u for u in whitelist.users if u.active]

    def list_admins(self, include_inactive: bool = False) -> list[WhitelistEntry]:
        """List all admin users.

        Args:
            include_inactive: Include deactivated admins if True.

        Returns:
            List of WhitelistEntry objects for admins.
        """
        whitelist = self._load()
        if include_inactive:
            return whitelist.admins
        return [a for a in whitelist.admins if a.active]
