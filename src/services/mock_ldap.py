"""Mock LDAP service for development and testing."""

from dataclasses import dataclass


@dataclass
class LDAPUser:
    """Represents a user from LDAP directory."""

    dn: str
    uid: str
    email: str
    display_name: str
    department: str
    groups: list[str]


# Mock LDAP directory with demo users
MOCK_LDAP_USERS: dict[str, LDAPUser] = {
    "user@demo.company.com": LDAPUser(
        dn="cn=user,ou=users,dc=demo,dc=company,dc=com",
        uid="user",
        email="user@demo.company.com",
        display_name="Demo User",
        department="Engineering",
        groups=["employees", "engineering"],
    ),
    "admin@demo.company.com": LDAPUser(
        dn="cn=admin,ou=admins,dc=demo,dc=company,dc=com",
        uid="admin",
        email="admin@demo.company.com",
        display_name="Demo Admin",
        department="IT",
        groups=["employees", "it", "admins"],
    ),
    "alice@company.com": LDAPUser(
        dn="cn=alice,ou=users,dc=company,dc=com",
        uid="alice",
        email="alice@company.com",
        display_name="Alice Chen",
        department="Engineering",
        groups=["employees", "engineering"],
    ),
    "bob@company.com": LDAPUser(
        dn="cn=bob,ou=users,dc=company,dc=com",
        uid="bob",
        email="bob@company.com",
        display_name="Bob Wang",
        department="Product",
        groups=["employees", "product"],
    ),
}

# Mock credentials (email -> password)
MOCK_CREDENTIALS: dict[str, str] = {
    "user@demo.company.com": "demo123",
    "admin@demo.company.com": "admin123",
    "alice@company.com": "alice123",
    "bob@company.com": "bob123",
}


class MockLDAPService:
    """Mock LDAP service that simulates directory lookups."""

    def __init__(self) -> None:
        """Initialize mock LDAP service."""
        self._users = MOCK_LDAP_USERS
        self._credentials = MOCK_CREDENTIALS

    def authenticate(self, email: str, password: str) -> LDAPUser | None:
        """Simulate LDAP authentication.

        Args:
            email: User email address.
            password: User password.

        Returns:
            LDAPUser if authenticated, None otherwise.
        """
        email_lower = email.lower()
        if email_lower in self._credentials and self._credentials[email_lower] == password:
            return self._users.get(email_lower)
        return None

    def lookup_user(self, email: str) -> LDAPUser | None:
        """Look up user by email in LDAP directory.

        Args:
            email: User email address.

        Returns:
            LDAPUser if found, None otherwise.
        """
        return self._users.get(email.lower())

    def search_users(self, query: str) -> list[LDAPUser]:
        """Search for users matching query.

        Args:
            query: Search string to match against email or name.

        Returns:
            List of matching LDAPUser objects.
        """
        results = []
        query_lower = query.lower()
        for user in self._users.values():
            if (
                query_lower in user.email.lower()
                or query_lower in user.display_name.lower()
            ):
                results.append(user)
        return results

    def get_user_groups(self, email: str) -> list[str]:
        """Get groups for a user.

        Args:
            email: User email address.

        Returns:
            List of group names, empty list if user not found.
        """
        user = self._users.get(email.lower())
        return user.groups if user else []
