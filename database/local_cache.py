"""Local SQLite cache with transactional operations."""

import sqlite3
import json
import logging
import uuid
import bcrypt
from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime
from contextlib import contextmanager
from config.settings import settings

logger = logging.getLogger(__name__)


class LocalCache:
    """Manages local SQLite cache with WAL mode and transactions."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.local_cache_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with WAL mode."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
    
    def _initialize_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        
        # Create core tables
        tables = [
            """CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT,
                date_of_birth TEXT,
                address TEXT,
                medical_history TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                created_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS doctors (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                specialization TEXT,
                license_number TEXT,
                hire_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS staff (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                position TEXT,
                hire_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                room_number TEXT,
                room_type TEXT,
                capacity INTEGER,
                is_available INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,
                room_id TEXT,
                equipment_name TEXT,
                equipment_type TEXT,
                serial_number TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                doctor_id TEXT,
                room_id TEXT,
                reservation_date TEXT,
                start_time_utc TEXT,
                end_time_utc TEXT,
                status TEXT,
                notes TEXT,
                locked_until TEXT,
                created_by TEXT,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                reservation_id TEXT,
                client_id TEXT,
                amount REAL,
                payment_method TEXT,
                payment_date_utc TEXT,
                status TEXT,
                notes TEXT,
                processed_by TEXT,
                created_at TEXT,
                updated_at TEXT,
                last_modified_by TEXT,
                pending_sync INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'synced',
                original_data TEXT,
                last_synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS sync_queue (
                id TEXT PRIMARY KEY,
                table_name TEXT,
                record_id TEXT,
                operation TEXT,
                local_data TEXT,
                remote_data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                synced_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                last_login_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS user_roles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'doctor', 'staff', 'receptionist')),
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )"""
        ]
        
        with self.transaction() as conn:
            for table_sql in tables:
                conn.execute(table_sql)
        
        # Create default admin user if no users exist
        self._create_default_admin()
        
        logger.info("Local cache database initialized")
    
    def _create_default_admin(self):
        """Create default admin user if no users exist."""
        try:
            conn = self._get_connection()
            
            # Check if any users exist
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Create default admin user
                admin_id = str(uuid.uuid4())
                admin_username = "admin"
                admin_password = "admin"  # Default password - CHANGE IN PRODUCTION!
                admin_email = "admin@clinic.local"
                
                # Hash password
                password_hash = bcrypt.hashpw(
                    admin_password.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                now = datetime.utcnow().isoformat()
                
                # Insert admin user
                conn.execute(
                    """INSERT INTO users (id, username, email, password_hash, full_name, is_active, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (admin_id, admin_username, admin_email, password_hash, "Administrator", 1, now, now)
                )
                
                # Assign admin role
                role_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO user_roles (id, user_id, role, created_at) VALUES (?, ?, ?, ?)",
                    (role_id, admin_id, 'admin', now)
                )
                
                conn.commit()
                logger.info("Default admin user created: username='admin', password='admin'")
                print("\n" + "=" * 60)
                print("DEFAULT ADMIN USER CREATED")
                print("=" * 60)
                print("Username: admin")
                print("Password: admin")
                print("⚠️  WARNING: Change this password in production!")
                print("=" * 60 + "\n")
        
        except Exception as e:
            logger.error(f"Error creating default admin user: {e}")
            # Don't raise - allow app to continue even if admin creation fails
    
    def insert(self, table: str, data: Dict[str, Any], mark_pending: bool = True) -> str:
        """Insert a record into local cache."""
        record_id = data.get('id', str(uuid.uuid4()))
        now = datetime.utcnow().isoformat()
        
        data['id'] = record_id
        data['created_at'] = data.get('created_at', now)
        data['updated_at'] = data.get('updated_at', now)
        
        if mark_pending:
            data['pending_sync'] = 1
            data['sync_status'] = 'pending'
            data['original_data'] = json.dumps(data)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.transaction() as conn:
            conn.execute(sql, values)
        
        return record_id
    
    def update(self, table: str, record_id: str, data: Dict[str, Any], mark_pending: bool = True) -> bool:
        """Update a record in local cache."""
        # Get original data before update
        original = self.get(table, record_id)
        
        data['updated_at'] = datetime.utcnow().isoformat()
        
        if mark_pending and original:
            data['original_data'] = json.dumps(original)
            data['pending_sync'] = 1
            data['sync_status'] = 'pending'
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [record_id]
        
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        with self.transaction() as conn:
            cursor = conn.execute(sql, values)
            return cursor.rowcount > 0
    
    def delete(self, table: str, record_id: str, mark_pending: bool = True) -> bool:
        """Delete a record from local cache."""
        if mark_pending:
            # Add to sync queue for deletion
            self._add_to_sync_queue(table, record_id, 'delete', None, None)
        
        sql = f"DELETE FROM {table} WHERE id = ?"
        
        with self.transaction() as conn:
            cursor = conn.execute(sql, (record_id,))
            return cursor.rowcount > 0
    
    def get(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record from local cache."""
        sql = f"SELECT * FROM {table} WHERE id = ?"
        
        conn = self._get_connection()
        cursor = conn.execute(sql, (record_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def query(self, table: str, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query records from local cache."""
        sql = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        if limit:
            sql += f" LIMIT {limit}"
        
        conn = self._get_connection()
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def _add_to_sync_queue(self, table: str, record_id: str, operation: str, local_data: Optional[Dict], remote_data: Optional[Dict]):
        """Add operation to sync queue."""
        queue_data = {
            'id': str(uuid.uuid4()),
            'table_name': table,
            'record_id': record_id,
            'operation': operation,
            'local_data': json.dumps(local_data) if local_data else None,
            'remote_data': json.dumps(remote_data) if remote_data else None,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.insert('sync_queue', queue_data, mark_pending=False)
    
    def get_pending_sync(self, table: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending sync operations."""
        filters = {'status': 'pending'}
        if table:
            filters['table_name'] = table
        
        return self.query('sync_queue', filters)
    
    def mark_synced(self, table: str, record_id: str):
        """Mark a record as synced."""
        data = {
            'pending_sync': 0,
            'sync_status': 'synced',
            'last_synced_at': datetime.utcnow().isoformat()
        }
        self.update(table, record_id, data, mark_pending=False)
        
        # Update sync queue
        sql = "UPDATE sync_queue SET status = 'synced', synced_at = ? WHERE table_name = ? AND record_id = ?"
        conn = self._get_connection()
        conn.execute(sql, (datetime.utcnow().isoformat(), table, record_id))
        conn.commit()


# Global instance
local_cache = LocalCache()

