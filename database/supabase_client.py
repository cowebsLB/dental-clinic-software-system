"""Supabase client initialization and management."""

from supabase import create_client, Client
from typing import Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase client connection."""
    
    _instance: Optional['SupabaseManager'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Don't initialize immediately - wait until client is accessed
        pass
    
    def _initialize_client(self):
        """Initialize Supabase client."""
        if self._client is not None:
            return  # Already initialized
        
        try:
            if not settings.supabase_url or not settings.supabase_anon_key:
                raise ValueError("Supabase URL and anon key must be configured")
            
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_service_client(self) -> Client:
        """Get Supabase client with service role key (for admin operations)."""
        if not settings.supabase_service_role_key:
            raise ValueError("Service role key not configured")
        
        return create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    def test_connection(self) -> bool:
        """Test Supabase connection."""
        try:
            # Simple query to test connection
            response = self.client.table('clients').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global instance
supabase_manager = SupabaseManager()

