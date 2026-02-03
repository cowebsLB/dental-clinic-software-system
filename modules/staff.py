"""Staff management module."""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue
from utils.network_monitor import network_monitor
from auth.permission_validator import permission_validator

logger = logging.getLogger(__name__)


class StaffManager:
    """Manages staff operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new staff member."""
        if not permission_validator.validate('manage_users'):
            return False, None, "Permission denied"
        
        staff_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        staff_data = {
            'id': staff_id,
            'user_id': data.get('user_id'),
            'position': data.get('position', ''),
            'hire_date': data.get('hire_date', ''),
            'is_active': data.get('is_active', True),
            'created_at': now,
            'updated_at': now,
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('staff').insert(staff_data).execute()
                if response.data:
                    local_cache.insert('staff', staff_data, mark_pending=False)
                    return True, staff_id, None
                return False, None, "Failed to create staff"
            else:
                local_cache.insert('staff', staff_data, mark_pending=True)
                sync_queue.add_operation('staff', staff_id, 'create', staff_data)
                return True, staff_id, None
        except Exception as e:
            logger.error(f"Error creating staff: {e}")
            return False, None, str(e)
    
    def update(self, staff_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update staff member."""
        if not permission_validator.validate('manage_users'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['user_id', 'position', 'hire_date', 'is_active']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('staff').update(update_data).eq('id', staff_id).execute()
                if response.data:
                    local_cache.update('staff', staff_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update staff"
            else:
                existing = self.get(staff_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('staff', staff_id, update_data, mark_pending=True)
                    sync_queue.add_operation('staff', staff_id, 'update', merged_data)
                    return True, None
                return False, "Staff not found"
        except Exception as e:
            logger.error(f"Error updating staff: {e}")
            return False, str(e)
    
    def get(self, staff_id: str) -> Optional[Dict]:
        """Get staff by ID."""
        return local_cache.get('staff', staff_id)
    
    def list_all(self, active_only: bool = True) -> List[Dict]:
        """List all staff."""
        filters = {}
        if active_only:
            filters['is_active'] = 1
        return local_cache.query('staff', filters)


# Global instance
staff_manager = StaffManager()

