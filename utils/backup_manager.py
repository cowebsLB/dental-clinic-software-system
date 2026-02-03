"""Backup and restore functionality."""

import logging
import shutil
import json
from pathlib import Path
from datetime import datetime
from database.local_cache import local_cache
from config.settings import settings

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backups."""
    
    def __init__(self):
        self.backup_dir = Path.home() / ".dental_clinic" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> tuple[bool, Optional[str]]:
        """Create a backup of local cache."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.db"
            
            # Copy database file
            db_path = Path(settings.local_cache_path)
            if db_path.exists():
                shutil.copy2(db_path, backup_file)
                
                # Create backup metadata
                metadata = {
                    'timestamp': timestamp,
                    'backup_file': str(backup_file),
                    'original_path': str(db_path)
                }
                
                metadata_file = self.backup_dir / f"backup_{timestamp}.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Backup created: {backup_file}")
                return True, str(backup_file)
            else:
                return False, "Database file not found"
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False, str(e)
    
    def restore_backup(self, backup_file: str) -> tuple[bool, Optional[str]]:
        """Restore from backup."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False, "Backup file not found"
            
            db_path = Path(settings.local_cache_path)
            
            # Create backup of current database before restore
            if db_path.exists():
                current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(db_path, current_backup)
            
            # Restore
            shutil.copy2(backup_path, db_path)
            
            logger.info(f"Backup restored from: {backup_file}")
            return True, None
        
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False, str(e)
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        for backup_file in self.backup_dir.glob("backup_*.db"):
            metadata_file = backup_file.with_suffix('.json')
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        backups.append(metadata)
                except:
                    backups.append({
                        'backup_file': str(backup_file),
                        'timestamp': backup_file.stem.replace('backup_', '')
                    })
        
        return sorted(backups, key=lambda x: x.get('timestamp', ''), reverse=True)


# Global instance
backup_manager = BackupManager()

