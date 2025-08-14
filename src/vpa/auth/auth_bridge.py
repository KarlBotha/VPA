import json
from ..util.dynload import load_symbol_from_paths, get_recovery_map, resolve_relative_path

def get_auth_coordinator(recover_map_path="tools/recover/recover_map.json"):
    """Get authentication coordinator from current or recovered sources"""
    
    # Try native import first
    try:
        from vpa.core.auth_coordinator import VPAAuthenticationCoordinator  # type: ignore
        return VPAAuthenticationCoordinator
    except ImportError:
        pass
    
    # Try recovery from archives
    recovery_map = get_recovery_map(recover_map_path)
    auth_candidates = recovery_map.get("auth_coord", [])
    
    if auth_candidates:
        auth_candidates = [resolve_relative_path(p) for p in auth_candidates]
        
        # Try to load authentication coordinator
        auth_coord = load_symbol_from_paths("VPAAuthenticationCoordinator", auth_candidates)
        if auth_coord:
            return auth_coord
        
        # Try alternative names
        for class_name in ["AuthCoordinator", "AuthenticationCoordinator", "AuthManager"]:
            auth_class = load_symbol_from_paths(class_name, auth_candidates)
            if auth_class:
                return auth_class
    
    # Fallback: simple auth coordinator
    return create_fallback_auth_coordinator()

def get_secure_config_manager(recover_map_path="tools/recover/recover_map.json"):
    """Get secure configuration manager"""
    
    try:
        from vpa.core.config import SecureConfigManager  # type: ignore
        return SecureConfigManager
    except ImportError:
        pass
    
    # Try recovery
    recovery_map = get_recovery_map(recover_map_path)
    config_candidates = recovery_map.get("secure_config", [])
    
    if config_candidates:
        config_candidates = [resolve_relative_path(p) for p in config_candidates]
        
        config_manager = load_symbol_from_paths("SecureConfigManager", config_candidates)
        if config_manager:
            return config_manager
        
        # Try alternatives
        for class_name in ["ConfigManager", "Config", "Settings"]:
            config_class = load_symbol_from_paths(class_name, config_candidates)
            if config_class:
                return config_class
    
    # Fallback
    return create_fallback_config_manager()

def create_fallback_auth_coordinator():
    """Create a simple fallback authentication coordinator"""
    
    class FallbackAuthCoordinator:
        def __init__(self):
            self.is_authenticated = False
            self.current_user = None
        
        def login(self, username, password):
            """Simple login - accepts any non-empty credentials"""
            if username and password:
                self.is_authenticated = True
                self.current_user = username
                return True
            return False
        
        def logout(self):
            """Logout current user"""
            self.is_authenticated = False
            self.current_user = None
        
        def register(self, username, password, email=None):
            """Simple registration - accepts any credentials"""
            if username and password:
                return {"success": True, "message": "Registration successful"}
            return {"success": False, "message": "Invalid credentials"}
        
        def is_logged_in(self):
            """Check if user is logged in"""
            return self.is_authenticated
        
        def get_current_user(self):
            """Get current user"""
            return self.current_user
    
    return FallbackAuthCoordinator

def create_fallback_config_manager():
    """Create a simple fallback configuration manager"""
    
    class FallbackConfigManager:
        def __init__(self):
            self.config = {}
        
        def get(self, key, default=None):
            """Get configuration value"""
            return self.config.get(key, default)
        
        def set(self, key, value):
            """Set configuration value"""
            self.config[key] = value
        
        def save(self):
            """Save configuration (no-op in fallback)"""
            pass
        
        def load(self):
            """Load configuration (no-op in fallback)"""
            pass
    
    return FallbackConfigManager

def run_auth_flow():
    """Run authentication flow with GUI or CLI"""
    auth_coordinator_class = get_auth_coordinator()
    auth_coordinator = auth_coordinator_class()
    
    # Try to import GUI login window
    recovery_map = get_recovery_map()
    login_candidates = recovery_map.get("login_window", [])
    
    if login_candidates:
        login_candidates = [resolve_relative_path(p) for p in login_candidates]
        
        # Try to load login window
        for class_name in ["LoginWindow", "VPALoginWindow", "AuthWindow"]:
            login_window_class = load_symbol_from_paths(class_name, login_candidates)
            if login_window_class:
                try:
                    login_window = login_window_class(auth_coordinator)
                    if hasattr(login_window, 'show'):
                        return login_window.show()
                    elif hasattr(login_window, 'run'):
                        return login_window.run()
                except Exception as e:
                    print(f"Login window failed: {e}")
    
    # Fallback to CLI authentication
    return run_cli_auth(auth_coordinator)

def run_cli_auth(auth_coordinator):
    """Simple CLI authentication"""
    import getpass
    
    print("VPA Authentication")
    print("1. Login")
    print("2. Register")
    choice = input("Choice (1/2): ").strip()
    
    if choice == "1":
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        if auth_coordinator.login(username, password):
            print(f"Welcome back, {username}!")
            return True
        else:
            print("Login failed.")
            return False
    
    elif choice == "2":
        username = input("Username: ").strip()
        email = input("Email (optional): ").strip()
        password = getpass.getpass("Password: ")
        
        result = auth_coordinator.register(username, password, email)
        if result.get("success"):
            print(result.get("message", "Registration successful"))
            return True
        else:
            print(result.get("message", "Registration failed"))
            return False
    
    return False
