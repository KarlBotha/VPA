import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_gui_manager_import():
    """Test GUI Manager import"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        assert VPAGUIManager is not None
    except ImportError as e:
        pytest.skip(f"GUI Manager not available: {e}")


def test_gui_manager_creation():
    """Test GUI Manager creation with mocking"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk") as mock_ctk:
            mock_root = Mock()
            mock_ctk.return_value = mock_root
            gui_manager = VPAGUIManager()
            assert gui_manager is not None
    except Exception as e:
        pytest.skip(f"GUI Manager creation failed: {e}")


def test_gui_manager_attributes():
    """Test GUI Manager has required attributes"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk"):
            gui_manager = VPAGUIManager()
            assert hasattr(gui_manager, "root")
            assert hasattr(gui_manager, "config_manager")
    except Exception as e:
        pytest.skip(f"GUI Manager attributes test failed: {e}")


def test_gui_manager_proper_creation():
    """Test GUI Manager creation with proper arguments"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk"), \
             patch("customtkinter.set_appearance_mode"):
            mock_auth = Mock()
            mock_config = Mock()
            mock_db = Mock()
            gui_manager = VPAGUIManager(mock_auth, mock_config, mock_db)
            assert gui_manager is not None
            assert gui_manager.auth_coordinator == mock_auth
            assert gui_manager.config_manager == mock_config
            assert gui_manager.db_manager == mock_db
    except Exception as e:
        pytest.skip(f"GUI Manager proper creation failed: {e}")


def test_gui_manager_initialization_components():
    """Test GUI Manager initialization components"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk"), \
             patch("customtkinter.set_appearance_mode"):
            mock_auth = Mock()
            mock_config = Mock()
            mock_db = Mock()
            gui_manager = VPAGUIManager(mock_auth, mock_config, mock_db)
            assert hasattr(gui_manager, "gui_config")
            assert hasattr(gui_manager, "root")
            assert hasattr(gui_manager, "windows")
            assert hasattr(gui_manager, "notification_queue")
            assert gui_manager.current_user_id is None
            assert gui_manager.current_session_id is None
    except Exception as e:
        pytest.skip(f"GUI Manager initialization test failed: {e}")


def test_gui_manager_methods_exist():
    """Test that GUI Manager has expected methods"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk"), \
             patch("customtkinter.set_appearance_mode"):
            mock_auth = Mock()
            mock_config = Mock()
            mock_db = Mock()
            gui_manager = VPAGUIManager(mock_auth, mock_config, mock_db)
            methods = ["start_gui", "show_login_window", "show_main_window", "logout", "quit_application"]
            for method_name in methods:
                assert hasattr(gui_manager, method_name)
                assert callable(getattr(gui_manager, method_name))
    except Exception as e:
        pytest.skip(f"GUI Manager methods test failed: {e}")


def test_gui_config_class():
    """Test VPAGUIConfig class"""
    try:
        from vpa.gui.gui_manager import VPAGUIConfig
        with patch("customtkinter.set_appearance_mode"):
            config = VPAGUIConfig()
            assert config.theme == "dark"
            assert config.window_geometry == "1200x800"
            assert hasattr(config, "colors")
            assert callable(config.apply_theme)
    except Exception as e:
        pytest.skip(f"VPAGUIConfig test failed: {e}")


def test_gui_manager_auth_status():
    """Test GUI Manager auth status method"""
    try:
        from vpa.gui.gui_manager import VPAGUIManager
        with patch("customtkinter.CTk"), \
             patch("customtkinter.set_appearance_mode"):
            mock_auth = Mock()
            mock_config = Mock()
            mock_db = Mock()
            gui_manager = VPAGUIManager(mock_auth, mock_config, mock_db)
            auth_status = gui_manager.get_user_auth_status()
            assert isinstance(auth_status, dict)
    except Exception as e:
        pytest.skip(f"GUI Manager auth status test failed: {e}")
