"""Medical records and dental charts module."""

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


class MedicalRecordsManager:
    """Manages medical records."""
    
    def create_clinical_note(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create clinical note."""
        if not permission_validator.validate('edit_medical_records'):
            return False, None, "Permission denied"
        
        note_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        note_data = {
            'id': note_id,
            'client_id': data.get('client_id'),
            'reservation_id': data.get('reservation_id'),
            'doctor_id': data.get('doctor_id'),
            'visit_date_utc': data.get('visit_date_utc', now),
            'chief_complaint': data.get('chief_complaint', ''),
            'examination': data.get('examination', ''),
            'diagnosis': data.get('diagnosis', ''),
            'treatment_rendered': data.get('treatment_rendered', ''),
            'notes': data.get('notes', ''),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('clinical_notes').insert(note_data).execute()
                if response.data:
                    local_cache.insert('clinical_notes', note_data, mark_pending=False)
                    return True, note_id, None
                return False, None, "Failed to create clinical note"
            else:
                local_cache.insert('clinical_notes', note_data, mark_pending=True)
                sync_queue.add_operation('clinical_notes', note_id, 'create', note_data)
                return True, note_id, None
        except Exception as e:
            logger.error(f"Error creating clinical note: {e}")
            return False, None, str(e)
    
    def create_dental_chart(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create dental chart."""
        if not permission_validator.validate('edit_medical_records'):
            return False, None, "Permission denied"
        
        chart_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        chart_data = {
            'id': chart_id,
            'client_id': data.get('client_id'),
            'chart_date': data.get('chart_date', now[:10]),
            'tooth_data': data.get('tooth_data', {}),
            'chart_notes': data.get('chart_notes', ''),
            'created_by': data.get('created_by', ''),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('dental_charts').insert(chart_data).execute()
                if response.data:
                    local_cache.insert('dental_charts', chart_data, mark_pending=False)
                    return True, chart_id, None
                return False, None, "Failed to create dental chart"
            else:
                local_cache.insert('dental_charts', chart_data, mark_pending=True)
                sync_queue.add_operation('dental_charts', chart_id, 'create', chart_data)
                return True, chart_id, None
        except Exception as e:
            logger.error(f"Error creating dental chart: {e}")
            return False, None, str(e)
    
    def get_clinical_notes(self, client_id: str) -> List[Dict]:
        """Get clinical notes for a client."""
        return local_cache.query('clinical_notes', {'client_id': client_id})
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all clinical notes."""
        return local_cache.query('clinical_notes', limit=limit)
    
    def get(self, note_id: str) -> Optional[Dict]:
        """Get clinical note by ID."""
        return local_cache.get('clinical_notes', note_id)
    
    def update(self, note_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update clinical note."""
        if not permission_validator.validate('edit_medical_records'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        for key in ['client_id', 'reservation_id', 'doctor_id', 'visit_date_utc', 
                   'chief_complaint', 'examination', 'diagnosis', 'treatment_rendered', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('clinical_notes').update(update_data).eq('id', note_id).execute()
                if response.data:
                    local_cache.update('clinical_notes', note_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update clinical note"
            else:
                existing = self.get(note_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('clinical_notes', note_id, update_data, mark_pending=True)
                    sync_queue.add_operation('clinical_notes', note_id, 'update', merged_data)
                    return True, None
                return False, "Clinical note not found"
        except Exception as e:
            logger.error(f"Error updating clinical note: {e}")
            return False, str(e)
    
    def delete(self, note_id: str) -> tuple[bool, Optional[str]]:
        """Delete clinical note."""
        if not permission_validator.validate('edit_medical_records'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('clinical_notes').delete().eq('id', note_id).execute()
                if response.data:
                    local_cache.delete('clinical_notes', note_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete clinical note"
            else:
                local_cache.delete('clinical_notes', note_id, mark_pending=True)
                sync_queue.add_operation('clinical_notes', note_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting clinical note: {e}")
            return False, str(e)


# Global instance
medical_records_manager = MedicalRecordsManager()

