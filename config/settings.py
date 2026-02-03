"""Application settings and configuration management."""

import os
import json
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

# Get the project root directory (parent of config directory)
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file in project root
env_path = PROJECT_ROOT / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Try loading from current directory as fallback
    load_dotenv()


class Settings:
    """Application settings manager."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".dental_clinic"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_config()
        self._load_env_vars()
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _load_env_vars(self):
        """Load environment variables."""
        # Supabase
        self.supabase_url = os.getenv('SUPABASE_URL', '').strip()
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
        self.supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip()
        
        # GitHub
        self.github_repo = os.getenv('GITHUB_REPO', '')
        
        # Email
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        
        # SMS (Twilio)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        
        # Application
        self.app_version = os.getenv('APP_VERSION', '1.0.0')
        self.update_check_interval = int(os.getenv('UPDATE_CHECK_INTERVAL', '3600'))
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '30'))
        self.network_check_interval = int(os.getenv('NETWORK_CHECK_INTERVAL', '30'))
        
        # Auth mode: 'sqlite' or 'supabase' (default: 'sqlite' for testing)
        self.auth_mode = os.getenv('AUTH_MODE', 'sqlite').lower()
        
        # Backup
        self.backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        self.backup_interval_hours = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
        self.backup_retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        
        # Cache
        self.cache_ttl_seconds = int(os.getenv('CACHE_TTL_SECONDS', '300'))
        self.local_cache_path = os.getenv('LOCAL_CACHE_PATH', './data/local_cache.db')
        
        # Language
        self.default_language = os.getenv('DEFAULT_LANGUAGE', 'en')
    
    def validate_required_settings(self) -> tuple[bool, list[str]]:
        """Validate that required settings are configured."""
        errors = []
        
        # Only require Supabase settings if auth_mode is 'supabase'
        if self.auth_mode == 'supabase':
            if not self.supabase_url:
                errors.append("SUPABASE_URL is required (when AUTH_MODE=supabase)")
            if not self.supabase_anon_key:
                errors.append("SUPABASE_ANON_KEY is required (when AUTH_MODE=supabase)")
        
        return len(errors) == 0, errors
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._config[key] = value
        self._save_config()
    
    def get_clinic_setting(self, key: str, default: Any = None) -> Any:
        """Get a clinic setting."""
        clinic_settings = self._config.get('clinic_settings', {})
        return clinic_settings.get(key, default)
    
    def set_clinic_setting(self, key: str, value: Any):
        """Set a clinic setting."""
        if 'clinic_settings' not in self._config:
            self._config['clinic_settings'] = {}
        self._config['clinic_settings'][key] = value
        self._save_config()
    
    def get_user_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        user_prefs = self._config.get('user_preferences', {}).get(user_id, {})
        return user_prefs.get(key, default)
    
    def set_user_preference(self, user_id: str, key: str, value: Any):
        """Set a user preference."""
        if 'user_preferences' not in self._config:
            self._config['user_preferences'] = {}
        if user_id not in self._config['user_preferences']:
            self._config['user_preferences'][user_id] = {}
        self._config['user_preferences'][user_id][key] = value
        self._save_config()


# Global settings instance
settings = Settings()

