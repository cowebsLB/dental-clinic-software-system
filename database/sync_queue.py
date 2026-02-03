"""Transactional sync queue management."""

import json
import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class SyncQueue:
    """Manages sync queue operations."""
    
    def __init__(self):
        self.cache = local_cache
    
    def add_operation(self, table: str, record_id: str, operation: str, 
                     local_data: Optional[Dict] = None, remote_data: Optional[Dict] = None):
        """Add an operation to the sync queue."""
        queue_item = {
            'id': str(uuid.uuid4()),
            'table_name': table,
            'record_id': record_id,
            'operation': operation,
            'local_data': json.dumps(local_data) if local_data else None,
            'remote_data': json.dumps(remote_data) if remote_data else None,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.cache.insert('sync_queue', queue_item, mark_pending=False)
        logger.debug(f"Added {operation} operation for {table}.{record_id} to sync queue")
    
    def get_pending_operations(self, table: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get pending sync operations."""
        filters = {'status': 'pending'}
        if table:
            filters['table_name'] = table
        
        operations = self.cache.query('sync_queue', filters, limit=limit)
        
        # Parse JSON fields
        for op in operations:
            if op.get('local_data'):
                try:
                    op['local_data'] = json.loads(op['local_data'])
                except:
                    pass
            if op.get('remote_data'):
                try:
                    op['remote_data'] = json.loads(op['remote_data'])
                except:
                    pass
        
        return operations
    
    def mark_synced(self, queue_id: str, synced_at: Optional[datetime] = None):
        """Mark a queue item as synced."""
        update_data = {
            'status': 'synced',
            'synced_at': (synced_at or datetime.utcnow()).isoformat()
        }
        
        self.cache.update('sync_queue', queue_id, update_data, mark_pending=False)
        logger.debug(f"Marked sync queue item {queue_id} as synced")
    
    def mark_conflict(self, queue_id: str, remote_data: Optional[Dict] = None):
        """Mark a queue item as having a conflict."""
        update_data = {
            'status': 'conflict'
        }
        if remote_data:
            update_data['remote_data'] = json.dumps(remote_data)
        
        self.cache.update('sync_queue', queue_id, update_data, mark_pending=False)
        logger.warning(f"Marked sync queue item {queue_id} as conflict")
    
    def remove_operation(self, queue_id: str):
        """Remove an operation from the sync queue."""
        self.cache.delete('sync_queue', queue_id, mark_pending=False)
    
    def get_conflicts(self) -> List[Dict]:
        """Get all conflict items."""
        return self.cache.query('sync_queue', {'status': 'conflict'})
    
    def clear_synced(self, older_than_days: int = 7):
        """Clear synced items older than specified days."""
        # This would need a date comparison query
        # For now, we'll keep all items for audit purposes
        pass


# Global instance
sync_queue = SyncQueue()

