"""Export/import functionality."""

import csv
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from openpyxl import Workbook
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class ExportImportManager:
    """Manages export and import operations."""
    
    def export_to_csv(self, table: str, file_path: str, filters: Optional[Dict] = None) -> bool:
        """Export table data to CSV."""
        try:
            data = local_cache.query(table, filters)
            if not data:
                return False
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_excel(self, table: str, file_path: str, filters: Optional[Dict] = None) -> bool:
        """Export table data to Excel."""
        try:
            data = local_cache.query(table, filters)
            if not data:
                return False
            
            wb = Workbook()
            ws = wb.active
            ws.title = table
            
            if data:
                # Write headers
                headers = list(data[0].keys())
                ws.append(headers)
                
                # Write data
                for row in data:
                    ws.append([row.get(h, '') for h in headers])
            
            wb.save(file_path)
            return True
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False
    
    def import_clients_from_csv(self, file_path: str) -> tuple[int, int, List[str]]:
        """Import clients from CSV."""
        imported = 0
        errors = 0
        error_messages = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Validate required fields
                        if not row.get('first_name') or not row.get('last_name'):
                            errors += 1
                            error_messages.append(f"Row missing required fields: {row}")
                            continue
                        
                        # Create client
                        from modules.clients import client_manager
                        success, client_id, error = client_manager.create({
                            'first_name': row.get('first_name', ''),
                            'last_name': row.get('last_name', ''),
                            'phone': row.get('phone', ''),
                            'email': row.get('email', ''),
                            'date_of_birth': row.get('date_of_birth', ''),
                            'address': row.get('address', ''),
                            'medical_history': row.get('medical_history', ''),
                            'notes': row.get('notes', '')
                        })
                        
                        if success:
                            imported += 1
                        else:
                            errors += 1
                            error_messages.append(f"Failed to import: {error}")
                    except Exception as e:
                        errors += 1
                        error_messages.append(f"Error processing row: {e}")
            
            return imported, errors, error_messages
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            return 0, 0, [str(e)]


# Global instance
export_import_manager = ExportImportManager()

