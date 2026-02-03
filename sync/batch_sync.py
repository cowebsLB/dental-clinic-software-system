"""Batch sync operations for efficient synchronization."""

import logging
from typing import List, Dict, Any
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue
from sync.conflict_handler import ConflictHandler

logger = logging.getLogger(__name__)


class BatchSync:
    """Handles batch synchronization operations."""
    
    def __init__(self):
        self.conflict_handler = ConflictHandler()
    
    def sync_table(self, table: str, operations: List[Dict]) -> Dict[str, Any]:
        """Sync a batch of operations for a table."""
        results = {
            'synced': 0,
            'failed': 0,
            'conflicts': 0,
            'errors': []
        }
        
        if not operations:
            return results
        
        # Group operations by type
        creates = [op for op in operations if op['operation'] == 'create']
        updates = [op for op in operations if op['operation'] == 'update']
        deletes = [op for op in operations if op['operation'] == 'delete']
        
        # Process creates
        if creates:
            create_results = self._batch_create(table, creates)
            results['synced'] += create_results['synced']
            results['failed'] += create_results['failed']
            results['conflicts'] += create_results['conflicts']
            results['errors'].extend(create_results['errors'])
        
        # Process updates
        if updates:
            update_results = self._batch_update(table, updates)
            results['synced'] += update_results['synced']
            results['failed'] += update_results['failed']
            results['conflicts'] += update_results['conflicts']
            results['errors'].extend(update_results['errors'])
        
        # Process deletes
        if deletes:
            delete_results = self._batch_delete(table, deletes)
            results['synced'] += delete_results['synced']
            results['failed'] += delete_results['failed']
            results['errors'].extend(delete_results['errors'])
        
        return results
    
    def _batch_create(self, table: str, operations: List[Dict]) -> Dict[str, Any]:
        """Batch create operations."""
        results = {'synced': 0, 'failed': 0, 'conflicts': 0, 'errors': []}
        client = supabase_manager.client
        
        for op in operations:
            try:
                local_data = op.get('local_data', {})
                if not local_data:
                    continue
                
                # Remove sync-related fields before sending to Supabase
                sync_fields = ['pending_sync', 'sync_status', 'original_data', 'last_synced_at']
                clean_data = {k: v for k, v in local_data.items() if k not in sync_fields}
                
                # Insert into Supabase
                response = client.table(table).insert(clean_data).execute()
                
                if response.data:
                    # Update local cache
                    record_id = local_data.get('id')
                    local_cache.mark_synced(table, record_id)
                    sync_queue.mark_synced(op['id'])
                    results['synced'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Create failed for {table}.{op['record_id']}")
            
            except Exception as e:
                logger.error(f"Error creating {table} record: {e}")
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    def _batch_update(self, table: str, operations: List[Dict]) -> Dict[str, Any]:
        """Batch update operations."""
        results = {'synced': 0, 'failed': 0, 'conflicts': 0, 'errors': []}
        client = supabase_manager.client
        
        for op in operations:
            try:
                local_data = op.get('local_data', {})
                record_id = op['record_id']
                
                if not local_data:
                    continue
                
                # Check for conflicts
                conflict = self.conflict_handler.check_conflict(table, record_id, local_data)
                if conflict:
                    sync_queue.mark_conflict(op['id'], conflict.get('remote_data'))
                    results['conflicts'] += 1
                    continue
                
                # Remove sync-related fields
                sync_fields = ['pending_sync', 'sync_status', 'original_data', 'last_synced_at']
                clean_data = {k: v for k, v in local_data.items() if k not in sync_fields}
                
                # Update in Supabase
                response = client.table(table).update(clean_data).eq('id', record_id).execute()
                
                if response.data:
                    local_cache.mark_synced(table, record_id)
                    sync_queue.mark_synced(op['id'])
                    results['synced'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Update failed for {table}.{record_id}")
            
            except Exception as e:
                logger.error(f"Error updating {table} record: {e}")
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    def _batch_delete(self, table: str, operations: List[Dict]) -> Dict[str, Any]:
        """Batch delete operations."""
        results = {'synced': 0, 'failed': 0, 'errors': []}
        client = supabase_manager.client
        
        for op in operations:
            try:
                record_id = op['record_id']
                
                # Delete from Supabase
                response = client.table(table).delete().eq('id', record_id).execute()
                
                # Remove from sync queue
                sync_queue.remove_operation(op['id'])
                results['synced'] += 1
            
            except Exception as e:
                logger.error(f"Error deleting {table} record: {e}")
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results

