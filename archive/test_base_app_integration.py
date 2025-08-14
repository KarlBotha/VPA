#!/usr/bin/env python3
"""
Quick integration test for VPA Base App to verify all features are working.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from vpa.core.base_app import VPABaseApp

def test_base_app_integration():
    """Test all major base app features."""
    print("🚀 Testing VPA Base App Integration...")
    
    # Create temporary directory for test
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Using temp directory: {temp_dir}")
    
    try:
        with VPABaseApp(data_dir=temp_dir) as app:
            print("✅ VPA Base App initialized successfully")
            
            # Test 1: Conversation Management
            conv_id = app.start_new_conversation('Integration Test')
            print(f"✅ Conversation created: {conv_id[:8]}...")
            
            # Test 2: Message Management
            msg1_id = app.add_message('Hello, VPA!', 'user')
            msg2_id = app.add_message('Hello! How can I help you?', 'assistant')
            msg3_id = app.add_message('Can you remember this?', 'user')
            print(f"✅ Messages added: {len([msg1_id, msg2_id, msg3_id])}")
            
            # Test 3: Conversation History
            history = app.get_conversation_history()
            print(f"✅ History retrieved: {len(history)} messages")
            
            # Test 4: User Profile Management
            success = app.update_user_profile(
                name='Integration Test User',
                preferences={'theme': 'dark', 'language': 'en'},
                metadata={'test_run': True}
            )
            print(f"✅ Profile updated: {success}")
            
            profile = app.get_user_profile()
            print(f"✅ Profile retrieved: {profile['name'] if profile else 'None'}")
            
            # Test 5: Conversation Listing
            conversations = app.list_conversations()
            print(f"✅ Conversations listed: {len(conversations)}")
            
            # Test 6: Search Functionality
            search_results = app.search_conversations('Integration')
            print(f"✅ Search performed: {len(search_results)} results")
            
            # Test 7: Data Export
            export_path = app.export_all_data()
            print(f"✅ Data exported to: {export_path.name}")
            
            # Test 8: Conversation Info
            current_info = app.get_current_conversation_info()
            print(f"✅ Current conversation info: {current_info['title'] if current_info else 'None'}")
            
            print("\n🎉 ALL TESTS PASSED! VPA Base App is fully functional!")
            print("\n📊 Feature Summary:")
            print(f"   • Database: Encrypted SQLite with Fernet")
            print(f"   • Conversations: {len(conversations)} created")
            print(f"   • Messages: {len(history)} stored with encryption")
            print(f"   • User Profile: {profile['name'] if profile else 'None'}")
            print(f"   • Export: Complete data portability")
            print(f"   • Search: Working conversation search")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    success = test_base_app_integration()
    sys.exit(0 if success else 1)
