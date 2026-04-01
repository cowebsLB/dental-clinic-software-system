from src_v2.shared.errors import AuthorizationError


ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"*"},
    "doctor": {
        "patients:read",
        "appointments:read",
        "appointments:write",
        "billing:read",
        "clinical:read",
        "clinical:write",
    },
    "staff": {"patients:read", "appointments:read", "operations:read"},
    "receptionist": {
        "patients:read",
        "patients:write",
        "appointments:read",
        "appointments:write",
        "billing:read",
        "billing:write",
        "operations:read",
    },
}


def assert_permission(role: str, permission: str) -> None:
    allowed = ROLE_PERMISSIONS.get(role, set())
    if "*" in allowed or permission in allowed:
        return
    raise AuthorizationError(f"Role '{role}' lacks permission '{permission}'")
