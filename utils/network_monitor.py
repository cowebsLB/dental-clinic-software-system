"""Event-driven network monitoring."""

import logging
import threading
import time
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal
from database.supabase_client import supabase_manager
from config.settings import settings

logger = logging.getLogger(__name__)


class NetworkMonitor(QObject):
    """Monitors network connectivity and triggers events."""
    
    # Signals
    status_changed = Signal(bool)  # Emitted when online/offline status changes
    
    def __init__(self):
        super().__init__()
        self._is_online = True
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable] = []
        self.check_interval = settings.network_check_interval
    
    def start_monitoring(self):
        """Start network monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Network monitoring started")
    
    def stop_monitoring(self):
        """Stop network monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        logger.info("Network monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                was_online = self._is_online
                self._is_online = self._check_connection()
                
                # Emit signal if status changed
                if was_online != self._is_online:
                    logger.info(f"Network status changed: {'online' if self._is_online else 'offline'}")
                    self.status_changed.emit(self._is_online)
                    
                    # Call registered callbacks
                    for callback in self._callbacks:
                        try:
                            callback(self._is_online)
                        except Exception as e:
                            logger.error(f"Error in network status callback: {e}")
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error in network monitor loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_connection(self) -> bool:
        """Check if connection to Supabase is available."""
        try:
            # Simple ping to Supabase
            client = supabase_manager.client
            response = client.table('clients').select('id').limit(1).execute()
            return True
        except Exception:
            return False
    
    def is_online(self) -> bool:
        """Check current online status."""
        return self._is_online
    
    def register_callback(self, callback: Callable[[bool], None]):
        """Register a callback for network status changes."""
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[bool], None]):
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# Global instance
network_monitor = NetworkMonitor()

