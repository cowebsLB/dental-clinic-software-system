from src_v2.shared.errors import DomainError


def require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise DomainError(f"{field_name} is required")


def require_non_negative(value: float, field_name: str) -> None:
    if value < 0:
        raise DomainError(f"{field_name} must be non-negative")
