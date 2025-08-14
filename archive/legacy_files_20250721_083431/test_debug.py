import asyncio
import sys
sys.path.append('src')
from vpa.ai.ai_coordinator import AICoordinator
from unittest.mock import MagicMock

async def test_complexity_and_approval():
    event_bus = MagicMock()
    coordinator = AICoordinator(event_bus)
    coordinator._initialize_nlp_patterns()
    
    commands = [
        'what is the time',
        'create a file and save it', 
        'create file then upload to server then send email and update database',
        'delete all files',
        'restart the server',
        'install new software',
        'show current status',
        'create a simple text file'
    ]
    
    for cmd in commands:
        parsed = await coordinator._parse_command_advanced(cmd, {})
        complexity = coordinator._assess_complexity(parsed)
        approval = coordinator._requires_approval(parsed)
        print(f'Command: {cmd}')
        print(f'  Complexity: {complexity}')  
        print(f'  Approval: {approval}')
        print(f'  Confidence: {parsed.confidence}')
        print()

asyncio.run(test_complexity_and_approval())
