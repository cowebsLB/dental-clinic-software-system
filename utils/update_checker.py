"""GitHub release checker with checksum verification."""

import logging
import requests
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict
from PySide6.QtCore import QObject, Signal, QThread
from config.settings import settings

logger = logging.getLogger(__name__)


class UpdateChecker(QObject):
    """Checks for updates from GitHub releases."""
    
    update_available = Signal(str, str, str)  # version, download_url, checksum
    download_progress = Signal(int)  # progress percentage
    download_complete = Signal(str)  # file path
    download_error = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        self.github_repo = settings.github_repo
        self.current_version = settings.app_version
        self.download_dir = Path.home() / ".dental_clinic" / "updates"
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check for available updates."""
        if not self.github_repo:
            logger.warning("GitHub repo not configured")
            return None
        
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                # Find Windows installer asset
                assets = release_data.get('assets', [])
                installer_asset = None
                checksum_asset = None
                
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if name.endswith('.exe') or name.endswith('.msi'):
                        installer_asset = asset
                    elif 'checksum' in name or 'sha256' in name:
                        checksum_asset = asset
                
                if installer_asset:
                    return {
                        'version': latest_version,
                        'download_url': installer_asset.get('browser_download_url'),
                        'checksum_url': checksum_asset.get('browser_download_url') if checksum_asset else None,
                        'release_notes': release_data.get('body', '')
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def download_update(self, download_url: str, checksum: Optional[str] = None):
        """Download update in background."""
        thread = UpdateDownloadThread(download_url, checksum, self.download_dir)
        thread.progress.connect(self.download_progress.emit)
        thread.complete.connect(self.download_complete.emit)
        thread.error.connect(self.download_error.emit)
        thread.start()
    
    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum.lower() == expected_checksum.lower()
        
        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
        def normalize_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = normalize_version(v1)
            v2_parts = normalize_version(v2)
            
            # Pad with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for a, b in zip(v1_parts, v2_parts):
                if a > b:
                    return 1
                elif a < b:
                    return -1
            
            return 0
        except:
            return 0


class UpdateDownloadThread(QThread):
    """Thread for downloading updates."""
    
    progress = Signal(int)
    complete = Signal(str)
    error = Signal(str)
    
    def __init__(self, download_url: str, checksum: Optional[str], download_dir: Path):
        super().__init__()
        self.download_url = download_url
        self.checksum = checksum
        self.download_dir = download_dir
    
    def run(self):
        """Download file."""
        try:
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get filename from URL or Content-Disposition
            filename = self.download_url.split('/')[-1]
            file_path = self.download_dir / filename
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)
            
            # Verify checksum if provided
            if self.checksum:
                checker = UpdateChecker()
                if not checker.verify_checksum(str(file_path), self.checksum):
                    os.remove(file_path)
                    self.error.emit("Checksum verification failed")
                    return
            
            self.complete.emit(str(file_path))
        
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            self.error.emit(str(e))


# Global instance
update_checker = UpdateChecker()

