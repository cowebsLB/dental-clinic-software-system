"""Complete change history tracking."""

import logging
import uuid
from typing import Dict, Optional, List
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from utils.network_monitor import network_monitor

logger = logging.getLogger(__name__)


class AuditTrail:
    """Manages audit trail."""
    
    def log_change(self, table_name: str, record_id: str, operation: str,
                   old_values: Optional[Dict], new_values: Optional[Dict],
                   changed_by: str, ip_address: str = '', user_agent: str = ''):
        """Log a data change."""
        audit_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        audit_entry = {
            'id': audit_id,
            'table_name': table_name,
            'record_id': record_id,
            'operation': operation,
            'old_values': old_values or {},
            'new_values': new_values or {},
            'changed_by': changed_by,
            'changed_at': now,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                supabase_client.table('audit_logs').insert(audit_entry).execute()
            else:
                local_cache.insert('audit_logs', audit_entry, mark_pending=True)
        except Exception as e:
            logger.error(f"Error logging audit trail: {e}")
    
    def get_audit_log(self, table_name: Optional[str] = None, 
                      record_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get audit log entries."""
        filters = {}
        if table_name:
            filters['table_name'] = table_name
        if record_id:
            filters['record_id'] = record_id
        
        return local_cache.query('audit_logs', filters, limit=limit)


# Global instance
audit_trail = AuditTrail()

