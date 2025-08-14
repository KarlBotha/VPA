"""
VPA Main Entry Point
Application launcher with performance monitoring and comprehensive startup.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from vpa.core.app import app
from vpa.core.events import event_bus
from vpa.core.plugins import plugin_manager
from audio.voice_system import audio_system


def setup_logging():
    """Setup comprehensive logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('vpa.log', mode='a')
        ]
    )


async def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting VPA - Virtual Personal Assistant")
        
        # Start the application
        success = await app.startup()
        
        if not success:
            logger.error("❌ Application startup failed")
            return 1
        
        # Verify voice system
        verification = audio_system.verify_voice_catalog()
        logger.info(f"Voice system status: {verification['catalog_complete']}")
        
        # Print startup summary
        status = app.get_status()
        logger.info(f"📊 Startup Summary:")
        logger.info(f"   ⏱️ Startup time: {status['startup_time']:.2f}s")
        logger.info(f"   💾 Memory usage: {status['memory_usage_mb']:.1f}MB")
        logger.info(f"   🔌 Services ready: {len(status['services_ready'])}")
        logger.info(f"   ✅ Performance targets achieved: {status['performance_targets']['startup_time_achieved']}")
        
        # Keep application running
        logger.info("🟢 VPA is ready and running...")
        
        # Simulate some activity
        while app._running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"💥 Application error: {e}")
        return 1
    finally:
        # Graceful shutdown
        await app.shutdown()
        logger.info("🛑 VPA shutdown complete")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)