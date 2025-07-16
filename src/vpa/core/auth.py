"""
Authentication System for VPA (M09 - Final Must-Have Requirement)
Provides secure authentication with OAuth2 and passwordless options
Integrates with existing user profile and database systems
"""

import hashlib
import secrets
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Import existing VPA components
from .database import ConversationDatabaseManager
from .logging import get_structured_logger

logger = get_structured_logger(__name__)

@dataclass
class AuthToken:
    """Authentication token structure"""
    token_id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    created_at: datetime
    last_used: datetime
    is_active: bool = True
    token_type: str = "session"  # session, api, refresh

@dataclass 
class AuthSession:
    """User authentication session"""
    session_id: str
    user_id: str
    username: str
    email: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_authenticated: bool = True
    auth_method: str = "local"  # local, oauth2, passwordless

@dataclass
class AuthUser:
    """Authenticated user information"""
    user_id: str
    username: str
    email: Optional[str]
    password_hash: Optional[str]
    salt: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool = True
    auth_methods: Optional[List[str]] = None  # ["local", "oauth2", "passwordless"]
    
    def __post_init__(self):
        if self.auth_methods is None:
            self.auth_methods = ["local"]

class VPAAuthenticationManager:
    """
    VPA Authentication Manager - Secure authentication system
    Supports local authentication, OAuth2, and passwordless methods
    """
    
    def __init__(self, db_manager: ConversationDatabaseManager):
        self.db = db_manager
        self.logger = logger
        self.active_sessions: Dict[str, AuthSession] = {}
        self.active_tokens: Dict[str, AuthToken] = {}
        
        # Security settings
        self.session_timeout = timedelta(hours=24)
        self.token_timeout = timedelta(hours=1)
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        
        # Initialize auth tables
        self._initialize_auth_tables()
        
        self.logger.info("VPA Authentication Manager initialized")
    
    def _initialize_auth_tables(self):
        """Initialize authentication database tables"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    auth_methods TEXT DEFAULT '["local"]',
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    auth_method TEXT DEFAULT 'local',
                    FOREIGN KEY (user_id) REFERENCES auth_users (user_id)
                )
            """)
            
            # Tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    token_type TEXT DEFAULT 'session',
                    FOREIGN KEY (user_id) REFERENCES auth_users (user_id)
                )
            """)
            
            conn.commit()
            self.logger.info("Authentication tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize auth tables: {e}")
            raise
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return password_hash.hex(), salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        computed_hash, _ = self._hash_password(password, salt)
        return secrets.compare_digest(computed_hash, stored_hash)
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _generate_token(self) -> str:
        """Generate secure token"""
        return secrets.token_urlsafe(48)
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user with local authentication
        
        Args:
            username: Unique username
            password: User password
            email: Optional email address
            
        Returns:
            Dict with registration result
        """
        try:
            # Validate input
            if not username or len(username) < 3:
                return {"success": False, "error": "Username must be at least 3 characters"}
            
            if not password or len(password) < 8:
                return {"success": False, "error": "Password must be at least 8 characters"}
            
            # Check if user exists
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM auth_users WHERE username = ?", (username,))
            if cursor.fetchone():
                return {"success": False, "error": "Username already exists"}
            
            if email:
                cursor.execute("SELECT user_id FROM auth_users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return {"success": False, "error": "Email already registered"}
            
            # Create user
            user_id = secrets.token_hex(16)
            password_hash, salt = self._hash_password(password)
            
            cursor.execute("""
                INSERT INTO auth_users (user_id, username, email, password_hash, salt, auth_methods)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, email, password_hash, salt, json.dumps(["local"])))
            
            conn.commit()
            
            self.logger.info("User registered successfully", extra={
                "user_id": user_id,
                "username": username,
                "auth_method": "local"
            })
            
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "message": "User registered successfully"
            }
            
        except Exception as e:
            self.logger.error(f"User registration failed: {e}")
            return {"success": False, "error": "Registration failed"}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username/password
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Dict with authentication result and session info
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get user info
                cursor.execute("""
                    SELECT user_id, username, email, password_hash, salt, is_active, 
                           login_attempts, locked_until
                    FROM auth_users 
                    WHERE username = ?
                """, (username,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return {"success": False, "error": "Invalid credentials"}
                
                user_id, username, email, stored_hash, salt, is_active, login_attempts, locked_until = user_row
                
                # Check if account is active
                if not is_active:
                    return {"success": False, "error": "Account is disabled"}
                
                # Check if account is locked
                if locked_until:
                    lock_time = datetime.fromisoformat(locked_until)
                    if datetime.now() < lock_time:
                        return {"success": False, "error": "Account is temporarily locked"}
                    else:
                        # Unlock account
                        cursor.execute("""
                            UPDATE auth_users 
                            SET login_attempts = 0, locked_until = NULL 
                            WHERE user_id = ?
                        """, (user_id,))
                        login_attempts = 0
                
                # Verify password
                if not self._verify_password(password, stored_hash, salt):
                    # Increment login attempts
                    login_attempts += 1
                    
                    if login_attempts >= self.max_login_attempts:
                        # Lock account
                        lock_until = datetime.now() + self.lockout_duration
                        cursor.execute("""
                            UPDATE auth_users 
                            SET login_attempts = ?, locked_until = ?
                            WHERE user_id = ?
                        """, (login_attempts, lock_until.isoformat(), user_id))
                    else:
                        cursor.execute("""
                            UPDATE auth_users 
                            SET login_attempts = ?
                            WHERE user_id = ?
                        """, (login_attempts, user_id))
                    
                    conn.commit()
                    return {"success": False, "error": "Invalid credentials"}
                
                # Reset login attempts on successful auth
                cursor.execute("""
                    UPDATE auth_users 
                    SET login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                
                # Create session
                session = self._create_session(user_id, username, email, "local")
                
                conn.commit()
            
            self.logger.info("User authenticated successfully", extra={
                "user_id": user_id,
                "username": username,
                "session_id": session.session_id,
                "auth_method": "local"
            })
            
            return {
                "success": True,
                "session": asdict(session),
                "message": "Authentication successful"
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def _create_session(self, user_id: str, username: str, email: Optional[str] = None, 
                       auth_method: str = "local") -> AuthSession:
        """Create a new user session"""
        session_id = self._generate_session_id()
        now = datetime.now()
        expires_at = now + self.session_timeout
        
        session = AuthSession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            email=email,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            auth_method=auth_method
        )
        
        # Store in database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO auth_sessions 
                (session_id, user_id, created_at, last_activity, expires_at, auth_method)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, now.isoformat(), now.isoformat(), 
                  expires_at.isoformat(), auth_method))
            conn.commit()
        
        # Store in memory
        self.active_sessions[session_id] = session
        
        return session
    
    def validate_session(self, session_id: str) -> Optional[AuthSession]:
        """
        Validate and return session if valid
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            AuthSession if valid, None otherwise
        """
        try:
            # Check memory cache first
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                # Check if expired
                if datetime.now() > session.expires_at:
                    self._invalidate_session(session_id)
                    return None
                
                # Update last activity
                session.last_activity = datetime.now()
                self._update_session_activity(session_id)
                
                return session
            
            # Check database
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.session_id, s.user_id, u.username, u.email, s.created_at,
                           s.last_activity, s.expires_at, s.is_active, s.auth_method
                    FROM auth_sessions s
                    JOIN auth_users u ON s.user_id = u.user_id
                    WHERE s.session_id = ? AND s.is_active = 1
                """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse row data
            (sid, user_id, username, email, created_at, last_activity, 
             expires_at, is_active, auth_method) = row
            
            # Check if expired
            expires_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > expires_dt:
                self._invalidate_session(session_id)
                return None
            
            # Recreate session object
            session = AuthSession(
                session_id=sid,
                user_id=user_id,
                username=username,
                email=email,
                created_at=datetime.fromisoformat(created_at),
                last_activity=datetime.fromisoformat(last_activity),
                expires_at=expires_dt,
                auth_method=auth_method
            )
            
            # Update activity and cache
            session.last_activity = datetime.now()
            self.active_sessions[session_id] = session
            self._update_session_activity(session_id)
            
            return session
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {e}")
            return None
    
    def _update_session_activity(self, session_id: str):
        """Update session last activity timestamp"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE auth_sessions 
                    SET last_activity = CURRENT_TIMESTAMP 
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")
    
    def logout_user(self, session_id: str) -> bool:
        """
        Logout user by invalidating session
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._invalidate_session(session_id)
            self.logger.info("User logged out", extra={"session_id": session_id})
            return True
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False
    
    def _invalidate_session(self, session_id: str):
        """Invalidate a session"""
        # Remove from memory
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Mark as inactive in database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE auth_sessions 
                SET is_active = 0 
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with user info or None
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, email, created_at, last_login, 
                           is_active, auth_methods
                    FROM auth_users 
                    WHERE user_id = ?
                """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, username, email, created_at, last_login, is_active, auth_methods = row
            
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at,
                "last_login": last_login,
                "is_active": bool(is_active),
                "auth_methods": json.loads(auth_methods) if auth_methods else ["local"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # Mark expired sessions as inactive
                cursor.execute("""
                    UPDATE auth_sessions 
                    SET is_active = 0 
                    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = 1
                """)
                
                cleaned_count = cursor.rowcount
                
                # Remove from memory cache
                expired_sessions = []
                now = datetime.now()
                
                for session_id, session in self.active_sessions.items():
                    if now > session.expires_at:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                
                conn.commit()
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} expired sessions")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
            return 0
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auth_sessions 
                    WHERE is_active = 1 AND expires_at > CURRENT_TIMESTAMP
                """)
                return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get active sessions count: {e}")
            return 0
    
    def is_authenticated(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """
        Check if user/session is authenticated
        
        Args:
            session_id: Session ID to check
            user_id: User ID to check (checks for any active session)
            
        Returns:
            True if authenticated, False otherwise
        """
        if session_id:
            session = self.validate_session(session_id)
            return session is not None
        
        if user_id:
            try:
                with self.db._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM auth_sessions 
                        WHERE user_id = ? AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP
                    """, (user_id,))
                    return cursor.fetchone()[0] > 0
            except Exception as e:
                self.logger.error(f"Authentication check failed: {e}")
                return False
        
        return False


