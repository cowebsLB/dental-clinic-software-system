"""Prescription management module."""

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


class PrescriptionManager:
    """Manages prescriptions."""
    
    def create_prescription(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create prescription."""
        if not permission_validator.validate('create_prescriptions'):
            return False, None, "Permission denied"
        
        prescription_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        prescription_data = {
            'id': prescription_id,
            'client_id': data.get('client_id'),
            'doctor_id': data.get('doctor_id'),
            'reservation_id': data.get('reservation_id'),
            'prescription_date_utc': data.get('prescription_date_utc', now),
            'status': data.get('status', 'active'),
            'notes': data.get('notes', ''),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('prescriptions').insert(prescription_data).execute()
                if response.data:
                    local_cache.insert('prescriptions', prescription_data, mark_pending=False)
                    # Add prescription items
                    items = data.get('items', [])
                    for item in items:
                        self.add_prescription_item(prescription_id, item)
                    return True, prescription_id, None
                return False, None, "Failed to create prescription"
            else:
                local_cache.insert('prescriptions', prescription_data, mark_pending=True)
                sync_queue.add_operation('prescriptions', prescription_id, 'create', prescription_data)
                return True, prescription_id, None
        except Exception as e:
            logger.error(f"Error creating prescription: {e}")
            return False, None, str(e)
    
    def add_prescription_item(self, prescription_id: str, item_data: Dict) -> tuple[bool, Optional[str]]:
        """Add item to prescription."""
        item_id = str(uuid.uuid4())
        
        item = {
            'id': item_id,
            'prescription_id': prescription_id,
            'medication_name': item_data.get('medication_name', ''),
            'dosage': item_data.get('dosage', ''),
            'frequency': item_data.get('frequency', ''),
            'duration': item_data.get('duration', ''),
            'instructions': item_data.get('instructions', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('prescription_items').insert(item).execute()
                if response.data:
                    local_cache.insert('prescription_items', item, mark_pending=False)
                    return True, item_id
                return False, "Failed to add prescription item"
            else:
                local_cache.insert('prescription_items', item, mark_pending=True)
                sync_queue.add_operation('prescription_items', item_id, 'create', item)
                return True, item_id
        except Exception as e:
            logger.error(f"Error adding prescription item: {e}")
            return False, str(e)
    
    def get_prescription(self, prescription_id: str) -> Optional[Dict]:
        """Get prescription with items."""
        prescription = local_cache.get('prescriptions', prescription_id)
        if prescription:
            items = local_cache.query('prescription_items', {'prescription_id': prescription_id})
            prescription['items'] = items
        return prescription
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all prescriptions."""
        return local_cache.query('prescriptions', limit=limit)
    
    def update(self, prescription_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update prescription."""
        if not permission_validator.validate('create_prescriptions'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        for key in ['client_id', 'doctor_id', 'reservation_id', 'prescription_date_utc', 'status', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('prescriptions').update(update_data).eq('id', prescription_id).execute()
                if response.data:
                    local_cache.update('prescriptions', prescription_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update prescription"
            else:
                existing = self.get_prescription(prescription_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('prescriptions', prescription_id, update_data, mark_pending=True)
                    sync_queue.add_operation('prescriptions', prescription_id, 'update', merged_data)
                    return True, None
                return False, "Prescription not found"
        except Exception as e:
            logger.error(f"Error updating prescription: {e}")
            return False, str(e)
    
    def delete(self, prescription_id: str) -> tuple[bool, Optional[str]]:
        """Delete prescription."""
        if not permission_validator.validate('create_prescriptions'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                # Delete prescription items first
                supabase_client.table('prescription_items').delete().eq('prescription_id', prescription_id).execute()
                # Delete prescription
                response = supabase_client.table('prescriptions').delete().eq('id', prescription_id).execute()
                if response.data:
                    local_cache.delete('prescriptions', prescription_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete prescription"
            else:
                local_cache.delete('prescriptions', prescription_id, mark_pending=True)
                sync_queue.add_operation('prescriptions', prescription_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting prescription: {e}")
            return False, str(e)


# Global instance
prescription_manager = PrescriptionManager()

