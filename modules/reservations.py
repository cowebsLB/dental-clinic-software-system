"""Appointment/reservation management module with locking."""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database.supabase_client import supabase_manager
from database.local_cache import local_cache
from database.sync_queue import sync_queue
from utils.network_monitor import network_monitor
from auth.permission_validator import permission_validator

logger = logging.getLogger(__name__)


class ReservationManager:
    """Manages appointment/reservation operations."""
    
    def create(self, data: Dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new reservation."""
        if not permission_validator.validate('create_appointments'):
            return False, None, "Permission denied"
        
        # Check availability
        availability = self.check_availability(
            data.get('doctor_id'),
            data.get('room_id'),
            data.get('start_time_utc'),
            data.get('end_time_utc')
        )
        
        if not availability['available']:
            return False, None, availability.get('reason', 'Time slot not available')
        
        reservation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        reservation_data = {
            'id': reservation_id,
            'client_id': data.get('client_id'),
            'doctor_id': data.get('doctor_id'),
            'room_id': data.get('room_id'),
            'reservation_date': data.get('reservation_date'),
            'start_time_utc': data.get('start_time_utc'),
            'end_time_utc': data.get('end_time_utc'),
            'status': data.get('status', 'scheduled'),
            'notes': data.get('notes', ''),
            'locked_until': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            'created_at': now,
            'updated_at': now,
            'created_by': data.get('created_by', ''),
            'last_modified_by': data.get('created_by', '')
        }
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('reservations').insert(reservation_data).execute()
                
                if response.data:
                    local_cache.insert('reservations', reservation_data, mark_pending=False)
                    logger.info(f"Reservation {reservation_id} created")
                    return True, reservation_id, None
                else:
                    return False, None, "Failed to create reservation"
            else:
                local_cache.insert('reservations', reservation_data, mark_pending=True)
                sync_queue.add_operation('reservations', reservation_id, 'create', reservation_data)
                logger.info(f"Reservation {reservation_id} created offline")
                return True, reservation_id, None
        
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            return False, None, str(e)
    
    def check_availability(self, doctor_id: Optional[str], room_id: Optional[str],
                         start_time_utc: str, end_time_utc: str) -> Dict:
        """Check if doctor and room are available."""
        try:
            # Check doctor availability
            if doctor_id:
                doctor_conflicts = self._check_conflicts('doctor_id', doctor_id, start_time_utc, end_time_utc)
                if doctor_conflicts:
                    return {'available': False, 'reason': 'Doctor not available at this time'}
            
            # Check room availability
            if room_id:
                room_conflicts = self._check_conflicts('room_id', room_id, start_time_utc, end_time_utc)
                if room_conflicts:
                    return {'available': False, 'reason': 'Room not available at this time'}
            
            return {'available': True}
        
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {'available': False, 'reason': str(e)}
    
    def _check_conflicts(self, field: str, value: str, start_time_utc: str, end_time_utc: str,
                        exclude_id: Optional[str] = None) -> List[Dict]:
        """Check for time conflicts."""
        conflicts = []
        
        # Check local cache
        all_reservations = local_cache.query('reservations', {field: value})
        
        for res in all_reservations:
            if exclude_id and res['id'] == exclude_id:
                continue
            
            res_start = res.get('start_time_utc')
            res_end = res.get('end_time_utc')
            
            if res_start and res_end:
                # Check for overlap
                if not (end_time_utc <= res_start or start_time_utc >= res_end):
                    conflicts.append(res)
        
        # Check Supabase if online
        if network_monitor.is_online():
            try:
                supabase_client = supabase_manager.client
                response = supabase_client.table('reservations').select('*').eq(field, value).execute()
                
                for res in response.data:
                    if exclude_id and res['id'] == exclude_id:
                        continue
                    
                    res_start = res.get('start_time_utc')
                    res_end = res.get('end_time_utc')
                    
                    if res_start and res_end:
                        if not (end_time_utc <= res_start or start_time_utc >= res_end):
                            conflicts.append(res)
            except Exception as e:
                logger.error(f"Error checking Supabase conflicts: {e}")
        
        return conflicts
    
    def update(self, reservation_id: str, data: Dict) -> tuple[bool, Optional[str]]:
        """Update a reservation."""
        if not permission_validator.validate('edit_appointments'):
            return False, "Permission denied"
        
        existing = self.get(reservation_id)
        if not existing:
            return False, "Reservation not found"
        
        # Check availability if time changed
        if 'start_time_utc' in data or 'end_time_utc' in data:
            start = data.get('start_time_utc', existing.get('start_time_utc'))
            end = data.get('end_time_utc', existing.get('end_time_utc'))
            
            availability = self.check_availability(
                existing.get('doctor_id'),
                existing.get('room_id'),
                start,
                end
            )
            
            if not availability['available']:
                return False, availability.get('reason', 'Time slot not available')
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'last_modified_by': data.get('last_modified_by', '')
        }
        
        for key in ['client_id', 'doctor_id', 'room_id', 'reservation_date',
                    'start_time_utc', 'end_time_utc', 'status', 'notes']:
            if key in data:
                update_data[key] = data[key]
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                response = supabase_client.table('reservations').update(update_data).eq('id', reservation_id).execute()
                
                if response.data:
                    local_cache.update('reservations', reservation_id, update_data, mark_pending=False)
                    return True, None
                else:
                    return False, "Failed to update reservation"
            else:
                merged_data = {**existing, **update_data}
                local_cache.update('reservations', reservation_id, update_data, mark_pending=True)
                sync_queue.add_operation('reservations', reservation_id, 'update', merged_data)
                return True, None
        
        except Exception as e:
            logger.error(f"Error updating reservation: {e}")
            return False, str(e)
    
    def delete(self, reservation_id: str) -> tuple[bool, Optional[str]]:
        """Cancel/delete a reservation."""
        if not permission_validator.validate('delete_appointments'):
            return False, "Permission denied"
        
        try:
            if network_monitor.is_online():
                supabase_client = supabase_manager.client
                supabase_client.table('reservations').delete().eq('id', reservation_id).execute()
                local_cache.delete('reservations', reservation_id, mark_pending=False)
                return True, None
            else:
                local_cache.delete('reservations', reservation_id, mark_pending=True)
                sync_queue.add_operation('reservations', reservation_id, 'delete')
                return True, None
        
        except Exception as e:
            logger.error(f"Error deleting reservation: {e}")
            return False, str(e)
    
    def get(self, reservation_id: str) -> Optional[Dict]:
        """Get a reservation by ID."""
        if not permission_validator.validate('view_appointments'):
            return None
        
        res = local_cache.get('reservations', reservation_id)
        if res:
            return res
        
        if network_monitor.is_online():
            try:
                supabase_client = supabase_manager.client
                response = supabase_client.table('reservations').select('*').eq('id', reservation_id).execute()
                if response.data:
                    res_data = response.data[0]
                    local_cache.insert('reservations', res_data, mark_pending=False)
                    return res_data
            except Exception as e:
                logger.error(f"Error fetching reservation: {e}")
        
        return None
    
    def list_by_date(self, date: str, doctor_id: Optional[str] = None) -> List[Dict]:
        """List reservations for a specific date."""
        if not permission_validator.validate('view_appointments'):
            return []
        
        filters = {'reservation_date': date}
        if doctor_id:
            filters['doctor_id'] = doctor_id
        
        return local_cache.query('reservations', filters)
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all reservations."""
        if not permission_validator.validate('view_appointments'):
            return []
        
        return local_cache.query('reservations', limit=limit)


# Global instance
reservation_manager = ReservationManager()

