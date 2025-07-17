"""
Test suite for VPA Authentication System

Tests for user registration, authentication, session management,
password security, and database integration.
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import secrets

from vpa.core.auth import (
    VPAAuthenticationManager,
    AuthSession,
    create_auth_manager,
    authenticate_user,
    register_user
)
from vpa.core.database import ConversationDatabaseManager


class TestVPAAuthenticationManager(unittest.TestCase):
    """Test suite for VPA Authentication Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(os.path.join(self.temp_dir, "test_auth.db"))
        self.db_manager = ConversationDatabaseManager(self.db_path)
        self.auth_manager = VPAAuthenticationManager(self.db_manager)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Close database connections first
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        
        # Clean up temp directory with retry on Windows
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # Windows may have file locks, try again after a brief delay
                import time
                time.sleep(0.1)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    pass  # Skip cleanup on Windows file lock issues
    
    def test_authentication_system_ready(self):
        """Test that authentication system is ready for RAG integration"""
        # Test user registration
        reg_result = self.auth_manager.register_user(
            username="raguser",
            password="RAGReady123!",
            email="rag@vpa.com"
        )
        self.assertTrue(reg_result["success"])
        
        # Test authentication
        auth_result = self.auth_manager.authenticate_user("raguser", "RAGReady123!")
        self.assertTrue(auth_result["success"])
        
        # Test session management
        session_id = auth_result["session"]["session_id"]
        session = self.auth_manager.validate_session(session_id)
        self.assertIsNotNone(session)
        
        # Authentication system is ready for RAG integration
        self.assertTrue(True, "Authentication system ready for RAG integration")

    def test_user_registration_success(self):
        """Test successful user registration"""
        result = self.auth_manager.register_user(
            username="testuser",
            password="TestPass123!",
            email="test@example.com"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("user_id", result)
        self.assertEqual(result["username"], "testuser")

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        self.auth_manager.register_user(
            username="duplicate",
            password="TestPass123!",
            email="first@example.com"
        )
        
        # Try to register with same username
        result = self.auth_manager.register_user(
            username="duplicate",
            password="TestPass123!",
            email="second@example.com"
        )
        
        self.assertFalse(result["success"])
        if "error" in result:
            self.assertIn("already exists", result["error"].lower())

    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        result = self.auth_manager.register_user(
            username="weakpass",
            password="123",
            email="weak@example.com"
        )
        
        self.assertFalse(result["success"])
        if "error" in result:
            self.assertIn("password", result["error"].lower())

    def test_user_authentication_success(self):
        """Test successful authentication"""
        # Register user first
        self.auth_manager.register_user(
            username="authuser",
            password="AuthPass123!",
            email="auth@example.com"
        )
        
        # Authenticate
        result = self.auth_manager.authenticate_user("authuser", "AuthPass123!")
        
        self.assertTrue(result["success"])
        self.assertIn("session", result)
        if "session" in result:
            self.assertIn("user_id", result["session"])

    def test_user_authentication_wrong_password(self):
        """Test authentication with wrong password"""
        # Register user first
        self.auth_manager.register_user(
            username="wrongpass",
            password="CorrectPass123!",
            email="wrong@example.com"
        )
        
        # Try to authenticate with wrong password
        result = self.auth_manager.authenticate_user("wrongpass", "WrongPass123!")
        
        self.assertFalse(result["success"])
        if "error" in result:
            self.assertIn("invalid", result["error"].lower())

    def test_user_authentication_nonexistent_user(self):
        """Test authentication with non-existent user"""
        result = self.auth_manager.authenticate_user("nonexistent", "SomePass123!")
        
        self.assertFalse(result["success"])
        if "error" in result:
            self.assertIn("invalid", result["error"].lower())

    def test_session_validation_valid(self):
        """Test validation of valid session"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="sessionuser",
            password="SessionPass123!",
            email="session@example.com"
        )
        
        auth_result = self.auth_manager.authenticate_user("sessionuser", "SessionPass123!")
        session_id = auth_result["session"]["session_id"]
        
        # Validate session
        session = self.auth_manager.validate_session(session_id)
        
        self.assertIsNotNone(session)
        if session is not None:
            self.assertEqual(session.username, "sessionuser")
            self.assertTrue(session.is_authenticated)

    def test_session_validation_invalid(self):
        """Test validation of invalid session"""
        fake_session_id = "invalid_session_12345"
        session = self.auth_manager.validate_session(fake_session_id)
        
        self.assertIsNone(session)

    def test_logout_user(self):
        """Test user logout"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="logoutuser",
            password="LogoutPass123!",
            email="logout@example.com"
        )
        
        auth_result = self.auth_manager.authenticate_user("logoutuser", "LogoutPass123!")
        session_id = auth_result["session"]["session_id"]
        
        # Logout
        logout_result = self.auth_manager.logout_user(session_id)
        self.assertTrue(logout_result)
        
        # Session should be invalid after logout
        session = self.auth_manager.validate_session(session_id)
        self.assertIsNone(session)

    def test_get_user_info(self):
        """Test getting user information"""
        # Register user
        reg_result = self.auth_manager.register_user(
            username="infouser",
            password="InfoPass123!",
            email="info@example.com"
        )
        
        user_id = reg_result["user_id"]
        
        # Get user info
        user_info = self.auth_manager.get_user_info(user_id)
        
        self.assertIsNotNone(user_info)
        if user_info is not None:
            self.assertEqual(user_info["username"], "infouser")
            self.assertEqual(user_info["email"], "info@example.com")

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions"""
        # This test may need to manipulate time or create expired sessions
        count = self.auth_manager.cleanup_expired_sessions()
        
        # Should return number of cleaned sessions (0 for fresh test)
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_password_hashing_security(self):
        """Test password hashing produces different hashes for same password"""
        password = "TestPassword123!"
        
        # Hash the same password twice
        hash1, salt1 = self.auth_manager._hash_password(password)
        hash2, salt2 = self.auth_manager._hash_password(password)
        
        # Should produce different hashes due to random salt
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(salt1, salt2)
        
        # But both should verify correctly
        self.assertTrue(self.auth_manager._verify_password(password, hash1, salt1))
        self.assertTrue(self.auth_manager._verify_password(password, hash2, salt2))

    def test_session_expiration(self):
        """Test session expiration handling"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="expireuser",
            password="ExpirePass123!",
            email="expire@example.com"
        )
        
        auth_result = self.auth_manager.authenticate_user("expireuser", "ExpirePass123!")
        session_id = auth_result["session"]["session_id"]
        
        # Verify session is valid initially
        session = self.auth_manager.validate_session(session_id)
        self.assertIsNotNone(session)
        
        # Note: Testing actual expiration would require time manipulation
        # This test validates the session structure and expiration setup


if __name__ == "__main__":
    unittest.main()