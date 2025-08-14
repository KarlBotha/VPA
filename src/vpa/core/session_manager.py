"""
Session Manager for VPA Authentication
Provides secure session management with multiple authentication methods
"""

import secrets
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .logging import get_structured_logger
from .database import ConversationDatabaseManager

logger = get_structured_logger(__name__)

@dataclass
class SessionInfo:
    """Session information structure"""
    session_id: str
    user_id: str
    username: str
    email: Optional[str]
    auth_method: str  # local, oauth2_google, oauth2_github, passwordless
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings for storage
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create from dictionary"""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'last_activity', 'expires_at']
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() >= self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

class SessionManager:
    """
    Advanced session manager for VPA authentication
    Supports multiple authentication methods and session security
    """
    
    def __init__(self, db_manager: ConversationDatabaseManager):
        self.db = db_manager
        self.logger = logger
        self.active_sessions: Dict[str, SessionInfo] = {}
        
        # Session configuration
        self.default_session_timeout = timedelta(hours=24)
        self.max_sessions_per_user = 5
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.now()
        
        # Initialize session tables
        self._initialize_session_tables()
        
        # Load active sessions from database
        self._load_active_sessions()
        
        self.logger.info("Session Manager initialized")
    
    def _initialize_session_tables(self):
        """Initialize session management database tables"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Enhanced sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    email TEXT,
                    auth_method TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_data TEXT DEFAULT '{}'
                )
            """)
            
            # Session activity log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    details TEXT DEFAULT '{}'
                )
            """)
            
            conn.commit()
            self.logger.info("Session tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session tables: {e}")
            raise
    
    def _load_active_sessions(self):
        """Load active sessions from database"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, user_id, username, email, auth_method,
                       created_at, last_activity, expires_at, is_active,
                       ip_address, user_agent
                FROM user_sessions
                WHERE is_active = 1 AND expires_at > CURRENT_TIMESTAMP
            """)
            
            for row in cursor.fetchall():
                session_id, user_id, username, email, auth_method, created_at, last_activity, expires_at, is_active, ip_address, user_agent = row
                
                session_info = SessionInfo(
                    session_id=session_id,
                    user_id=user_id,
                    username=username,
                    email=email,
                    auth_method=auth_method,
                    created_at=datetime.fromisoformat(created_at),
                    last_activity=datetime.fromisoformat(last_activity),
                    expires_at=datetime.fromisoformat(expires_at),
                    is_active=bool(is_active),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                self.active_sessions[session_id] = session_info
            
            self.logger.info(f"Loaded {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            self.logger.error(f"Failed to load active sessions: {e}")
    
    def create_session(self, user_id: str, username: str, auth_method: str, 
                      email: Optional[str] = None, session_timeout: Optional[timedelta] = None,
                      ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> SessionInfo:
        """
        Create a new user session
        
        Args:
            user_id: User identifier
            username: Username
            auth_method: Authentication method used
            email: User email (optional)
            session_timeout: Custom session timeout (optional)
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
            
        Returns:
            SessionInfo object
        """
        try:
            # Generate secure session ID
            session_id = secrets.token_urlsafe(32)
            
            # Set session timeout
            timeout = session_timeout or self.default_session_timeout
            expires_at = datetime.now() + timeout
            
            # Create session info
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                username=username,
                email=email,
                auth_method=auth_method,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Check session limits per user
            self._enforce_session_limits(user_id)
            
            # Store session in database
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_sessions 
                (session_id, user_id, username, email, auth_method, 
                 created_at, last_activity, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, username, email, auth_method,
                session_info.created_at.isoformat(),
                session_info.last_activity.isoformat(),
                session_info.expires_at.isoformat(),
                ip_address, user_agent
            ))
            
            conn.commit()
            
            # Add to active sessions
            self.active_sessions[session_id] = session_info
            
            # Log session creation
            self._log_session_activity(session_id, "session_created", ip_address, user_agent)
            
            self.logger.info("Session created successfully", extra={
                "session_id": session_id,
                "user_id": user_id,
                "username": username,
                "auth_method": auth_method
            })
            
            return session_info
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def validate_session(self, session_id: str, update_activity: bool = True) -> Optional[SessionInfo]:
        """
        Validate a session and optionally update activity
        
        Args:
            session_id: Session identifier
            update_activity: Whether to update last activity timestamp
            
        Returns:
            SessionInfo if valid, None if invalid
        """
        try:
            # Check if session exists in memory
            session_info = self.active_sessions.get(session_id)
            
            if not session_info:
                # Try to load from database
                session_info = self._load_session_from_db(session_id)
                if session_info:
                    self.active_sessions[session_id] = session_info
            
            if not session_info:
                return None
            
            # Check if session is expired
            if session_info.is_expired or not session_info.is_active:
                self._invalidate_session(session_id)
                return None
            
            # Update activity if requested
            if update_activity:
                session_info.update_activity()
                self._update_session_activity(session_id)
            
            return session_info
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {e}")
            return None
    
    def _load_session_from_db(self, session_id: str) -> Optional[SessionInfo]:
        """Load session from database"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, email, auth_method, created_at,
                       last_activity, expires_at, is_active, ip_address, user_agent
                FROM user_sessions
                WHERE session_id = ? AND is_active = 1
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, username, email, auth_method, created_at, last_activity, expires_at, is_active, ip_address, user_agent = row
            
            return SessionInfo(
                session_id=session_id,
                user_id=user_id,
                username=username,
                email=email,
                auth_method=auth_method,
                created_at=datetime.fromisoformat(created_at),
                last_activity=datetime.fromisoformat(last_activity),
                expires_at=datetime.fromisoformat(expires_at),
                is_active=bool(is_active),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load session from database: {e}")
            return None
    
    def _update_session_activity(self, session_id: str):
        """Update session activity in database"""
        try:
            session_info = self.active_sessions.get(session_id)
            if not session_info:
                return
            
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions
                SET last_activity = ?
                WHERE session_id = ?
            """, (session_info.last_activity.isoformat(), session_id))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was invalidated, False if not found
        """
        return self._invalidate_session(session_id)
    
    def _invalidate_session(self, session_id: str) -> bool:
        """Internal method to invalidate session"""
        try:
            # Remove from active sessions
            session_info = self.active_sessions.pop(session_id, None)
            
            # Update database
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions
                SET is_active = 0
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            
            # Log session invalidation
            if session_info:
                self._log_session_activity(session_id, "session_invalidated")
                self.logger.info("Session invalidated", extra={
                    "session_id": session_id,
                    "user_id": session_info.user_id
                })
            
            return session_info is not None
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate session: {e}")
            return False
    
    def invalidate_user_sessions(self, user_id: str, exclude_session: Optional[str] = None) -> int:
        """
        Invalidate all sessions for a user
        
        Args:
            user_id: User identifier
            exclude_session: Session to exclude from invalidation (optional)
            
        Returns:
            Number of sessions invalidated
        """
        try:
            # Get user sessions
            user_sessions = [
                session_id for session_id, session_info in self.active_sessions.items()
                if session_info.user_id == user_id and session_id != exclude_session
            ]
            
            # Invalidate each session
            for session_id in user_sessions:
                self._invalidate_session(session_id)
            
            self.logger.info(f"Invalidated {len(user_sessions)} sessions for user", extra={
                "user_id": user_id,
                "sessions_invalidated": len(user_sessions)
            })
            
            return len(user_sessions)
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate user sessions: {e}")
            return 0
    
    def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""
        try:
            user_sessions = [
                (session_id, session_info) for session_id, session_info in self.active_sessions.items()
                if session_info.user_id == user_id
            ]
            
            if len(user_sessions) >= self.max_sessions_per_user:
                # Sort by last activity (oldest first)
                user_sessions.sort(key=lambda x: x[1].last_activity)
                
                # Remove oldest sessions
                sessions_to_remove = len(user_sessions) - self.max_sessions_per_user + 1
                for i in range(sessions_to_remove):
                    session_id = user_sessions[i][0]
                    self._invalidate_session(session_id)
                    self.logger.info("Removed old session due to limit", extra={
                        "user_id": user_id,
                        "session_id": session_id
                    })
        
        except Exception as e:
            self.logger.error(f"Failed to enforce session limits: {e}")
    
    def _log_session_activity(self, session_id: str, activity_type: str, 
                             ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                             details: Optional[Dict[str, Any]] = None):
        """Log session activity"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO session_activity
                (session_id, activity_type, ip_address, user_agent, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id, activity_type, ip_address, user_agent,
                json.dumps(details or {})
            ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to log session activity: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            
            # Only run cleanup if enough time has passed
            if current_time - self.last_cleanup < self.cleanup_interval:
                return
            
            expired_sessions = [
                session_id for session_id, session_info in self.active_sessions.items()
                if session_info.is_expired
            ]
            
            # Remove expired sessions
            for session_id in expired_sessions:
                self._invalidate_session(session_id)
            
            # Update database to mark expired sessions as inactive
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions
                SET is_active = 0
                WHERE expires_at <= ? AND is_active = 1
            """, (current_time.isoformat(),))
            
            conn.commit()
            
            self.last_cleanup = current_time
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
    
    def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """Get all active sessions for a user"""
        try:
            user_sessions = [
                session_info for session_info in self.active_sessions.values()
                if session_info.user_id == user_id and not session_info.is_expired
            ]
            return user_sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            active_count = len(self.active_sessions)
            auth_methods = {}
            
            for session_info in self.active_sessions.values():
                method = session_info.auth_method
                auth_methods[method] = auth_methods.get(method, 0) + 1
            
            return {
                "active_sessions": active_count,
                "auth_methods": auth_methods,
                "cleanup_interval": self.cleanup_interval.total_seconds(),
                "last_cleanup": self.last_cleanup.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session stats: {e}")
            return {}
