"""Appointment reports."""

import logging
from typing import Dict, List
from datetime import datetime
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class AppointmentReports:
    """Generates appointment reports."""
    
    def get_appointment_statistics(self, start_date: str, end_date: str) -> Dict:
        """Get appointment statistics."""
        try:
            reservations = local_cache.query('reservations')
            
            filtered = [
                r for r in reservations
                if start_date <= r.get('reservation_date', '') <= end_date
            ]
            
            total = len(filtered)
            scheduled = len([r for r in filtered if r.get('status') == 'scheduled'])
            completed = len([r for r in filtered if r.get('status') == 'completed'])
            cancelled = len([r for r in filtered if r.get('status') == 'cancelled'])
            no_show = len([r for r in filtered if r.get('status') == 'no_show'])
            
            return {
                'total': total,
                'scheduled': scheduled,
                'completed': completed,
                'cancelled': cancelled,
                'no_show': no_show,
                'completion_rate': (completed / total * 100) if total > 0 else 0,
                'no_show_rate': (no_show / total * 100) if total > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error generating appointment statistics: {e}")
            return {}


# Global instance
appointment_reports = AppointmentReports()

