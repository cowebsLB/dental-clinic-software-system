"""Role definitions and permissions."""

from typing import List, Dict
from enum import Enum


class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    DOCTOR = "doctor"
    STAFF = "staff"
    RECEPTIONIST = "receptionist"


class Permission:
    """Permission definitions."""
    # Client permissions
    VIEW_CLIENTS = "view_clients"
    EDIT_CLIENTS = "edit_clients"
    DELETE_CLIENTS = "delete_clients"
    
    # Appointment permissions
    VIEW_APPOINTMENTS = "view_appointments"
    EDIT_APPOINTMENTS = "edit_appointments"
    CREATE_APPOINTMENTS = "create_appointments"
    DELETE_APPOINTMENTS = "delete_appointments"
    
    # Treatment plan permissions
    VIEW_TREATMENT_PLANS = "view_treatment_plans"
    EDIT_TREATMENT_PLANS = "edit_treatment_plans"
    CREATE_TREATMENT_PLANS = "create_treatment_plans"
    
    # Medical records permissions
    VIEW_MEDICAL_RECORDS = "view_medical_records"
    EDIT_MEDICAL_RECORDS = "edit_medical_records"
    
    # Billing permissions
    VIEW_BILLING = "view_billing"
    EDIT_BILLING = "edit_billing"
    PROCESS_PAYMENTS = "process_payments"
    
    # Reports permissions
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    
    # System permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_AUDIT_LOG = "view_audit_log"


# Role permission matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    Role.ADMIN: [
        Permission.VIEW_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.DELETE_CLIENTS,
        Permission.VIEW_APPOINTMENTS,
        Permission.EDIT_APPOINTMENTS,
        Permission.CREATE_APPOINTMENTS,
        Permission.DELETE_APPOINTMENTS,
        Permission.VIEW_TREATMENT_PLANS,
        Permission.EDIT_TREATMENT_PLANS,
        Permission.CREATE_TREATMENT_PLANS,
        Permission.VIEW_MEDICAL_RECORDS,
        Permission.EDIT_MEDICAL_RECORDS,
        Permission.VIEW_BILLING,
        Permission.EDIT_BILLING,
        Permission.PROCESS_PAYMENTS,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_AUDIT_LOG
    ],
    Role.DOCTOR: [
        Permission.VIEW_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.VIEW_APPOINTMENTS,
        Permission.EDIT_APPOINTMENTS,
        Permission.CREATE_APPOINTMENTS,
        Permission.VIEW_TREATMENT_PLANS,
        Permission.EDIT_TREATMENT_PLANS,
        Permission.CREATE_TREATMENT_PLANS,
        Permission.VIEW_MEDICAL_RECORDS,
        Permission.EDIT_MEDICAL_RECORDS,
        Permission.VIEW_REPORTS
    ],
    Role.STAFF: [
        Permission.VIEW_CLIENTS,
        Permission.VIEW_APPOINTMENTS,
        Permission.EDIT_APPOINTMENTS,
        Permission.VIEW_TREATMENT_PLANS,
        Permission.VIEW_MEDICAL_RECORDS,
        Permission.VIEW_REPORTS
    ],
    Role.RECEPTIONIST: [
        Permission.VIEW_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.VIEW_APPOINTMENTS,
        Permission.EDIT_APPOINTMENTS,
        Permission.CREATE_APPOINTMENTS,
        Permission.VIEW_BILLING,
        Permission.PROCESS_PAYMENTS
    ]
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    permissions = ROLE_PERMISSIONS.get(role, [])
    return permission in permissions


def get_role_permissions(role: str) -> List[str]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])

