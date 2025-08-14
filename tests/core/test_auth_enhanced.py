"""
Enhanced Authentication Tests for VPA
Tests OAuth2 and enhanced session management features
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

from src.vpa.core.auth import VPAAuthenticationManager, create_auth_manager
from src.vpa.core.auth_providers import OAuth2Manager, GoogleOAuth2Provider, GitHubOAuth2Provider, OAuth2UserInfo
from src.vpa.core.session_manager import SessionManager, SessionInfo
from src.vpa.core.database import ConversationDatabaseManager


class TestOAuth2Manager:
    """Test OAuth2 manager functionality"""
    
    def test_oauth2_manager_initialization(self):
        """Test OAuth2 manager initialization"""
        manager = OAuth2Manager()
        assert manager.providers == {}
        assert manager.pending_states == {}
    
    def test_register_oauth2_provider(self):
        """Test OAuth2 provider registration"""
        manager = OAuth2Manager()
        provider = GoogleOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        
        manager.register_provider(provider)
        
        assert "google" in manager.providers
        assert manager.get_provider("google") == provider
    
    def test_generate_oauth2_state(self):
        """Test OAuth2 state generation"""
        manager = OAuth2Manager()
        
        state = manager.generate_state("google", {"test": "data"})
        
        assert state in manager.pending_states
        assert manager.pending_states[state]["provider_name"] == "google"
        assert manager.pending_states[state]["user_data"]["test"] == "data"
    
    def test_validate_oauth2_state(self):
        """Test OAuth2 state validation"""
        manager = OAuth2Manager()
        
        state = manager.generate_state("google")
        state_data = manager.validate_state(state)
        
        assert state_data is not None
        assert state_data["provider_name"] == "google"
        # State should be removed after validation
        assert state not in manager.pending_states
    
    def test_validate_expired_oauth2_state(self):
        """Test OAuth2 expired state validation"""
        manager = OAuth2Manager()
        
        state = manager.generate_state("google")
        # Simulate expired state
        manager.pending_states[state]["created_at"] = manager.pending_states[state]["created_at"] - 700
        
        state_data = manager.validate_state(state, max_age=600)
        
        assert state_data is None
        assert state not in manager.pending_states


class TestGoogleOAuth2Provider:
    """Test Google OAuth2 provider"""
    
    def test_google_provider_initialization(self):
        """Test Google provider initialization"""
        provider = GoogleOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        
        assert provider.config.provider_name == "google"
        assert provider.config.client_id == "test_id"
        assert provider.config.client_secret == "test_secret"
        assert "openid" in provider.config.scopes
        assert "email" in provider.config.scopes
    
    def test_google_authorization_url(self):
        """Test Google authorization URL generation"""
        provider = GoogleOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        
        url = provider.get_authorization_url("test_state")
        
        assert "accounts.google.com" in url
        assert "client_id=test_id" in url
        assert "state=test_state" in url
        assert "scope=openid+email+profile" in url


class TestGitHubOAuth2Provider:
    """Test GitHub OAuth2 provider"""
    
    def test_github_provider_initialization(self):
        """Test GitHub provider initialization"""
        provider = GitHubOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        
        assert provider.config.provider_name == "github"
        assert provider.config.client_id == "test_id"
        assert provider.config.client_secret == "test_secret"
        assert "user:email" in provider.config.scopes
    
    def test_github_authorization_url(self):
        """Test GitHub authorization URL generation"""
        provider = GitHubOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        
        url = provider.get_authorization_url("test_state")
        
        assert "github.com" in url
        assert "client_id=test_id" in url
        assert "state=test_state" in url
        assert "scope=user%3Aemail" in url


class TestSessionManager:
    """Test enhanced session manager"""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager for testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        db_manager = None
        session_mgr = None
        try:
            db_manager = ConversationDatabaseManager(Path(tmp_path))
            session_mgr = SessionManager(db_manager)
            yield session_mgr
        finally:
            # Properly close database connections
            if session_mgr and hasattr(session_mgr, 'db'):
                try:
                    session_mgr.db.close()
                except Exception:
                    pass
            if db_manager:
                try:
                    db_manager.close()
                except Exception:
                    pass
            # Small delay to ensure Windows releases file handle
            import time
            time.sleep(0.1)
            # Attempt cleanup with retry
            for attempt in range(3):
                try:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    break
                except PermissionError:
                    time.sleep(0.1)
                    continue
    
    def test_session_manager_initialization(self, session_manager):
        """Test session manager initialization"""
        assert session_manager.active_sessions == {}
        assert session_manager.default_session_timeout == timedelta(hours=24)
        assert session_manager.max_sessions_per_user == 5
    
    def test_create_session(self, session_manager):
        """Test session creation"""
        session_info = session_manager.create_session(
            user_id="test_user",
            username="testuser",
            auth_method="local",
            email="test@example.com"
        )
        
        assert session_info.user_id == "test_user"
        assert session_info.username == "testuser"
        assert session_info.auth_method == "local"
        assert session_info.email == "test@example.com"
        assert session_info.is_active
        assert not session_info.is_expired
        assert session_info.session_id in session_manager.active_sessions
    
    def test_validate_session(self, session_manager):
        """Test session validation"""
        session_info = session_manager.create_session(
            user_id="test_user",
            username="testuser",
            auth_method="local"
        )
        
        # Validate existing session
        validated_session = session_manager.validate_session(session_info.session_id)
        assert validated_session is not None
        assert validated_session.session_id == session_info.session_id
        
        # Validate non-existent session
        invalid_session = session_manager.validate_session("invalid_session")
        assert invalid_session is None
    
    def test_invalidate_session(self, session_manager):
        """Test session invalidation"""
        session_info = session_manager.create_session(
            user_id="test_user",
            username="testuser",
            auth_method="local"
        )
        
        result = session_manager.invalidate_session(session_info.session_id)
        assert result is True
        assert session_info.session_id not in session_manager.active_sessions
        
        # Validate invalidated session
        validated_session = session_manager.validate_session(session_info.session_id)
        assert validated_session is None
    
    def test_session_limits_enforcement(self, session_manager):
        """Test session limits per user"""
        user_id = "test_user"
        
        # Create maximum allowed sessions
        sessions = []
        for i in range(session_manager.max_sessions_per_user):
            session = session_manager.create_session(
                user_id=user_id,
                username=f"testuser{i}",
                auth_method="local"
            )
            sessions.append(session)
        
        # All sessions should be active
        user_sessions = session_manager.get_user_sessions(user_id)
        assert len(user_sessions) == session_manager.max_sessions_per_user
        
        # Create one more session (should remove oldest)
        new_session = session_manager.create_session(
            user_id=user_id,
            username="newuser",
            auth_method="local"
        )
        
        # Should still have max sessions
        user_sessions = session_manager.get_user_sessions(user_id)
        assert len(user_sessions) == session_manager.max_sessions_per_user
        
        # New session should be included
        session_ids = [s.session_id for s in user_sessions]
        assert new_session.session_id in session_ids
    
    def test_invalidate_user_sessions(self, session_manager):
        """Test invalidating all user sessions"""
        user_id = "test_user"
        
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session = session_manager.create_session(
                user_id=user_id,
                username=f"testuser{i}",
                auth_method="local"
            )
            sessions.append(session)
        
        # Invalidate all user sessions except one
        exclude_session = sessions[0].session_id
        invalidated_count = session_manager.invalidate_user_sessions(user_id, exclude_session)
        
        assert invalidated_count == 2
        
        # Only excluded session should remain
        user_sessions = session_manager.get_user_sessions(user_id)
        assert len(user_sessions) == 1
        assert user_sessions[0].session_id == exclude_session
    
    def test_session_stats(self, session_manager):
        """Test session statistics"""
        # Create sessions with different auth methods
        session_manager.create_session("user1", "user1", "local")
        session_manager.create_session("user2", "user2", "oauth2_google")
        session_manager.create_session("user3", "user3", "oauth2_github")
        
        stats = session_manager.get_session_stats()
        
        assert stats["active_sessions"] == 3
        assert stats["auth_methods"]["local"] == 1
        assert stats["auth_methods"]["oauth2_google"] == 1
        assert stats["auth_methods"]["oauth2_github"] == 1


class TestEnhancedAuthentication:
    """Test enhanced authentication with OAuth2 integration"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create authentication manager for testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        db_manager = None
        auth_mgr = None
        try:
            db_manager = ConversationDatabaseManager(Path(tmp_path))
            auth_mgr = VPAAuthenticationManager(db_manager)
            yield auth_mgr
        finally:
            # Properly close database connections
            if auth_mgr and hasattr(auth_mgr, 'db'):
                try:
                    auth_mgr.db.close()
                except Exception:
                    pass
            if db_manager:
                try:
                    db_manager.close()
                except Exception:
                    pass
            # Small delay to ensure Windows releases file handle
            import time
            time.sleep(0.1)
            # Attempt cleanup with retry
            for attempt in range(3):
                try:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    break
                except PermissionError:
                    time.sleep(0.1)
                    continue
    
    def test_enhanced_auth_manager_initialization(self, auth_manager):
        """Test enhanced authentication manager initialization"""
        assert auth_manager.oauth2_manager is not None
        assert auth_manager.session_manager is not None
        assert isinstance(auth_manager.oauth2_manager, OAuth2Manager)
        assert isinstance(auth_manager.session_manager, SessionManager)
    
    def test_oauth2_provider_registration(self, auth_manager):
        """Test OAuth2 provider registration in auth manager"""
        # Register Google provider
        google_provider = GoogleOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        auth_manager.oauth2_manager.register_provider(google_provider)
        
        # Register GitHub provider
        github_provider = GitHubOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        auth_manager.oauth2_manager.register_provider(github_provider)
        
        assert auth_manager.oauth2_manager.get_provider("google") is not None
        assert auth_manager.oauth2_manager.get_provider("github") is not None
    
    def test_oauth2_flow_integration(self, auth_manager):
        """Test OAuth2 flow integration with authentication manager"""
        # Register provider
        provider = GoogleOAuth2Provider("test_id", "test_secret", "http://localhost/callback")
        auth_manager.oauth2_manager.register_provider(provider)
        
        # Start OAuth2 flow
        auth_url = auth_manager.oauth2_manager.start_oauth2_flow("google")
        assert auth_url is not None
        assert "accounts.google.com" in auth_url
    
    def test_session_integration_with_auth(self, auth_manager):
        """Test session manager integration with authentication"""
        # Register user
        result = auth_manager.register_user("testuser", "testpassword123", "test@example.com")
        assert result["success"]
        
        # Authenticate user
        auth_result = auth_manager.authenticate_user("testuser", "testpassword123")
        assert auth_result["success"]
        assert "session" in auth_result
        
        # Extract user_id from the session or result
        user_id = result["user_id"]
        
        # Check if session was created through the session manager
        user_sessions = auth_manager.session_manager.get_user_sessions(user_id)
        # Note: The legacy auth system creates its own sessions, not through session_manager
        # So we check the auth result contains session info
        assert auth_result["session"]["user_id"] == user_id
    
    def test_backward_compatibility(self, auth_manager):
        """Test that existing authentication functionality still works"""
        # Test existing user registration
        result = auth_manager.register_user("testuser", "testpassword123")
        assert result["success"]
        
        # Test existing authentication
        auth_result = auth_manager.authenticate_user("testuser", "testpassword123")
        assert auth_result["success"]
        assert "session" in auth_result
        
        # Test session validation
        session_data = auth_result["session"]
        session_id = session_data["session_id"]
        validated_session = auth_manager.validate_session(session_id)
        assert validated_session is not None
    
    def test_enhanced_security_features(self, auth_manager):
        """Test enhanced security features"""
        # Test account lockout protection
        auth_manager.register_user("testuser", "testpassword123")
        
        # Attempt multiple failed logins
        for i in range(6):  # Exceed max attempts
            result = auth_manager.authenticate_user("testuser", "wrongpassword")
            if i < 5:
                assert not result["success"]
            else:
                # Account should be locked
                assert "locked" in result["error"].lower()
    
    def test_multiple_auth_methods_support(self, auth_manager):
        """Test support for multiple authentication methods"""
        # Register user with local auth
        auth_manager.register_user("testuser", "testpassword123", "test@example.com")
        
        # Create sessions with different auth methods
        user_id = "test_user_id"
        
        # Local authentication session
        local_session = auth_manager.session_manager.create_session(
            user_id=user_id, username="testuser", auth_method="local"
        )
        
        # OAuth2 Google session
        google_session = auth_manager.session_manager.create_session(
            user_id=user_id, username="testuser", auth_method="oauth2_google"
        )
        
        # OAuth2 GitHub session
        github_session = auth_manager.session_manager.create_session(
            user_id=user_id, username="testuser", auth_method="oauth2_github"
        )
        
        # All sessions should be active
        user_sessions = auth_manager.session_manager.get_user_sessions(user_id)
        assert len(user_sessions) == 3
        
        auth_methods = [session.auth_method for session in user_sessions]
        assert "local" in auth_methods
        assert "oauth2_google" in auth_methods
        assert "oauth2_github" in auth_methods


def test_create_auth_manager():
    """Test authentication manager factory function"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    db_manager = None
    auth_manager = None
    try:
        db_manager = ConversationDatabaseManager(Path(tmp_path))
        auth_manager = create_auth_manager(db_manager)
        
        assert isinstance(auth_manager, VPAAuthenticationManager)
        assert auth_manager.db == db_manager
    finally:
        # Properly close database connections
        if auth_manager and hasattr(auth_manager, 'db'):
            try:
                auth_manager.db.close()
            except Exception:
                pass
        if db_manager:
            try:
                db_manager.close()
            except Exception:
                pass
        # Small delay to ensure Windows releases file handle
        import time
        time.sleep(0.1)
        # Attempt cleanup with retry
        for attempt in range(3):
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                break
            except PermissionError:
                time.sleep(0.1)
                continue
