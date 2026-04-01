class DomainError(Exception):
    """Raised when domain rules are violated."""


class AuthorizationError(Exception):
    """Raised when caller lacks required permission."""
