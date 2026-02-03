"""Authentication manager supporting both SQLite and Supabase."""

import logging
import uuid
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime
from database.local_cache import LocalCache
from database.supabase_client import supabase_manager
from config.settings import settings

logger = logging.getLogger(__name__)

# Global cache instance
local_cache = LocalCache()


class AuthManager:
    """Manages authentication and user sessions."""
    
    def __init__(self):
        self.current_user: Optional[Dict] = None
        self.session_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.auth_mode = settings.auth_mode
    
    def login(self, username: str, password: str) -> tuple[bool, Optional[str]]:
        """Login with username and password."""
        if self.auth_mode == 'sqlite':
            return self._login_sqlite(username, password)
        else:
            return self._login_supabase(username, password)
    
    def _login_sqlite(self, username: str, password: str) -> tuple[bool, Optional[str]]:
        """Login using SQLite database."""
        try:
            conn = local_cache._get_connection()
            
            # Find user by username
            cursor = conn.execute(
                "SELECT id, username, email, password_hash, full_name FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user_row = cursor.fetchone()
            
            if not user_row:
                logger.warning(f"Login attempt with invalid username: {username}")
                return False, "Invalid username or password"
            
            user_id, db_username, email, password_hash, full_name = user_row
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                logger.warning(f"Login attempt with invalid password for user: {username}")
                return False, "Invalid username or password"
            
            # Get user role
            role = self.get_user_role(user_id)
            
            # Update last login
            now = datetime.utcnow().isoformat()
            conn.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (now, user_id)
            )
            conn.commit()
            
            # Set current user
            self.current_user = {
                'id': user_id,
                'username': db_username,
                'email': email,
                'full_name': full_name,
                'role': role,
                'created_at': None  # Can be fetched if needed
            }
            
            # Generate a simple session token (for SQLite mode)
            self.session_token = f"sqlite_session_{user_id}_{uuid.uuid4().hex[:16]}"
            
            logger.info(f"User {username} logged in successfully (SQLite)")
            return True, None
        
        except Exception as e:
            logger.error(f"Login error (SQLite): {e}")
            return False, str(e)
    
    def _login_supabase(self, username: str, password: str) -> tuple[bool, Optional[str]]:
        """Login using Supabase Auth."""
        try:
            client = supabase_manager.client
            
            # First, try to find email by username
            if '@' in username:
                email = username
            else:
                email = self._get_email_from_username(username)
                if not email:
                    return False, "Invalid username"
            
            # Sign in with Supabase Auth using email
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                username_from_db = self._get_username_from_user_id(response.user.id)
                
                self.current_user = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'username': username_from_db or username,
                    'created_at': response.user.created_at
                }
                self.session_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                
                role = self.get_user_role(response.user.id)
                self.current_user['role'] = role
                
                logger.info(f"User {username} ({email}) logged in successfully (Supabase)")
                return True, None
            else:
                return False, "Invalid credentials"
        
        except Exception as e:
            logger.error(f"Login error (Supabase): {e}")
            return False, str(e)
    
    def logout(self) -> bool:
        """Logout current user."""
        try:
            if self.auth_mode == 'supabase':
                client = supabase_manager.client
                client.auth.sign_out()
            
            self.current_user = None
            self.session_token = None
            self.refresh_token = None
            
            logger.info("User logged out")
            return True
        
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current logged-in user."""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        if self.auth_mode == 'sqlite':
            return self.current_user is not None and self.session_token is not None
        else:
            return self.current_user is not None and self.session_token is not None
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role from database."""
        try:
            if self.auth_mode == 'sqlite':
                conn = local_cache._get_connection()
                cursor = conn.execute(
                    "SELECT role FROM user_roles WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
                return 'staff'  # Default role
            else:
                client = supabase_manager.client
                response = client.table('user_roles').select('role').eq('user_id', user_id).execute()
                
                if response.data:
                    return response.data[0].get('role', 'staff')
                return 'staff'  # Default role
        
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'staff'
    
    def create_user(self, username: str, email: str, password: str, full_name: str = None, role: str = 'staff') -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new user (SQLite mode only)."""
        if self.auth_mode != 'sqlite':
            return False, None, "User creation only supported in SQLite mode"
        
        try:
            conn = local_cache._get_connection()
            
            # Check if username already exists
            cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, None, "Username already exists"
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            conn.execute(
                """INSERT INTO users (id, username, email, password_hash, full_name, is_active, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, username, email, password_hash, full_name, 1, now, now)
            )
            
            # Assign role
            role_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO user_roles (id, user_id, role, created_at) VALUES (?, ?, ?, ?)",
                (role_id, user_id, role, now)
            )
            
            conn.commit()
            
            logger.info(f"User {username} created successfully")
            return True, user_id, None
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, None, str(e)
    
    def refresh_session(self) -> bool:
        """Refresh the session token."""
        if self.auth_mode != 'supabase':
            return True  # SQLite doesn't need refresh
        
        try:
            if not self.refresh_token:
                return False
            
            client = supabase_manager.client
            response = client.auth.refresh_session(self.refresh_token)
            
            if response.session:
                self.session_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has a specific permission."""
        if not self.current_user:
            return False
        
        role = self.current_user.get('role', 'staff')
        return self._check_role_permission(role, permission)
    
    def _check_role_permission(self, role: str, permission: str) -> bool:
        """Check if role has permission."""
        # Permission matrix
        permissions = {
            'admin': ['all'],
            'doctor': ['view_clients', 'edit_clients', 'view_appointments', 'edit_appointments',
                      'view_treatment_plans', 'edit_treatment_plans', 'view_medical_records',
                      'edit_medical_records', 'create_prescriptions', 'view_reports'],
            'staff': ['view_clients', 'view_appointments', 'edit_appointments', 'view_treatment_plans',
                     'view_medical_records', 'view_reports'],
            'receptionist': ['view_clients', 'edit_clients', 'view_appointments', 'edit_appointments',
                           'create_appointments', 'view_payments', 'process_payments']
        }
        
        role_perms = permissions.get(role, [])
        return 'all' in role_perms or permission in role_perms
    
    def _get_email_from_username(self, username: str) -> Optional[str]:
        """Get email address from username (Supabase mode only)."""
        try:
            client = supabase_manager.client
            
            try:
                response = client.table('users').select('email').eq('username', username).execute()
                if response.data and response.data[0].get('email'):
                    return response.data[0].get('email')
            except Exception as e:
                logger.debug(f"Users table lookup failed: {e}")
            
            if '@' in username:
                return username
            
            logger.warning(f"Username '{username}' not found in users table.")
            return None
        
        except Exception as e:
            logger.error(f"Error getting email from username: {e}")
            return None
    
    def _get_username_from_user_id(self, user_id: str) -> Optional[str]:
        """Get username from user ID (Supabase mode only)."""
        try:
            client = supabase_manager.client
            
            try:
                response = client.table('users').select('username').eq('user_id', user_id).execute()
                if response.data:
                    return response.data[0].get('username')
            except:
                pass
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting username from user_id: {e}")
            return None


# Global instance
auth_manager = AuthManager()
