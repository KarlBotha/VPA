"
Comprehensive tests for Auth Providers - Strategic Coverage Sprint
Strategic coverage improvement targeting 949 lines in Auth Providers.
"
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the source directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / \
src\))

def test_oauth2_config_import():
    \
\\Test
OAuth2Config
can
be
imported\\\
    from vpa.core.auth_providers import OAuth2Config
    assert OAuth2Config is not None

def test_oauth2_token_import():
    \
\\Test
OAuth2Token
can
be
imported\\\
    from vpa.core.auth_providers import OAuth2Token
    assert OAuth2Token is not None

def test_oauth2_config_creation():
    \
\\Test
OAuth2Config
creation\\\
    from vpa.core.auth_providers import OAuth2Config
    config = OAuth2Config(
        provider_name='test',
        client_id='test_id',
        client_secret='test_secret',
        authorization_url='https://example.com/auth',
        token_url='https://example.com/token',
        user_info_url='https://example.com/user',
        scopes=['read'],
        redirect_uri='https://example.com/callback'
    )
    assert config.provider_name == 'test'
    assert config.client_id == 'test_id'

def test_oauth2_token_creation():
    \
\\Test
OAuth2Token
creation
and
expiry\\\
    from vpa.core.auth_providers import OAuth2Token
    from datetime import datetime, timedelta
    token = OAuth2Token(
        access_token='test_token',
        token_type='bearer',
        expires_in=3600
    )
    assert token.access_token == 'test_token'
    assert token.token_type == 'bearer'
    assert not token.is_expired
