"""Reminder scheduling and sending service."""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from utils.network_monitor import network_monitor

logger = logging.getLogger(__name__)


class ReminderService:
    """Manages reminders."""
    
    def create_reminder(self, reminder_type: str, related_id: str, client_id: str,
                      reminder_date_utc: str, method: str = 'email') -> tuple[bool, Optional[str]]:
        """Create a reminder."""
        reminder_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        reminder_data = {
            'id': reminder_id,
            'reminder_type': reminder_type,
            'related_id': related_id,
            'client_id': client_id,
            'reminder_date_utc': reminder_date_utc,
            'status': 'pending',
            'method': method,
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('reminders').insert(reminder_data).execute()
                if response.data:
                    local_cache.insert('reminders', reminder_data, mark_pending=False)
                    return True, reminder_id
                return False, "Failed to create reminder"
            else:
                local_cache.insert('reminders', reminder_data, mark_pending=True)
                return True, reminder_id
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return False, str(e)
    
    def get_pending_reminders(self) -> List[Dict]:
        """Get pending reminders that are due."""
        now = datetime.utcnow().isoformat()
        reminders = local_cache.query('reminders', {'status': 'pending'})
        
        # Filter by date
        due_reminders = [
            r for r in reminders 
            if r.get('reminder_date_utc', '') <= now
        ]
        
        return due_reminders


# Global instance
reminder_service = ReminderService()

