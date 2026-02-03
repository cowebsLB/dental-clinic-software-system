"""Document management module."""

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


class DocumentManager:
    """Manages documents."""
    
    def upload_document(self, client_id: str, file_path: str, document_type: str,
                       description: str = '') -> tuple[bool, Optional[str], Optional[str]]:
        """Upload document to Supabase Storage."""
        if not permission_validator.validate('edit_medical_records'):
            return False, None, "Permission denied"
        
        try:
            if network_monitor.is_online():
                # Upload to Supabase Storage
                supabase_client = supabase_manager.client
                file_name = file_path.split('/')[-1]
                storage_path = f"documents/{client_id}/{file_name}"
                
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    response = supabase_client.storage.from_('documents').upload(
                        storage_path, file_data
                    )
                
                if response:
                    # Create document record
                    doc_id = str(uuid.uuid4())
                    now = datetime.utcnow().isoformat()
                    
                    doc_data = {
                        'id': doc_id,
                        'client_id': client_id,
                        'document_type': document_type,
                        'file_path': storage_path,
                        'file_name': file_name,
                        'file_size': len(file_data),
                        'mime_type': 'application/octet-stream',  # TODO: detect MIME type
                        'description': description,
                        'uploaded_by': '',  # TODO: get from auth
                        'uploaded_at': now,
                        'created_at': now,
                        'updated_at': now
                    }
                    
                    response = supabase_client.table('documents').insert(doc_data).execute()
                    if response.data:
                        local_cache.insert('documents', doc_data, mark_pending=False)
                        return True, doc_id, None
                    return False, None, "Failed to create document record"
                else:
                    return False, None, "Failed to upload file"
            else:
                return False, None, "Cannot upload documents while offline"
        
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return False, None, str(e)
    
    def get_documents(self, client_id: str) -> List[Dict]:
        """Get documents for a client."""
        return local_cache.query('documents', {'client_id': client_id})


# Global instance
document_manager = DocumentManager()

