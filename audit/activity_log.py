"""Activity logging."""

import logging
import uuid
from typing import Dict, Optional, List
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from utils.network_monitor import network_monitor

logger = logging.getLogger(__name__)


class ActivityLog:
    """Manages activity logs."""
    
    def log_activity(self, user_id: str, activity_type: str, description: str,
                    related_entity_type: Optional[str] = None,
                    related_entity_id: Optional[str] = None,
                    metadata: Optional[Dict] = None):
        """Log user activity."""
        activity_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        activity_entry = {
            'id': activity_id,
            'user_id': user_id,
            'activity_type': activity_type,
            'description': description,
            'related_entity_type': related_entity_type,
            'related_entity_id': related_entity_id,
            'metadata': metadata or {},
            'created_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                supabase_client.table('activity_logs').insert(activity_entry).execute()
            else:
                local_cache.insert('activity_logs', activity_entry, mark_pending=True)
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def get_activity_log(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get activity log entries."""
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        
        return local_cache.query('activity_logs', filters, limit=limit)


# Global instance
activity_log = ActivityLog()

