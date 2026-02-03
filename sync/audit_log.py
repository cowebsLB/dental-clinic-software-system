"""Conflict audit logging."""

import json
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class ConflictAudit:
    """Manages conflict audit logging."""
    
    def log_conflict(self, table_name: str, record_id: str, conflict_type: str,
                    local_data: Dict, remote_data: Dict, resolution: str,
                    resolved_by: Optional[str] = None) -> str:
        """Log a conflict resolution."""
        audit_id = str(uuid.uuid4())
        
        audit_entry = {
            'id': audit_id,
            'table_name': table_name,
            'record_id': record_id,
            'conflict_type': conflict_type,
            'local_data': json.dumps(local_data),
            'remote_data': json.dumps(remote_data),
            'resolution': resolution,
            'resolved_by': resolved_by,
            'resolved_at': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        try:
            # Try to save to Supabase first
            client = supabase_manager.client
            client.table('conflict_audit').insert(audit_entry).execute()
        except Exception as e:
            logger.warning(f"Could not save conflict audit to Supabase: {e}")
            # Fallback to local cache
            local_cache.insert('conflict_audit', audit_entry, mark_pending=True)
        
        return audit_id
    
    def get_conflict_history(self, table_name: Optional[str] = None, 
                           limit: int = 100) -> list[Dict]:
        """Get conflict audit history."""
        try:
            client = supabase_manager.client
            query = client.table('conflict_audit').select('*')
            
            if table_name:
                query = query.eq('table_name', table_name)
            
            query = query.order('created_at', desc=True).limit(limit)
            response = query.execute()
            
            # Parse JSON fields
            for entry in response.data:
                if entry.get('local_data'):
                    try:
                        entry['local_data'] = json.loads(entry['local_data'])
                    except:
                        pass
                if entry.get('remote_data'):
                    try:
                        entry['remote_data'] = json.loads(entry['remote_data'])
                    except:
                        pass
            
            return response.data
        
        except Exception as e:
            logger.error(f"Error getting conflict history: {e}")
            # Fallback to local cache
            filters = {}
            if table_name:
                filters['table_name'] = table_name
            return local_cache.query('conflict_audit', filters, limit=limit)


# Global instance
conflict_audit = ConflictAudit()

