"""Equipment management module."""

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


class EquipmentManager:
    """Manages equipment operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create new equipment."""
        if not permission_validator.validate('manage_settings'):
            return False, None, "Permission denied"
        
        equipment_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        equipment_data = {
            'id': equipment_id,
            'room_id': data.get('room_id'),
            'equipment_name': data.get('equipment_name', ''),
            'equipment_type': data.get('equipment_type', ''),
            'serial_number': data.get('serial_number', ''),
            'status': data.get('status', 'operational'),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('equipment').insert(equipment_data).execute()
                if response.data:
                    local_cache.insert('equipment', equipment_data, mark_pending=False)
                    return True, equipment_id, None
                return False, None, "Failed to create equipment"
            else:
                local_cache.insert('equipment', equipment_data, mark_pending=True)
                sync_queue.add_operation('equipment', equipment_id, 'create', equipment_data)
                return True, equipment_id, None
        except Exception as e:
            logger.error(f"Error creating equipment: {e}")
            return False, None, str(e)
    
    def update(self, equipment_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update equipment."""
        if not permission_validator.validate('manage_settings'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        for key in ['room_id', 'equipment_name', 'equipment_type', 'serial_number', 'status']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('equipment').update(update_data).eq('id', equipment_id).execute()
                if response.data:
                    local_cache.update('equipment', equipment_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update equipment"
            else:
                existing = self.get(equipment_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('equipment', equipment_id, update_data, mark_pending=True)
                    sync_queue.add_operation('equipment', equipment_id, 'update', merged_data)
                    return True, None
                return False, "Equipment not found"
        except Exception as e:
            logger.error(f"Error updating equipment: {e}")
            return False, str(e)
    
    def get(self, equipment_id: str) -> Optional[Dict]:
        """Get equipment by ID."""
        return local_cache.get('equipment', equipment_id)
    
    def list_by_room(self, room_id: str) -> List[Dict]:
        """List equipment in a room."""
        return local_cache.query('equipment', {'room_id': room_id})
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all equipment."""
        return local_cache.query('equipment', limit=limit)
    
    def delete(self, equipment_id: str) -> tuple[bool, Optional[str]]:
        """Delete equipment."""
        if not permission_validator.validate('manage_settings'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('equipment').delete().eq('id', equipment_id).execute()
                if response.data:
                    local_cache.delete('equipment', equipment_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete equipment"
            else:
                local_cache.delete('equipment', equipment_id, mark_pending=True)
                sync_queue.add_operation('equipment', equipment_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting equipment: {e}")
            return False, str(e)


# Global instance
equipment_manager = EquipmentManager()

