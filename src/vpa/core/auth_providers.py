"""
OAuth2 Authentication Providers for VPA
Extends existing authentication system with OAuth2 capabilities
"""

import json
import urllib.parse
import urllib.request
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .logging import get_structured_logger

logger = get_structured_logger(__name__)

@dataclass
class OAuth2Config:
    """OAuth2 provider configuration"""
    provider_name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]
    redirect_uri: str

@dataclass
class OAuth2Token:
    """OAuth2 access token information"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.created_at:
            return True
        expiry_time = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.now() >= expiry_time

@dataclass
class OAuth2UserInfo:
    """OAuth2 user information from provider"""
    provider_id: str
    email: str
    name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_name: str = ""

class OAuth2Provider(ABC):
    """Abstract base class for OAuth2 providers"""
    
    def __init__(self, config: OAuth2Config):
        self.config = config
        self.logger = logger
    
    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Generate authorization URL for user redirect"""
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code: str, state: str) -> OAuth2Token:
        """Exchange authorization code for access token"""
        pass
    
    @abstractmethod
    def get_user_info(self, token: OAuth2Token) -> OAuth2UserInfo:
        """Get user information using access token"""
        pass
    
    def refresh_token(self, refresh_token: str) -> OAuth2Token:
        """Refresh an expired access token"""
        raise NotImplementedError("Token refresh not implemented for this provider")

class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 provider implementation"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        config = OAuth2Config(
            provider_name="google",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            scopes=["openid", "email", "profile"],
            redirect_uri=redirect_uri
        )
        super().__init__(config)
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth2 authorization URL"""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        url = f"{self.config.authorization_url}?{urllib.parse.urlencode(params)}"
        self.logger.info("Generated Google OAuth2 authorization URL", extra={
            "provider": "google",
            "state": state
        })
        return url
    
    def exchange_code_for_token(self, code: str, state: str) -> OAuth2Token:
        """Exchange Google authorization code for access token"""
        try:
            data = {
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.config.redirect_uri
            }
            
            request_data = urllib.parse.urlencode(data).encode('utf-8')
            request = urllib.request.Request(
                self.config.token_url,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            with urllib.request.urlopen(request) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            
            token = OAuth2Token(
                access_token=response_data["access_token"],
                token_type=response_data.get("token_type", "Bearer"),
                expires_in=response_data.get("expires_in", 3600),
                refresh_token=response_data.get("refresh_token"),
                scope=response_data.get("scope")
            )
            
            self.logger.info("Successfully exchanged Google OAuth2 code for token", extra={
                "provider": "google",
                "state": state
            })
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to exchange Google OAuth2 code: {e}", extra={
                "provider": "google",
                "state": state,
                "error": str(e)
            })
            raise
    
    def get_user_info(self, token: OAuth2Token) -> OAuth2UserInfo:
        """Get Google user information using access token"""
        try:
            request = urllib.request.Request(
                self.config.user_info_url,
                headers={"Authorization": f"{token.token_type} {token.access_token}"}
            )
            
            with urllib.request.urlopen(request) as response:
                user_data = json.loads(response.read().decode('utf-8'))
            
            user_info = OAuth2UserInfo(
                provider_id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                username=user_data.get("email"),  # Use email as username for Google
                avatar_url=user_data.get("picture"),
                provider_name="google"
            )
            
            self.logger.info("Retrieved Google user information", extra={
                "provider": "google",
                "user_id": user_info.provider_id,
                "email": user_info.email
            })
            
            return user_info
            
        except Exception as e:
            self.logger.error(f"Failed to get Google user info: {e}")
            raise

class GitHubOAuth2Provider(OAuth2Provider):
    """GitHub OAuth2 provider implementation"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        config = OAuth2Config(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user",
            scopes=["user:email"],
            redirect_uri=redirect_uri
        )
        super().__init__(config)
    
    def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth2 authorization URL"""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
            "allow_signup": "true"
        }
        
        url = f"{self.config.authorization_url}?{urllib.parse.urlencode(params)}"
        self.logger.info("Generated GitHub OAuth2 authorization URL", extra={
            "provider": "github",
            "state": state
        })
        return url
    
    def exchange_code_for_token(self, code: str, state: str) -> OAuth2Token:
        """Exchange GitHub authorization code for access token"""
        try:
            data = {
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": code
            }
            
            request_data = urllib.parse.urlencode(data).encode('utf-8')
            request = urllib.request.Request(
                self.config.token_url,
                data=request_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
            )
            
            with urllib.request.urlopen(request) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            
            token = OAuth2Token(
                access_token=response_data["access_token"],
                token_type=response_data.get("token_type", "bearer"),
                expires_in=response_data.get("expires_in", 3600),
                scope=response_data.get("scope")
            )
            
            self.logger.info("Successfully exchanged GitHub OAuth2 code for token", extra={
                "provider": "github",
                "state": state
            })
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to exchange GitHub OAuth2 code: {e}")
            raise
    
    def get_user_info(self, token: OAuth2Token) -> OAuth2UserInfo:
        """Get GitHub user information using access token"""
        try:
            request = urllib.request.Request(
                self.config.user_info_url,
                headers={
                    "Authorization": f"token {token.access_token}",
                    "User-Agent": "VPA-Authentication/1.0"
                }
            )
            
            with urllib.request.urlopen(request) as response:
                user_data = json.loads(response.read().decode('utf-8'))
            
            # Get user email (GitHub API requires separate call for private emails)
            email = user_data.get("email")
            if not email:
                email = self._get_user_email(token)
            
            user_info = OAuth2UserInfo(
                provider_id=str(user_data["id"]),
                email=email,
                name=user_data.get("name") or user_data["login"],
                username=user_data["login"],
                avatar_url=user_data.get("avatar_url"),
                provider_name="github"
            )
            
            self.logger.info("Retrieved GitHub user information", extra={
                "provider": "github",
                "user_id": user_info.provider_id,
                "username": user_info.username
            })
            
            return user_info
            
        except Exception as e:
            self.logger.error(f"Failed to get GitHub user info: {e}")
            raise
    
    def _get_user_email(self, token: OAuth2Token) -> str:
        """Get GitHub user's primary email address"""
        try:
            request = urllib.request.Request(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"token {token.access_token}",
                    "User-Agent": "VPA-Authentication/1.0"
                }
            )
            
            with urllib.request.urlopen(request) as response:
                emails_data = json.loads(response.read().decode('utf-8'))
            
            # Find primary email
            for email_info in emails_data:
                if email_info.get("primary"):
                    return email_info["email"]
            
            # Fallback to first email
            if emails_data:
                return emails_data[0]["email"]
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"Failed to get GitHub user email: {e}")
            return ""

