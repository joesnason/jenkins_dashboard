"""Integration tests for authentication flow."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from models.user import User
from services.auth import authenticate_user, check_authorization, logout_user


class TestAuthenticationFlow:
    """Integration tests for the authentication flow."""

    def test_authenticated_pm_can_access_dashboard(self) -> None:
        """Test that authenticated PM can access the dashboard."""
        mock_st_user = MagicMock()
        mock_st_user.is_logged_in = True
        mock_st_user.get.side_effect = lambda key, default=None: {
            "sub": "user123",
            "email": "pm@company.com",
            "name": "Test PM",
            "groups": ["PM"],
        }.get(key, default)

        with patch("services.auth.st") as mock_st:
            mock_st.user = mock_st_user

            user = authenticate_user()

            assert user is not None
            assert user.email == "pm@company.com"
            assert check_authorization(user) is True

    def test_authenticated_rd_manager_can_access_dashboard(self) -> None:
        """Test that authenticated RD Manager can access the dashboard."""
        mock_st_user = MagicMock()
        mock_st_user.is_logged_in = True
        mock_st_user.get.side_effect = lambda key, default=None: {
            "sub": "user456",
            "email": "rdm@company.com",
            "name": "Test RD Manager",
            "groups": ["RD_Manager"],
        }.get(key, default)

        with patch("services.auth.st") as mock_st:
            mock_st.user = mock_st_user

            user = authenticate_user()

            assert user is not None
            assert check_authorization(user) is True

    def test_authenticated_developer_cannot_access_dashboard(self) -> None:
        """Test that authenticated developer cannot access the dashboard."""
        mock_st_user = MagicMock()
        mock_st_user.is_logged_in = True
        mock_st_user.get.side_effect = lambda key, default=None: {
            "sub": "user789",
            "email": "dev@company.com",
            "name": "Test Developer",
            "groups": ["Developer"],
        }.get(key, default)

        with patch("services.auth.st") as mock_st:
            mock_st.user = mock_st_user

            user = authenticate_user()

            assert user is not None
            assert check_authorization(user) is False

    def test_unauthenticated_user_returns_none(self) -> None:
        """Test that unauthenticated user returns None."""
        mock_st_user = MagicMock()
        mock_st_user.is_logged_in = False

        with patch("services.auth.st") as mock_st:
            mock_st.user = mock_st_user

            user = authenticate_user()

            assert user is None

    def test_logout_calls_st_logout(self) -> None:
        """Test that logout calls Streamlit logout."""
        user = User(
            id="user123",
            email="pm@company.com",
            name="Test PM",
            roles=["PM"],
            login_time=datetime(2026, 1, 8, 10, 0, 0),
        )

        with patch("services.auth.st") as mock_st:
            with patch("services.auth.log_event") as mock_log:
                logout_user(user, "192.168.1.100")

                mock_st.logout.assert_called_once()
                mock_log.assert_called_once()
