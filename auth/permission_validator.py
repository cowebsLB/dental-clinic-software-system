"""Server-side permission validation."""

import logging
from typing import Optional
from auth.auth_manager import auth_manager
from auth.roles import Permission, has_permission

logger = logging.getLogger(__name__)


class PermissionValidator:
    """Validates permissions for operations."""
    
    @staticmethod
    def validate(permission: str, user_id: Optional[str] = None) -> bool:
        """Validate that current user has permission."""
        if not auth_manager.is_authenticated():
            logger.warning("Permission check failed: User not authenticated")
            return False
        
        user = auth_manager.get_current_user()
        if not user:
            return False
        
        role = user.get('role', 'staff')
        
        # Check permission
        if not has_permission(role, permission):
            logger.warning(f"Permission denied: {role} does not have {permission}")
            return False
        
        return True
    
    @staticmethod
    def validate_user_access(user_id: str, resource_user_id: Optional[str] = None) -> bool:
        """Validate user can access a resource."""
        current_user = auth_manager.get_current_user()
        if not current_user:
            return False
        
        # Admins can access everything
        if current_user.get('role') == 'admin':
            return True
        
        # Users can access their own resources
        if resource_user_id and current_user.get('id') == resource_user_id:
            return True
        
        return False
    
    @staticmethod
    def require_permission(permission: str):
        """Decorator to require permission for a function."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not PermissionValidator.validate(permission):
                    raise PermissionError(f"Permission required: {permission}")
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Global instance
permission_validator = PermissionValidator()

