"""Billing and invoicing module."""

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


class BillingManager:
    """Manages billing and invoicing."""
    
    def create_invoice(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create an invoice."""
        if not permission_validator.validate('edit_billing'):
            return False, None, "Permission denied"
        
        invoice_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Calculate totals
        items = data.get('items', [])
        subtotal = sum(item.get('total', 0) for item in items)
        tax_rate = data.get('tax_rate', 0.0)
        tax = subtotal * (tax_rate / 100)
        discount = data.get('discount', 0.0)
        total = subtotal + tax - discount
        
        invoice_data = {
            'id': invoice_id,
            'invoice_number': self._generate_invoice_number(),
            'client_id': data.get('client_id'),
            'reservation_id': data.get('reservation_id'),
            'treatment_plan_id': data.get('treatment_plan_id'),
            'issue_date': data.get('issue_date', now[:10]),
            'due_date': data.get('due_date', ''),
            'subtotal': subtotal,
            'tax': tax,
            'discount': discount,
            'total': total,
            'status': data.get('status', 'pending'),
            'notes': data.get('notes', ''),
            'created_by': data.get('created_by', ''),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('invoices').insert(invoice_data).execute()
                if response.data:
                    local_cache.insert('invoices', invoice_data, mark_pending=False)
                    # Add invoice items
                    for item in items:
                        self.add_invoice_item(invoice_id, item)
                    return True, invoice_id, None
                return False, None, "Failed to create invoice"
            else:
                local_cache.insert('invoices', invoice_data, mark_pending=True)
                sync_queue.add_operation('invoices', invoice_id, 'create', invoice_data)
                return True, invoice_id, None
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return False, None, str(e)
    
    def add_invoice_item(self, invoice_id: str, item_data: Dict) -> tuple[bool, Optional[str]]:
        """Add item to invoice."""
        item_id = str(uuid.uuid4())
        
        item = {
            'id': item_id,
            'invoice_id': invoice_id,
            'description': item_data.get('description', ''),
            'procedure_id': item_data.get('procedure_id'),
            'quantity': item_data.get('quantity', 1),
            'unit_price': item_data.get('unit_price', 0.0),
            'total': item_data.get('total', 0.0),
            'created_at': datetime.utcnow().isoformat()
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('invoice_items').insert(item).execute()
                if response.data:
                    local_cache.insert('invoice_items', item, mark_pending=False)
                    return True, item_id
                return False, "Failed to add invoice item"
            else:
                local_cache.insert('invoice_items', item, mark_pending=True)
                sync_queue.add_operation('invoice_items', item_id, 'create', item)
                return True, item_id
        except Exception as e:
            logger.error(f"Error adding invoice item: {e}")
            return False, str(e)
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Get invoice with items."""
        invoice = local_cache.get('invoices', invoice_id)
        if invoice:
            items = local_cache.query('invoice_items', {'invoice_id': invoice_id})
            invoice['items'] = items
        return invoice
    
    def get_outstanding_balance(self, client_id: str) -> float:
        """Get outstanding balance for a client."""
        invoices = local_cache.query('invoices', {'client_id': client_id})
        balance = 0.0
        
        for invoice in invoices:
            if invoice.get('status') in ['pending', 'overdue']:
                balance += invoice.get('total', 0.0)
        
        return balance
    
    def _generate_invoice_number(self) -> str:
        """Generate invoice number."""
        # Simple implementation - can be enhanced
        return f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all invoices."""
        return local_cache.query('invoices', limit=limit)
    
    def update(self, invoice_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update invoice."""
        if not permission_validator.validate('edit_billing'):
            return False, "Permission denied"
        
        # Recalculate totals if items changed
        items = data.get('items', [])
        if items:
            subtotal = sum(item.get('total', 0) for item in items)
            tax_rate = data.get('tax_rate', 0.0)
            tax = subtotal * (tax_rate / 100)
            discount = data.get('discount', 0.0)
            total = subtotal + tax - discount
            
            update_data = {
                'subtotal': subtotal,
                'tax': tax,
                'discount': discount,
                'total': total,
                'updated_at': datetime.utcnow().isoformat()
            }
        else:
            update_data = {
                'updated_at': datetime.utcnow().isoformat()
            }
        
        for key in ['client_id', 'reservation_id', 'treatment_plan_id', 'issue_date', 
                   'due_date', 'tax_rate', 'discount', 'status', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('invoices').update(update_data).eq('id', invoice_id).execute()
                if response.data:
                    local_cache.update('invoices', invoice_id, update_data, mark_pending=False)
                    # Update items if provided
                    if items:
                        # Delete old items
                        supabase_client.table('invoice_items').delete().eq('invoice_id', invoice_id).execute()
                        # Add new items
                        for item in items:
                            self.add_invoice_item(invoice_id, item)
                    return True, None
                return False, "Failed to update invoice"
            else:
                existing = self.get_invoice(invoice_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('invoices', invoice_id, update_data, mark_pending=True)
                    sync_queue.add_operation('invoices', invoice_id, 'update', merged_data)
                    return True, None
                return False, "Invoice not found"
        except Exception as e:
            logger.error(f"Error updating invoice: {e}")
            return False, str(e)
    
    def delete(self, invoice_id: str) -> tuple[bool, Optional[str]]:
        """Delete invoice."""
        if not permission_validator.validate('edit_billing'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                # Delete invoice items first
                supabase_client.table('invoice_items').delete().eq('invoice_id', invoice_id).execute()
                # Delete invoice
                response = supabase_client.table('invoices').delete().eq('id', invoice_id).execute()
                if response.data:
                    local_cache.delete('invoices', invoice_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete invoice"
            else:
                local_cache.delete('invoices', invoice_id, mark_pending=True)
                sync_queue.add_operation('invoices', invoice_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting invoice: {e}")
            return False, str(e)


# Global instance
billing_manager = BillingManager()

