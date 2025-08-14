"""
Global pytest config:
- Skip enterprise/advanced_llm tests unless explicitly enabled via env flags.
"""
import os
import pytest

def pytest_configure(config):
    """Add custom markers for feature flags."""
    config.addinivalue_line("markers", "enterprise: enterprise-only tests")
    config.addinivalue_line("markers", "advanced_llm: non-core LLM tests")

def pytest_collection_modifyitems(config, items):
    """Skip tests based on environment flags."""
    enterprise_enabled = os.getenv("VPA_ENABLE_ENTERPRISE", "0") == "1"
    advanced_llm_enabled = os.getenv("VPA_ENABLE_ADVANCED_LLM", "0") == "1"
    
    skip_enterprise = pytest.mark.skip(reason="VPA_ENABLE_ENTERPRISE=1 required")
    skip_advanced_llm = pytest.mark.skip(reason="VPA_ENABLE_ADVANCED_LLM=1 required")
    
    for item in items:
        if "enterprise" in item.keywords and not enterprise_enabled:
            item.add_marker(skip_enterprise)
        if "advanced_llm" in item.keywords and not advanced_llm_enabled:
            item.add_marker(skip_advanced_llm)
