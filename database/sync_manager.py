"""Batch sync manager with conflict resolution."""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue
from sync.batch_sync import BatchSync
from sync.conflict_handler import ConflictHandler

logger = logging.getLogger(__name__)


class SyncManager:
    """Manages synchronization between Supabase and local cache."""
    
    def __init__(self):
        self.batch_sync = BatchSync()
        self.conflict_handler = ConflictHandler()
        self.is_syncing = False
    
    def sync_all(self, force: bool = False) -> Dict[str, any]:
        """Sync all pending operations."""
        if self.is_syncing and not force:
            logger.warning("Sync already in progress")
            return {'status': 'busy', 'message': 'Sync already in progress'}
        
        self.is_syncing = True
        results = {
            'synced': 0,
            'failed': 0,
            'conflicts': 0,
            'errors': []
        }
        
        try:
            # Get all pending operations grouped by table
            pending_ops = sync_queue.get_pending_operations()
            
            if not pending_ops:
                logger.info("No pending operations to sync")
                return results
            
            # Group by table for batch processing
            by_table = {}
            for op in pending_ops:
                table = op['table_name']
                if table not in by_table:
                    by_table[table] = []
                by_table[table].append(op)
            
            # Process each table in batches
            for table, operations in by_table.items():
                try:
                    batch_results = self.batch_sync.sync_table(table, operations)
                    results['synced'] += batch_results.get('synced', 0)
                    results['failed'] += batch_results.get('failed', 0)
                    results['conflicts'] += batch_results.get('conflicts', 0)
                    results['errors'].extend(batch_results.get('errors', []))
                except Exception as e:
                    logger.error(f"Error syncing table {table}: {e}")
                    results['failed'] += len(operations)
                    results['errors'].append(f"{table}: {str(e)}")
            
            results['status'] = 'completed'
            logger.info(f"Sync completed: {results}")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            results['status'] = 'error'
            results['errors'].append(str(e))
        finally:
            self.is_syncing = False
        
        return results
    
    def sync_table(self, table: str) -> Dict[str, any]:
        """Sync a specific table."""
        pending_ops = sync_queue.get_pending_operations(table=table)
        if not pending_ops:
            return {'status': 'no_pending', 'synced': 0}
        
        return self.batch_sync.sync_table(table, pending_ops)
    
    def resolve_conflict(self, queue_id: str, resolution: str, data: Optional[Dict] = None) -> bool:
        """Resolve a conflict manually."""
        return self.conflict_handler.resolve_conflict(queue_id, resolution, data)
    
    def get_sync_status(self) -> Dict[str, any]:
        """Get current sync status."""
        pending = sync_queue.get_pending_operations()
        conflicts = sync_queue.get_conflicts()
        
        return {
            'is_syncing': self.is_syncing,
            'pending_count': len(pending),
            'conflict_count': len(conflicts),
            'last_sync': None  # TODO: Track last sync time
        }


# Global instance
sync_manager = SyncManager()