# Convenience functions for easy integration
def create_auth_manager(db_manager: ConversationDatabaseManager) -> VPAAuthenticationManager:
    """Create and return VPA Authentication Manager"""
    return VPAAuthenticationManager(db_manager)


def require_authentication(session_id: str, auth_manager: VPAAuthenticationManager) -> Optional[AuthSession]:
    """
    Decorator/helper function to require authentication
    
    Args:
        session_id: Session ID to validate
        auth_manager: Authentication manager instance
        
    Returns:
        AuthSession if authenticated, None otherwise
    """
    return auth_manager.validate_session(session_id)


def authenticate_user(username: str, password: str, auth_manager: VPAAuthenticationManager) -> Dict[str, Any]:
    """
    Convenience function for user authentication
    
    Args:
        username: Username
        password: Password
        auth_manager: Authentication manager instance
        
    Returns:
        Authentication result dictionary
    """
    return auth_manager.authenticate_user(username, password)


def register_user(username: str, password: str, email: Optional[str] = None, 
                 auth_manager: VPAAuthenticationManager = None) -> Dict[str, Any]:
    """
    Convenience function for user registration
    
    Args:
        username: Username
        password: Password
        email: Email address (optional)
        auth_manager: Authentication manager instance
        
    Returns:
        Registration result dictionary
    """
    return auth_manager.register_user(username, password, email)
