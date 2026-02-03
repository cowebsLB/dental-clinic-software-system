"""Payment processing module with reconciliation."""

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


class PaymentManager:
    """Manages payment operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new payment."""
        if not permission_validator.validate('process_payments'):
            return False, None, "Permission denied"
        
        payment_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        payment_data = {
            'id': payment_id,
            'reservation_id': data.get('reservation_id'),
            'client_id': data.get('client_id'),
            'amount': data.get('amount', 0.0),
            'payment_method': data.get('payment_method', 'cash'),
            'payment_date_utc': data.get('payment_date_utc', now),
            'status': data.get('status', 'pending'),
            'notes': data.get('notes', ''),
            'processed_by': data.get('processed_by', ''),
            'created_at': now,
            'updated_at': now,
            'last_modified_by': data.get('processed_by', '')
        }
        
        try:
            if network_monitor.is_online():
                # Check for duplicates before creating
                if self._check_duplicate(payment_data):
                    return False, None, "Duplicate payment detected"
                
                supabase_client = supabase_manager.client
                response = supabase_client.table('payments').insert(payment_data).execute()
                if response.data:
                    local_cache.insert('payments', payment_data, mark_pending=False)
                    logger.info(f"Payment {payment_id} created")
                    return True, payment_id, None
                return False, None, "Failed to create payment"
            else:
                local_cache.insert('payments', payment_data, mark_pending=True)
                sync_queue.add_operation('payments', payment_id, 'create', payment_data)
                logger.info(f"Payment {payment_id} created offline")
                return True, payment_id, None
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return False, None, str(e)
    
    def _check_duplicate(self, payment_data: Dict) -> bool:
        """Check for duplicate payments."""
        try:
            reservation_id = payment_data.get('reservation_id')
            amount = payment_data.get('amount')
            payment_date = payment_data.get('payment_date_utc')
            
            if not all([reservation_id, amount, payment_date]):
                return False
            
            # Check local cache
            local_payments = local_cache.query('payments', {
                'reservation_id': reservation_id,
                'amount': amount
            })
            
            for payment in local_payments:
                if payment.get('payment_date_utc') == payment_date:
                    return True
            
            # Check Supabase
            supabase_client = supabase_manager.client
            response = supabase_client.table('payments').select('*').eq('reservation_id', reservation_id).eq('amount', amount).execute()
            
            for payment in response.data:
                if payment.get('payment_date_utc') == payment_date:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False
    
    def update(self, payment_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update payment."""
        if not permission_validator.validate('process_payments'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['amount', 'payment_method', 'payment_date_utc', 'status', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('payments').update(update_data).eq('id', payment_id).execute()
                if response.data:
                    local_cache.update('payments', payment_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update payment"
            else:
                existing = self.get(payment_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('payments', payment_id, update_data, mark_pending=True)
                    sync_queue.add_operation('payments', payment_id, 'update', merged_data)
                    return True, None
                return False, "Payment not found"
        except Exception as e:
            logger.error(f"Error updating payment: {e}")
            return False, str(e)
    
    def get(self, payment_id: str) -> Optional[Dict]:
        """Get payment by ID."""
        return local_cache.get('payments', payment_id)
    
    def list_by_client(self, client_id: str) -> List[Dict]:
        """List payments for a client."""
        return local_cache.query('payments', {'client_id': client_id})
    
    def list_by_reservation(self, reservation_id: str) -> List[Dict]:
        """List payments for a reservation."""
        return local_cache.query('payments', {'reservation_id': reservation_id})
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all payments."""
        return local_cache.query('payments', limit=limit)
    
    def delete(self, payment_id: str) -> tuple[bool, Optional[str]]:
        """Delete payment."""
        if not permission_validator.validate('process_payments'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('payments').delete().eq('id', payment_id).execute()
                if response.data:
                    local_cache.delete('payments', payment_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete payment"
            else:
                local_cache.delete('payments', payment_id, mark_pending=True)
                sync_queue.add_operation('payments', payment_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting payment: {e}")
            return False, str(e)


# Global instance
payment_manager = PaymentManager()

