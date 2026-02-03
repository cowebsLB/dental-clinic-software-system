"""Insurance management module."""

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


class InsuranceManager:
    """Manages insurance."""
    
    def create_insurance_company(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create insurance company."""
        if not permission_validator.validate('manage_settings'):
            return False, None, "Permission denied"
        
        company_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        company_data = {
            'id': company_id,
            'company_name': data.get('company_name', ''),
            'contact_info': data.get('contact_info', {}),
            'claims_email': data.get('claims_email', ''),
            'phone': data.get('phone', ''),
            'is_active': data.get('is_active', True),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('insurance_companies').insert(company_data).execute()
                if response.data:
                    local_cache.insert('insurance_companies', company_data, mark_pending=False)
                    return True, company_id, None
                return False, None, "Failed to create insurance company"
            else:
                local_cache.insert('insurance_companies', company_data, mark_pending=True)
                sync_queue.add_operation('insurance_companies', company_id, 'create', company_data)
                return True, company_id, None
        except Exception as e:
            logger.error(f"Error creating insurance company: {e}")
            return False, None, str(e)
    
    def create_claim(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create insurance claim."""
        if not permission_validator.validate('edit_billing'):
            return False, None, "Permission denied"
        
        claim_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        claim_data = {
            'id': claim_id,
            'client_id': data.get('client_id'),
            'reservation_id': data.get('reservation_id'),
            'insurance_company_id': data.get('insurance_company_id'),
            'claim_number': self._generate_claim_number(),
            'submission_date': data.get('submission_date', now[:10]),
            'amount': data.get('amount', 0.0),
            'status': data.get('status', 'pending'),
            'response_date': data.get('response_date'),
            'notes': data.get('notes', ''),
            'created_by': data.get('created_by', ''),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('insurance_claims').insert(claim_data).execute()
                if response.data:
                    local_cache.insert('insurance_claims', claim_data, mark_pending=False)
                    return True, claim_id, None
                return False, None, "Failed to create claim"
            else:
                local_cache.insert('insurance_claims', claim_data, mark_pending=True)
                sync_queue.add_operation('insurance_claims', claim_id, 'create', claim_data)
                return True, claim_id, None
        except Exception as e:
            logger.error(f"Error creating claim: {e}")
            return False, None, str(e)
    
    def _generate_claim_number(self) -> str:
        """Generate claim number."""
        return f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all insurance claims."""
        return local_cache.query('insurance_claims', limit=limit)
    
    def get(self, claim_id: str) -> Optional[Dict]:
        """Get insurance claim by ID."""
        return local_cache.get('insurance_claims', claim_id)
    
    def update(self, claim_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update insurance claim."""
        if not permission_validator.validate('edit_billing'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        for key in ['client_id', 'reservation_id', 'insurance_company_id', 'submission_date',
                   'amount', 'status', 'response_date', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('insurance_claims').update(update_data).eq('id', claim_id).execute()
                if response.data:
                    local_cache.update('insurance_claims', claim_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update insurance claim"
            else:
                existing = self.get(claim_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('insurance_claims', claim_id, update_data, mark_pending=True)
                    sync_queue.add_operation('insurance_claims', claim_id, 'update', merged_data)
                    return True, None
                return False, "Insurance claim not found"
        except Exception as e:
            logger.error(f"Error updating insurance claim: {e}")
            return False, str(e)
    
    def delete(self, claim_id: str) -> tuple[bool, Optional[str]]:
        """Delete insurance claim."""
        if not permission_validator.validate('edit_billing'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('insurance_claims').delete().eq('id', claim_id).execute()
                if response.data:
                    local_cache.delete('insurance_claims', claim_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete insurance claim"
            else:
                local_cache.delete('insurance_claims', claim_id, mark_pending=True)
                sync_queue.add_operation('insurance_claims', claim_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting insurance claim: {e}")
            return False, str(e)


# Global instance
insurance_manager = InsuranceManager()

