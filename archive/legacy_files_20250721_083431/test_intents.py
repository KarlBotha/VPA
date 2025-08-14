import asyncio
import sys
sys.path.append('src')
from vpa.ai.ai_coordinator import AICoordinator
from unittest.mock import MagicMock

async def test_intents():
    event_bus = MagicMock()
    coordinator = AICoordinator(event_bus)
    coordinator._initialize_nlp_patterns()
    
    commands = [
        'create a new file',
        'delete the old folder', 
        'execute the backup script',
        'show me the current status',
        'update the configuration'
    ]
    
    for cmd in commands:
        result = await coordinator._detect_intent(cmd)
        print(f'Command: {cmd} -> Intent: {result["intent"]}')

asyncio.run(test_intents())