class OAuth2Manager:
    """Manager for OAuth2 providers and authentication flows"""
    
    def __init__(self):
        self.providers: Dict[str, OAuth2Provider] = {}
        self.pending_states: Dict[str, Dict[str, Any]] = {}
        self.logger = logger
    
    def register_provider(self, provider: OAuth2Provider):
        """Register an OAuth2 provider"""
        self.providers[provider.config.provider_name] = provider
        self.logger.info(f"Registered OAuth2 provider: {provider.config.provider_name}")
    
    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """Get OAuth2 provider by name"""
        return self.providers.get(provider_name)
    
    def generate_state(self, provider_name: str, user_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate secure state parameter for OAuth2 flow"""
        state = secrets.token_urlsafe(32)
        self.pending_states[state] = {
            "provider_name": provider_name,
            "created_at": time.time(),
            "user_data": user_data or {}
        }
        return state
    
    def validate_state(self, state: str, max_age: int = 600) -> Optional[Dict[str, Any]]:
        """Validate OAuth2 state parameter"""
        if state not in self.pending_states:
            return None
        
        state_data = self.pending_states[state]
        
        # Check if state is expired (default 10 minutes)
        if time.time() - state_data["created_at"] > max_age:
            del self.pending_states[state]
            return None
        
        # Remove state after validation (single use)
        del self.pending_states[state]
        return state_data
    
    def start_oauth2_flow(self, provider_name: str, user_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Start OAuth2 authentication flow"""
        provider = self.get_provider(provider_name)
        if not provider:
            self.logger.error(f"OAuth2 provider not found: {provider_name}")
            return None
        
        state = self.generate_state(provider_name, user_data)
        authorization_url = provider.get_authorization_url(state)
        
        self.logger.info("Started OAuth2 flow", extra={
            "provider": provider_name,
            "state": state
        })
        
        return authorization_url
    
    def complete_oauth2_flow(self, code: str, state: str) -> Dict[str, Any]:
        """Complete OAuth2 authentication flow"""
        try:
            # Validate state
            state_data = self.validate_state(state)
            if not state_data:
                return {"success": False, "error": "Invalid or expired state"}
            
            provider_name = state_data["provider_name"]
            provider = self.get_provider(provider_name)
            if not provider:
                return {"success": False, "error": "Provider not found"}
            
            # Exchange code for token
            token = provider.exchange_code_for_token(code, state)
            
            # Get user information
            user_info = provider.get_user_info(token)
            
            self.logger.info("Completed OAuth2 flow", extra={
                "provider": provider_name,
                "user_email": user_info.email
            })
            
            return {
                "success": True,
                "provider": provider_name,
                "user_info": user_info,
                "token": token,
                "user_data": state_data.get("user_data", {})
            }
            
        except Exception as e:
            self.logger.error(f"OAuth2 flow completion failed: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def cleanup_expired_states(self, max_age: int = 600):
        """Clean up expired OAuth2 states"""
        current_time = time.time()
        expired_states = [
            state for state, data in self.pending_states.items()
            if current_time - data["created_at"] > max_age
        ]
        
        for state in expired_states:
            del self.pending_states[state]
        
        if expired_states:
            self.logger.info(f"Cleaned up {len(expired_states)} expired OAuth2 states")
