"""Conflict detection and resolution logic."""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue

logger = logging.getLogger(__name__)


class ConflictHandler:
    """Handles conflict detection and resolution."""
    
    def check_conflict(self, table: str, record_id: str, local_data: Dict) -> Optional[Dict]:
        """Check if there's a conflict between local and remote data."""
        try:
            client = supabase_manager.client
            
            # Get remote data
            response = client.table(table).select('*').eq('id', record_id).execute()
            
            if not response.data:
                # Record doesn't exist remotely, no conflict
                return None
            
            remote_data = response.data[0]
            local_updated = local_data.get('updated_at')
            remote_updated = remote_data.get('updated_at')
            
            if not local_updated or not remote_updated:
                return None
            
            # Parse timestamps
            try:
                local_time = datetime.fromisoformat(local_updated.replace('Z', '+00:00'))
                remote_time = datetime.fromisoformat(remote_updated.replace('Z', '+00:00'))
                
                # If remote is newer, there's a conflict
                if remote_time > local_time:
                    return {
                        'type': 'timestamp_conflict',
                        'local_data': local_data,
                        'remote_data': remote_data,
                        'local_updated': local_updated,
                        'remote_updated': remote_updated
                    }
            except ValueError as e:
                logger.warning(f"Error parsing timestamps: {e}")
                return None
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking conflict: {e}")
            return None
    
    def resolve_conflict(self, queue_id: str, resolution: str, data: Optional[Dict] = None) -> bool:
        """Resolve a conflict manually.
        
        Args:
            queue_id: ID of the sync queue item
            resolution: 'local', 'remote', or 'merge'
            data: Merged data if resolution is 'merge'
        """
        try:
            # Get queue item
            queue_item = local_cache.get('sync_queue', queue_id)
            if not queue_item:
                return False
            
            table = queue_item['table_name']
            record_id = queue_item['record_id']
            client = supabase_manager.client
            
            if resolution == 'local':
                # Use local data
                local_data = queue_item.get('local_data')
                if isinstance(local_data, str):
                    import json
                    local_data = json.loads(local_data)
                
                sync_fields = ['pending_sync', 'sync_status', 'original_data', 'last_synced_at']
                clean_data = {k: v for k, v in local_data.items() if k not in sync_fields}
                
                client.table(table).update(clean_data).eq('id', record_id).execute()
                local_cache.mark_synced(table, record_id)
                sync_queue.mark_synced(queue_id)
            
            elif resolution == 'remote':
                # Use remote data
                response = client.table(table).select('*').eq('id', record_id).execute()
                if response.data:
                    remote_data = response.data[0]
                    local_cache.insert(table, remote_data, mark_pending=False)
                    sync_queue.mark_synced(queue_id)
            
            elif resolution == 'merge' and data:
                # Use merged data
                sync_fields = ['pending_sync', 'sync_status', 'original_data', 'last_synced_at']
                clean_data = {k: v for k, v in data.items() if k not in sync_fields}
                
                client.table(table).update(clean_data).eq('id', record_id).execute()
                local_cache.insert(table, clean_data, mark_pending=False)
                sync_queue.mark_synced(queue_id)
            
            else:
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return False
    
    def auto_resolve_conflict(self, conflict: Dict) -> bool:
        """Automatically resolve conflict using last-write-wins."""
        local_updated = conflict.get('local_updated')
        remote_updated = conflict.get('remote_updated')
        
        try:
            local_time = datetime.fromisoformat(local_updated.replace('Z', '+00:00'))
            remote_time = datetime.fromisoformat(remote_updated.replace('Z', '+00:00'))
            
            # Last write wins - use remote if it's newer
            if remote_time > local_time:
                return self.resolve_conflict(
                    conflict.get('queue_id', ''),
                    'remote'
                )
            else:
                return self.resolve_conflict(
                    conflict.get('queue_id', ''),
                    'local'
                )
        
        except Exception as e:
            logger.error(f"Error auto-resolving conflict: {e}")
            return False

