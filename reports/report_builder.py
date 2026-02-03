"""Custom report builder."""

import logging
from typing import Dict, List, Optional
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds custom reports."""
    
    def build_report(self, config: Dict) -> Dict:
        """Build a report from configuration."""
        try:
            table = config.get('table')
            filters = config.get('filters', {})
            columns = config.get('columns', [])
            
            # Get data
            data = local_cache.query(table, filters)
            
            # Filter columns if specified
            if columns:
                filtered_data = []
                for row in data:
                    filtered_row = {col: row.get(col) for col in columns if col in row}
                    filtered_data.append(filtered_row)
                data = filtered_data
            
            return {
                'success': True,
                'data': data,
                'row_count': len(data)
            }
        except Exception as e:
            logger.error(f"Error building report: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
report_builder = ReportBuilder()

