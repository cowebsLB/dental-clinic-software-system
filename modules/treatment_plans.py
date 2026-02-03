"""Treatment planning and procedures module."""

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


class TreatmentPlanManager:
    """Manages treatment plans and procedures."""
    
    def create_procedure(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a procedure in catalog."""
        if not permission_validator.validate('manage_settings'):
            return False, None, "Permission denied"
        
        procedure_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        procedure_data = {
            'id': procedure_id,
            'code': data.get('code', ''),
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'category': data.get('category', ''),
            'base_price': data.get('base_price', 0.0),
            'duration_minutes': data.get('duration_minutes', 30),
            'is_active': data.get('is_active', True),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('procedure_catalog').insert(procedure_data).execute()
                if response.data:
                    local_cache.insert('procedure_catalog', procedure_data, mark_pending=False)
                    return True, procedure_id, None
                return False, None, "Failed to create procedure"
            else:
                local_cache.insert('procedure_catalog', procedure_data, mark_pending=True)
                sync_queue.add_operation('procedure_catalog', procedure_id, 'create', procedure_data)
                return True, procedure_id, None
        except Exception as e:
            logger.error(f"Error creating procedure: {e}")
            return False, None, str(e)
    
    def create_treatment_plan(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a treatment plan."""
        if not permission_validator.validate('create_treatment_plans'):
            return False, None, "Permission denied"
        
        plan_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        plan_data = {
            'id': plan_id,
            'client_id': data.get('client_id'),
            'doctor_id': data.get('doctor_id'),
            'plan_name': data.get('plan_name', ''),
            'status': data.get('status', 'planned'),
            'total_cost': data.get('total_cost', 0.0),
            'start_date': data.get('start_date', ''),
            'completion_date': data.get('completion_date'),
            'notes': data.get('notes', ''),
            'created_by': data.get('created_by', ''),
            'created_at': now,
            'updated_at': now,
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('treatment_plans').insert(plan_data).execute()
                if response.data:
                    local_cache.insert('treatment_plans', plan_data, mark_pending=False)
                    # Add plan items
                    items = data.get('items', [])
                    for item in items:
                        self.add_plan_item(plan_id, item)
                    return True, plan_id, None
                return False, None, "Failed to create treatment plan"
            else:
                local_cache.insert('treatment_plans', plan_data, mark_pending=True)
                sync_queue.add_operation('treatment_plans', plan_id, 'create', plan_data)
                return True, plan_id, None
        except Exception as e:
            logger.error(f"Error creating treatment plan: {e}")
            return False, None, str(e)
    
    def add_plan_item(self, plan_id: str, item_data: Dict) -> tuple[bool, Optional[str]]:
        """Add item to treatment plan."""
        item_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        item = {
            'id': item_id,
            'treatment_plan_id': plan_id,
            'procedure_id': item_data.get('procedure_id'),
            'sequence_order': item_data.get('sequence_order', 0),
            'status': item_data.get('status', 'planned'),
            'cost': item_data.get('cost', 0.0),
            'notes': item_data.get('notes', ''),
            'completed_date': item_data.get('completed_date'),
            'created_at': now,
            'updated_at': now
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('treatment_plan_items').insert(item).execute()
                if response.data:
                    local_cache.insert('treatment_plan_items', item, mark_pending=False)
                    return True, item_id
                return False, "Failed to add plan item"
            else:
                local_cache.insert('treatment_plan_items', item, mark_pending=True)
                sync_queue.add_operation('treatment_plan_items', item_id, 'create', item)
                return True, item_id
        except Exception as e:
            logger.error(f"Error adding plan item: {e}")
            return False, str(e)
    
    def get_treatment_plan(self, plan_id: str) -> Optional[Dict]:
        """Get treatment plan with items."""
        plan = local_cache.get('treatment_plans', plan_id)
        if plan:
            items = local_cache.query('treatment_plan_items', {'treatment_plan_id': plan_id})
            plan['items'] = items
        return plan
    
    def list_procedures(self, active_only: bool = True) -> List[Dict]:
        """List all procedures."""
        filters = {}
        if active_only:
            filters['is_active'] = 1
        return local_cache.query('procedure_catalog', filters)
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all treatment plans."""
        return local_cache.query('treatment_plans', limit=limit)
    
    def update(self, plan_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update treatment plan."""
        if not permission_validator.validate('create_treatment_plans'):
            return False, "Permission denied"
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['plan_name', 'status', 'total_cost', 'start_date', 'completion_date', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('treatment_plans').update(update_data).eq('id', plan_id).execute()
                if response.data:
                    local_cache.update('treatment_plans', plan_id, update_data, mark_pending=False)
                    return True, None
                return False, "Failed to update treatment plan"
            else:
                existing = self.get_treatment_plan(plan_id)
                if existing:
                    merged_data = {**existing, **update_data}
                    local_cache.update('treatment_plans', plan_id, update_data, mark_pending=True)
                    sync_queue.add_operation('treatment_plans', plan_id, 'update', merged_data)
                    return True, None
                return False, "Treatment plan not found"
        except Exception as e:
            logger.error(f"Error updating treatment plan: {e}")
            return False, str(e)
    
    def delete(self, plan_id: str) -> tuple[bool, Optional[str]]:
        """Delete treatment plan."""
        if not permission_validator.validate('create_treatment_plans'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                # Delete plan items first
                supabase_client.table('treatment_plan_items').delete().eq('treatment_plan_id', plan_id).execute()
                # Delete plan
                response = supabase_client.table('treatment_plans').delete().eq('id', plan_id).execute()
                if response.data:
                    local_cache.delete('treatment_plans', plan_id, mark_pending=False)
                    return True, None
                return False, "Failed to delete treatment plan"
            else:
                local_cache.delete('treatment_plans', plan_id, mark_pending=True)
                sync_queue.add_operation('treatment_plans', plan_id, 'delete', {})
                return True, None
        except Exception as e:
            logger.error(f"Error deleting treatment plan: {e}")
            return False, str(e)


# Global instance
treatment_plan_manager = TreatmentPlanManager()

