"""Client management module."""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue
from utils.network_monitor import network_monitor
from auth.permission_validator import permission_validator
from config.settings import settings

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages client operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new client."""
        if not permission_validator.validate('edit_clients'):
            return False, None, "Permission denied"
        
        client_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        client_data = {
            'id': client_id,
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'date_of_birth': data.get('date_of_birth', ''),
            'address': data.get('address', ''),
            'medical_history': data.get('medical_history', ''),
            'notes': data.get('notes', ''),
            'created_at': now,
            'updated_at': now,
            'created_by': data.get('created_by', ''),
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            # If using SQLite mode, always use local cache
            if settings.auth_mode == 'sqlite':
                local_cache.insert('clients', client_data, mark_pending=False)
                logger.info(f"Client {client_id} created (SQLite mode)")
                return True, client_id, None
            
            # Supabase mode: check network status
            if network_monitor.is_online():
                # Online: Save to Supabase
                supabase_client = supabase_manager.client
                response = supabase_client.table('clients').insert(client_data).execute()
                
                if response.data:
                    # Update local cache
                    local_cache.insert('clients', client_data, mark_pending=False)
                    logger.info(f"Client {client_id} created")
                    return True, client_id, None
                else:
                    return False, None, "Failed to create client"
            else:
                # Offline: Save to local cache and queue
                local_cache.insert('clients', client_data, mark_pending=True)
                sync_queue.add_operation('clients', client_id, 'create', client_data)
                logger.info(f"Client {client_id} created offline, queued for sync")
                return True, client_id, None
        
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return False, None, str(e)
    
    def update(self, client_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update a client."""
        if not permission_validator.validate('edit_clients'):
            return False, "Permission denied"
        
        # Get existing data
        existing = self.get(client_id)
        if not existing:
            return False, "Client not found"
        
        # Update fields
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['first_name', 'last_name', 'phone', 'email', 'date_of_birth',
                    'address', 'medical_history', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            # If using SQLite mode, always use local cache
            if settings.auth_mode == 'sqlite':
                local_cache.update('clients', client_id, update_data, mark_pending=False)
                logger.info(f"Client {client_id} updated (SQLite mode)")
                return True, None
            
            # Supabase mode: check network status
            if network_monitor.is_online():
                # Online: Update Supabase
                supabase_client = supabase_manager.client
                response = supabase_client.table('clients').update(update_data).eq('id', client_id).execute()
                
                if response.data:
                    # Update local cache
                    local_cache.update('clients', client_id, update_data, mark_pending=False)
                    logger.info(f"Client {client_id} updated")
                    return True, None
                else:
                    return False, "Failed to update client"
            else:
                # Offline: Update local cache and queue
                merged_data = {**existing, **update_data}
                local_cache.update('clients', client_id, update_data, mark_pending=True)
                sync_queue.add_operation('clients', client_id, 'update', merged_data)
                logger.info(f"Client {client_id} updated offline, queued for sync")
                return True, None
        
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            return False, str(e)
    
    def delete(self, client_id: str) -> tuple[bool, Optional[str]]:
        """Delete a client."""
        if not permission_validator.validate('delete_clients'):
            return False, "Permission denied"
        
        try:
            # If using SQLite mode, always use local cache
            if settings.auth_mode == 'sqlite':
                local_cache.delete('clients', client_id, mark_pending=False)
                logger.info(f"Client {client_id} deleted (SQLite mode)")
                return True, None
            
            # Supabase mode: check network status
            if network_monitor.is_online():
                # Online: Delete from Supabase
                supabase_client = supabase_manager.client
                supabase_client.table('clients').delete().eq('id', client_id).execute()
                
                # Delete from local cache
                local_cache.delete('clients', client_id, mark_pending=False)
                logger.info(f"Client {client_id} deleted")
                return True, None
            else:
                # Offline: Queue deletion
                local_cache.delete('clients', client_id, mark_pending=True)
                sync_queue.add_operation('clients', client_id, 'delete')
                logger.info(f"Client {client_id} deleted offline, queued for sync")
                return True, None
        
        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            return False, str(e)
    
    def get(self, client_id: str) -> Optional[Dict]:
        """Get a client by ID."""
        if not permission_validator.validate('view_clients'):
            return None
        
        # Try local cache first
        client = local_cache.get('clients', client_id)
        if client:
            return client
        
        # Try Supabase if online
        if network_monitor.is_online():
            try:
                supabase_client = supabase_manager.client
                response = supabase_client.table('clients').select('*').eq('id', client_id).execute()
                
                if response.data:
                    client_data = response.data[0]
                    # Cache locally
                    local_cache.insert('clients', client_data, mark_pending=False)
                    return client_data
            except Exception as e:
                logger.error(f"Error fetching client from Supabase: {e}")
        
        return None
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search clients."""
        if not permission_validator.validate('view_clients'):
            return []
        
        results = []
        
        # Search local cache
        all_clients = local_cache.query('clients', limit=limit * 2)
        
        query_lower = query.lower()
        for client in all_clients:
            if (query_lower in client.get('first_name', '').lower() or
                query_lower in client.get('last_name', '').lower() or
                query_lower in client.get('email', '').lower() or
                query_lower in client.get('phone', '').lower()):
                results.append(client)
                if len(results) >= limit:
                    break
        
        # If online, also search Supabase
        if network_monitor.is_online() and len(results) < limit:
            try:
                supabase_client = supabase_manager.client
                # Simple search - can be enhanced with full-text search
                response = supabase_client.table('clients').select('*').limit(limit).execute()
                
                # Merge results
                existing_ids = {r['id'] for r in results}
                for client in response.data:
                    if client['id'] not in existing_ids:
                        # Check if matches query
                        if (query_lower in client.get('first_name', '').lower() or
                            query_lower in client.get('last_name', '').lower() or
                            query_lower in client.get('email', '').lower() or
                            query_lower in client.get('phone', '').lower()):
                            results.append(client)
                            local_cache.insert('clients', client, mark_pending=False)
                            if len(results) >= limit:
                                break
            except Exception as e:
                logger.error(f"Error searching Supabase: {e}")
        
        return results
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all clients."""
        if not permission_validator.validate('view_clients'):
            return []
        
        return local_cache.query('clients', limit=limit)


# Global instance
client_manager = ClientManager()

