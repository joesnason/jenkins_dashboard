"""Custom exceptions for the Jenkins Dashboard application."""


class JenkinsConnectionError(Exception):
    """Raised when unable to connect to Jenkins server."""

    pass


class JenkinsAuthError(Exception):
    """Raised when Jenkins API authentication fails."""

    pass


class JenkinsJobNotFoundError(Exception):
    """Raised when a specified Jenkins job does not exist."""

    pass


class AuthorizationError(Exception):
    """Raised when a user does not have permission to access a resource."""

    pass
