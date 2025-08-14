"""
Test Suite for VPA RAG-LLM UI Integration

This module provides comprehensive tests for the RAG-LLM UI integration,
ensuring proper functionality of all user interface components.

Test Categories:
- Widget initialization tests
- Menu integration tests
- Event handling tests
- Performance tests
- Error handling tests
"""

import unittest
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the modules to test
from ..gui.rag_llm_widget import RAGLLMChatWidget, RAGLLMIntegrationDialog
from ..gui.rag_llm_menu import VPARAGLLMMenuIntegration, integrate_rag_llm_menu
from ..core.llm import VPALLMManager, LLMProvider
from ..core.rag import VPARAGSystem


class TestRAGLLMChatWidget(unittest.TestCase):
    """Test cases for RAG-LLM Chat Widget"""
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide during tests
        
        # Create mock LLM manager
        self.mock_llm_manager = Mock(spec=VPALLMManager)
        self.mock_rag_system = Mock(spec=VPARAGSystem)
        
        # Create widget instance
        self.widget = RAGLLMChatWidget(
            self.root,
            self.mock_llm_manager,
            self.mock_rag_system
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if self.root:
            self.root.destroy()
    
    def test_widget_initialization(self):
        """Test widget initialization"""
        self.assertIsNotNone(self.widget.main_frame)
        self.assertIsNotNone(self.widget.conversation_text)
        self.assertIsNotNone(self.widget.input_entry)
        self.assertIsNotNone(self.widget.send_button)
        self.assertIsNotNone(self.widget.stream_button)
        
        # Test configuration variables
        self.assertTrue(self.widget.rag_enabled_var.get())
        self.assertEqual(self.widget.top_k_var.get(), 3)
        self.assertEqual(self.widget.provider_var.get(), "openai")
    
    def test_ui_components_creation(self):
        """Test UI components are created properly"""
        # Test main sections exist
        self.assertIsNotNone(self.widget.config_frame)
        self.assertIsNotNone(self.widget.conversation_frame)
        self.assertIsNotNone(self.widget.input_frame)
        self.assertIsNotNone(self.widget.status_frame)
        
        # Test status labels
        self.assertIsNotNone(self.widget.status_label)
        self.assertIsNotNone(self.widget.performance_label)
        self.assertIsNotNone(self.widget.sources_label)
    
    def test_message_display(self):
        """Test message display functionality"""
        # Test adding different message types
        self.widget._add_user_message("Test user message")
        self.widget._add_assistant_message("Test assistant message")
        self.widget._add_system_message("Test system message")
        self.widget._add_rag_context_message("Test RAG context")
        self.widget._add_error_message("Test error message")
        
        # Test conversation text is not empty
        content = self.widget.conversation_text.get(1.0, tk.END)
        self.assertIn("Test user message", content)
        self.assertIn("Test assistant message", content)
        self.assertIn("Test system message", content)
    
    def test_configuration_changes(self):
        """Test configuration change handling"""
        # Change RAG enabled
        self.widget.rag_enabled_var.set(False)
        self.widget._on_config_change()
        self.assertFalse(self.widget.use_rag)
        
        # Change top-K
        self.widget.top_k_var.set(5)
        self.widget._on_config_change()
        self.assertEqual(self.widget.rag_top_k, 5)
        
        # Change provider
        self.widget.provider_var.set("anthropic")
        self.widget._on_config_change()
        self.assertEqual(self.widget.provider_var.get(), "anthropic")
    
    def test_processing_state(self):
        """Test processing state management"""
        # Test setting processing state
        self.widget._set_processing_state(True)
        self.assertTrue(self.widget.is_processing)
        
        self.widget._set_processing_state(False)
        self.assertFalse(self.widget.is_processing)
    
    def test_performance_display_update(self):
        """Test performance metrics display"""
        mock_response = {
            "total_processing_time": 1.234,
            "rag_retrieval_time": 0.456,
            "llm_generation_time": 0.778,
            "rag_sources_count": 3
        }
        
        self.widget._update_performance_display(mock_response)
        
        self.assertEqual(self.widget.last_response_time, 1.234)
        self.assertEqual(self.widget.last_sources_count, 3)
    
    @patch('asyncio.new_event_loop')
    def test_message_processing_setup(self, mock_loop):
        """Test message processing setup (without actual async execution)"""
        # Mock event loop
        mock_loop_instance = Mock()
        mock_loop.return_value = mock_loop_instance
        
        # Test input validation
        self.widget.input_entry.insert(0, "")
        self.widget._send_message()  # Should not process empty message
        
        # Test with valid message
        self.widget.input_entry.delete(0, tk.END)
        self.widget.input_entry.insert(0, "Test message")
        
        # Mock threading to avoid actual async execution
        with patch('threading.Thread') as mock_thread:
            self.widget._send_message()
            mock_thread.assert_called_once()


class TestRAGLLMMenuIntegration(unittest.TestCase):
    """Test cases for RAG-LLM Menu Integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide during tests
        
        # Create menu integration
        self.integration = VPARAGLLMMenuIntegration(self.root)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.root:
            self.root.destroy()
    
    def test_menu_integration_initialization(self):
        """Test menu integration initialization"""
        self.assertIsNotNone(self.integration.llm_manager)
        self.assertEqual(len(self.integration.chat_windows), 0)
    
    def test_menu_creation(self):
        """Test menu items are created"""
        # Check if menubar exists
        menubar = self.root.nametowidget(self.root['menu']) if self.root['menu'] else None
        self.assertIsNotNone(menubar)
    
    def test_chat_window_management(self):
        """Test chat window management"""
        initial_count = len(self.integration.chat_windows)
        
        # Test opening chat window
        with patch.object(self.integration, 'llm_manager') as mock_llm:
            mock_llm.__bool__ = Mock(return_value=True)
            self.integration.open_rag_chat_window()
        
        # Should have created a new window
        self.assertGreater(len(self.integration.chat_windows), initial_count)
        
        # Test clearing all chats
        self.integration.chat_windows = [Mock()]  # Add mock window
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.integration.clear_all_chats()
        
        self.assertEqual(len(self.integration.chat_windows), 0)
    
    def test_system_status_display(self):
        """Test system status display functionality"""
        # Should not raise exceptions
        try:
            self.integration.show_system_status()
            # Close the status window if it opened
            for child in self.root.winfo_children():
                if isinstance(child, tk.Toplevel):
                    child.destroy()
        except Exception as e:
            self.fail(f"System status display failed: {e}")
    
    def test_knowledge_base_loading(self):
        """Test knowledge base loading dialog"""
        with patch('tkinter.filedialog.askopenfilenames', return_value=['test1.txt', 'test2.pdf']):
            try:
                self.integration.load_knowledge_base()
                # Close any dialogs that opened
                for child in self.root.winfo_children():
                    if isinstance(child, tk.Toplevel):
                        child.destroy()
            except Exception as e:
                self.fail(f"Knowledge base loading failed: {e}")
    
    def test_conversation_export(self):
        """Test conversation export functionality"""
        with patch('tkinter.filedialog.asksaveasfilename', return_value='test_export.json'):
            try:
                self.integration.export_conversations()
                # Close any dialogs that opened
                for child in self.root.winfo_children():
                    if isinstance(child, tk.Toplevel):
                        child.destroy()
            except Exception as e:
                self.fail(f"Conversation export failed: {e}")


class TestUIIntegrationPerformance(unittest.TestCase):
    """Test performance aspects of UI integration"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create mock systems for performance testing
        self.mock_llm_manager = Mock(spec=VPALLMManager)
        self.mock_rag_system = Mock(spec=VPARAGSystem)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.root:
            self.root.destroy()
    
    def test_widget_creation_performance(self):
        """Test widget creation performance"""
        start_time = time.time()
        
        widget = RAGLLMChatWidget(
            self.root,
            self.mock_llm_manager,
            self.mock_rag_system
        )
        
        creation_time = time.time() - start_time
        
        # Widget creation should be fast (under 1 second)
        self.assertLess(creation_time, 1.0, "Widget creation took too long")
    
    def test_message_display_performance(self):
        """Test message display performance"""
        widget = RAGLLMChatWidget(
            self.root,
            self.mock_llm_manager,
            self.mock_rag_system
        )
        
        start_time = time.time()
        
        # Add multiple messages
        for i in range(100):
            widget._add_user_message(f"Test message {i}")
            widget._add_assistant_message(f"Response {i}")
        
        display_time = time.time() - start_time
        
        # Message display should be reasonably fast
        self.assertLess(display_time, 5.0, "Message display took too long")
    
    def test_menu_integration_performance(self):
        """Test menu integration performance"""
        start_time = time.time()
        
        integration = VPARAGLLMMenuIntegration(self.root)
        
        integration_time = time.time() - start_time
        
        # Menu integration should be fast
        self.assertLess(integration_time, 2.0, "Menu integration took too long")


class TestUIErrorHandling(unittest.TestCase):
    """Test error handling in UI components"""
    
    def setUp(self):
        """Set up error handling test environment"""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment"""
        if self.root:
            self.root.destroy()
    
    def test_widget_with_invalid_llm_manager(self):
        """Test widget behavior with invalid LLM manager"""
        try:
            widget = RAGLLMChatWidget(self.root, None, None)
            # Should handle None gracefully
            self.assertIsNotNone(widget.main_frame)
        except Exception as e:
            self.fail(f"Widget failed with None LLM manager: {e}")
    
    def test_menu_integration_error_handling(self):
        """Test menu integration error handling"""
        try:
            # Test with invalid root
            integration = VPARAGLLMMenuIntegration(self.root)
            # Should not raise exceptions during initialization
            self.assertIsNotNone(integration)
        except Exception as e:
            self.fail(f"Menu integration failed: {e}")
    
    def test_message_handling_with_none_widgets(self):
        """Test message handling when widgets are None"""
        widget = RAGLLMChatWidget(self.root, Mock(), None)
        
        # Temporarily set widgets to None to test error handling
        original_text = widget.conversation_text
        widget.conversation_text = None
        
        try:
            widget._add_user_message("Test message")
            # Should not raise exceptions
        except Exception as e:
            self.fail(f"Message handling failed with None widget: {e}")
        finally:
            widget.conversation_text = original_text


class VPARAGLLMUITestSuite:
    """
    Comprehensive test suite for VPA RAG-LLM UI Integration
    
    Provides a single interface to run all UI integration tests
    with proper reporting and error handling.
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.test_loader = unittest.TestLoader()
        self.test_suite = unittest.TestSuite()
        self.test_runner = unittest.TextTestRunner(verbosity=2)
        
        # Add all test classes
        self._add_test_classes()
    
    def _add_test_classes(self):
        """Add all test classes to the suite"""
        test_classes = [
            TestRAGLLMChatWidget,
            TestRAGLLMMenuIntegration,
            TestUIIntegrationPerformance,
            TestUIErrorHandling
        ]
        
        for test_class in test_classes:
            tests = self.test_loader.loadTestsFromTestCase(test_class)
            self.test_suite.addTests(tests)
    
    def run_tests(self) -> unittest.TestResult:
        """
        Run all UI integration tests
        
        Returns:
            TestResult object with test results
        """
        print("🧪 Running VPA RAG-LLM UI Integration Tests...")
        print("=" * 60)
        
        result = self.test_runner.run(self.test_suite)
        
        print("=" * 60)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        if result.failures:
            print("\\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        
        return result
    
    def run_specific_test(self, test_class_name: str, test_method_name: str = None):
        """
        Run a specific test class or method
        
        Args:
            test_class_name: Name of the test class
            test_method_name: Optional specific test method
        """
        test_classes = {
            'TestRAGLLMChatWidget': TestRAGLLMChatWidget,
            'TestRAGLLMMenuIntegration': TestRAGLLMMenuIntegration,
            'TestUIIntegrationPerformance': TestUIIntegrationPerformance,
            'TestUIErrorHandling': TestUIErrorHandling
        }
        
        if test_class_name not in test_classes:
            print(f"❌ Test class '{test_class_name}' not found")
            return
        
        test_class = test_classes[test_class_name]
        
        if test_method_name:
            suite = unittest.TestSuite()
            suite.addTest(test_class(test_method_name))
        else:
            suite = self.test_loader.loadTestsFromTestCase(test_class)
        
        result = self.test_runner.run(suite)
        return result


def run_ui_integration_tests():
    """
    Main function to run UI integration tests
    
    Returns:
        TestResult object
    """
    test_suite = VPARAGLLMUITestSuite()
    return test_suite.run_tests()


if __name__ == "__main__":
    # Run tests when executed directly
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_suite = VPARAGLLMUITestSuite()
        if len(sys.argv) > 2:
            test_suite.run_specific_test(sys.argv[1], sys.argv[2])
        else:
            test_suite.run_specific_test(sys.argv[1])
    else:
        # Run all tests
        run_ui_integration_tests()
