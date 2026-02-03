"""Doctor management module."""

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


class DoctorManager:
    """Manages doctor operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new doctor."""
        if not permission_validator.validate('manage_users'):
            return False, None, "Permission denied"
        
        doctor_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        doctor_data = {
            'id': doctor_id,
            'user_id': data.get('user_id'),
            'specialization': data.get('specialization', ''),
            'license_number': data.get('license_number', ''),
            'hire_date': data.get('hire_date', ''),
            'is_active': data.get('is_active', True),
            'created_at': now,
            'updated_at': now,
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('doctors').insert(doctor_data).execute()
                if response.data:
                    local_cache.insert('doctors', doctor_data, mark_pending=False)
                    return True, doctor_id, None
                return False, None, "Failed to create doctor"
            else:
                local_cache.insert('doctors', doctor_data, mark_pending=True)
                sync_queue.add_operation('doctors', doctor_id, 'create', doctor_data)
                return True, doctor_id, None
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            return False, None, str(e)
    
    def update(self, doctor_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update doctor."""
        if not permission_validator.validate('manage_users'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['user_id', 'specialization', 'license_number', 'hire_date', 'is_active']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('doctors').update(update_data).eq('id', doctor_id).execute()
                if response.data:
                    local_cache.update('doctors', doctor_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update doctor"
            else:
                existing = self.get(doctor_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('doctors', doctor_id, update_data, mark_pending=True)
                    sync_queue.add_operation('doctors', doctor_id, 'update', merged_data)
                    return True, None
                return False, "Doctor not found"
        except Exception as e:
            logger.error(f"Error updating doctor: {e}")
            return False, str(e)
    
    def get(self, doctor_id: str) -> Optional[Dict]:
        """Get doctor by ID."""
        return local_cache.get('doctors', doctor_id)
    
    def list_all(self, active_only: bool = True) -> List[Dict]:
        """List all doctors."""
        filters = {}
        if active_only:
            filters['is_active'] = 1
        return local_cache.query('doctors', filters)


# Global instance
doctor_manager = DoctorManager()

