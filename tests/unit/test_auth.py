"""Unit tests for authentication service."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.models.user import User
from src.services.auth import check_authorization


class TestCheckAuthorization:
    """Tests for check_authorization function."""

    def test_pm_user_is_authorized(self, mock_user: User) -> None:
        """Test that PM role is authorized."""
        assert check_authorization(mock_user) is True

    def test_rd_manager_is_authorized(self, mock_rd_manager: User) -> None:
        """Test that RD_Manager role is authorized."""
        assert check_authorization(mock_rd_manager) is True

    def test_developer_is_not_authorized(self, mock_unauthorized_user: User) -> None:
        """Test that Developer role is not authorized."""
        assert check_authorization(mock_unauthorized_user) is False

    def test_admin_is_authorized(self) -> None:
        """Test that Admin role is authorized."""
        user = User(
            id="admin123",
            email="admin@company.com",
            name="Admin User",
            roles=["Admin"],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )
        assert check_authorization(user) is True

    def test_user_with_multiple_roles_including_authorized(self) -> None:
        """Test user with multiple roles including an authorized one."""
        user = User(
            id="user123",
            email="user@company.com",
            name="Multi-Role User",
            roles=["Developer", "PM"],  # Has PM role
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )
        assert check_authorization(user) is True

    def test_user_with_no_roles_is_not_authorized(self) -> None:
        """Test user with no roles is not authorized."""
        user = User(
            id="user123",
            email="user@company.com",
            name="No Role User",
            roles=[],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )
        assert check_authorization(user) is False

    def test_user_with_only_unauthorized_roles(self) -> None:
        """Test user with only unauthorized roles."""
        user = User(
            id="user123",
            email="user@company.com",
            name="Regular User",
            roles=["Developer", "QA", "Intern"],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )
        assert check_authorization(user) is False
