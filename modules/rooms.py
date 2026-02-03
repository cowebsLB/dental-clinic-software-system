"""Room management module."""

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


class RoomManager:
    """Manages room operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new room."""
        if not permission_validator.validate('manage_settings'):
            return False, None, "Permission denied"
        
        room_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        room_data = {
            'id': room_id,
            'room_number': data.get('room_number', ''),
            'room_type': data.get('room_type', ''),
            'capacity': data.get('capacity', 1),
            'is_available': data.get('is_available', True),
            'created_at': now,
            'updated_at': now,
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('rooms').insert(room_data).execute()
                if response.data:
                    local_cache.insert('rooms', room_data, mark_pending=False)
                    return True, room_id, None
                return False, None, "Failed to create room"
            else:
                local_cache.insert('rooms', room_data, mark_pending=True)
                sync_queue.add_operation('rooms', room_id, 'create', room_data)
                return True, room_id, None
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            return False, None, str(e)
    
    def update(self, room_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update room."""
        if not permission_validator.validate('manage_settings'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['room_number', 'room_type', 'capacity', 'is_available']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('rooms').update(update_data).eq('id', room_id).execute()
                if response.data:
                    local_cache.update('rooms', room_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update room"
            else:
                existing = self.get(room_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('rooms', room_id, update_data, mark_pending=True)
                    sync_queue.add_operation('rooms', room_id, 'update', merged_data)
                    return True, None
                return False, "Room not found"
        except Exception as e:
            logger.error(f"Error updating room: {e}")
            return False, str(e)
    
    def get(self, room_id: str) -> Optional[Dict]:
        """Get room by ID."""
        return local_cache.get('rooms', room_id)
    
    def list_all(self, available_only: bool = False) -> List[Dict]:
        """List all rooms."""
        filters = {}
        if available_only:
            filters['is_available'] = 1
        return local_cache.query('rooms', filters)


# Global instance
room_manager = RoomManager()

