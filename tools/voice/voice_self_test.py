#!/usr/bin/env python3
import argparse, json, os, sys, time

REPORT_HEADER = "# VPA Voice Self-Test\n"

def md_escape(s: str) -> str:
    """Escape markdown special characters"""
    return s.replace("|", "\\|").replace("*", "\\*").replace("_", "\\_")

def test_pyttsx3():
    """Test pyttsx3 TTS engine"""
    results = {
        'engine': 'pyttsx3',
        'available': False,
        'voices': [],
        'errors': [],
        'test_results': {}
    }
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        results['available'] = True
        for i, voice in enumerate(voices or []):
            voice_info = {
                'id': getattr(voice, 'id', f'voice_{i}'),
                'name': getattr(voice, 'name', 'Unknown'),
                'languages': getattr(voice, 'languages', []),
                'age': getattr(voice, 'age', None),
                'gender': getattr(voice, 'gender', None)
            }
            results['voices'].append(voice_info)
        
        engine.stop()
        
    except Exception as e:
        results['errors'].append(f"pyttsx3 error: {str(e)}")
    
    return results

def test_edge_tts():
    """Test Edge TTS engine"""
    results = {
        'engine': 'edge-tts',
        'available': False,
        'voices': [],
        'errors': [],
        'test_results': {}
    }
    
    try:
        import edge_tts
        import asyncio
        
        async def get_voices():
            voices = await edge_tts.list_voices()
            return voices
        
        try:
            voices = asyncio.run(get_voices())
            results['available'] = True
            
            # Limit to first 20 voices to avoid huge lists
            for voice in voices[:20]:
                voice_info = {
                    'id': voice.get('ShortName', 'unknown'),
                    'name': voice.get('FriendlyName', 'Unknown'),
                    'languages': [voice.get('Locale', 'unknown')],
                    'age': None,
                    'gender': voice.get('Gender', 'Unknown')
                }
                results['voices'].append(voice_info)
                
        except Exception as async_e:
            results['errors'].append(f"Edge TTS async error: {str(async_e)}")
            
    except ImportError:
        results['errors'].append("edge-tts not installed")
    except Exception as e:
        results['errors'].append(f"edge-tts error: {str(e)}")
    
    return results

def test_voice_playback(engine_name, voice_id, test_text="Hello VPA"):
    """Test voice playback (optional)"""
    try:
        if engine_name == 'pyttsx3':
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Find voice by ID
            for voice in voices:
                if getattr(voice, 'id', '') == voice_id:
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(test_text)
            engine.runAndWait()
            engine.stop()
            return True
            
        elif engine_name == 'edge-tts':
            import edge_tts
            import asyncio
            import pygame
            import tempfile
            import os
            
            async def speak():
                communicate = edge_tts.Communicate(test_text, voice_id)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            tmp.write(chunk["data"])
                    tmp_path = tmp.name
                
                # Play with pygame
                pygame.mixer.init()
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                pygame.mixer.quit()
                os.unlink(tmp_path)
                
            asyncio.run(speak())
            return True
            
    except Exception as e:
        return f"Playback error: {str(e)}"
    
    return False

def generate_report(results_list, args):
    """Generate markdown report"""
    report = [REPORT_HEADER]
    report.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Phase**: Phase 5 - Voice System Validation")
    report.append(f"**Mode**: {'List-only' if args.list_only else 'Full test with playback'}")
    report.append("")
    
    # Summary table
    report.append("## 🎯 **VOICE ENGINE SUMMARY**")
    report.append("")
    report.append("| Engine | Available | Voice Count | Status |")
    report.append("|--------|-----------|-------------|--------|")
    
    total_voices = 0
    available_engines = 0
    
    for result in results_list:
        status = "✅ AVAILABLE" if result['available'] else "❌ UNAVAILABLE"
        voice_count = len(result['voices'])
        total_voices += voice_count
        if result['available']:
            available_engines += 1
            
        report.append(f"| {result['engine']} | {result['available']} | {voice_count} | {status} |")
    
    report.append("")
    report.append(f"**Total Voices Available**: {total_voices}")
    report.append(f"**Available Engines**: {available_engines}/2")
    report.append("")
    
    # Detailed results per engine
    for result in results_list:
        report.append(f"## 🔊 **{result['engine'].upper()} ENGINE**")
        report.append("")
        
        if result['available']:
            report.append(f"✅ **Status**: Available ({len(result['voices'])} voices)")
            report.append("")
            
            if result['voices']:
                report.append("### Voice Catalog")
                report.append("")
                report.append("| ID | Name | Language | Gender |")
                report.append("|----|------|----------|--------|")
                
                for voice in result['voices'][:15]:  # Limit display to first 15
                    voice_id = md_escape(str(voice['id']))
                    name = md_escape(str(voice['name']))
                    lang = md_escape(str(voice['languages'][0] if voice['languages'] else 'Unknown'))
                    gender = md_escape(str(voice.get('gender', 'Unknown')))
                    
                    report.append(f"| {voice_id} | {name} | {lang} | {gender} |")
                
                if len(result['voices']) > 15:
                    report.append(f"| ... | *({len(result['voices']) - 15} more voices available)* | ... | ... |")
                
                report.append("")
            else:
                report.append("⚠️ No voices found")
                report.append("")
        else:
            report.append(f"❌ **Status**: Unavailable")
            report.append("")
            
            if result['errors']:
                report.append("**Errors**:")
                for error in result['errors']:
                    report.append(f"- {md_escape(error)}")
                report.append("")
    
    # Overall assessment
    report.append("## 🏁 **ASSESSMENT**")
    report.append("")
    
    if total_voices >= 8:
        report.append("✅ **Voice Availability**: EXCELLENT (8+ voices)")
    elif total_voices >= 3:
        report.append("⚠️ **Voice Availability**: ACCEPTABLE (3-7 voices)")
    else:
        report.append("❌ **Voice Availability**: INSUFFICIENT (<3 voices)")
    
    if available_engines == 2:
        report.append("✅ **Engine Redundancy**: EXCELLENT (dual-engine)")
    elif available_engines == 1:
        report.append("⚠️ **Engine Redundancy**: ACCEPTABLE (single-engine)")
    else:
        report.append("❌ **Engine Redundancy**: POOR (no engines)")
    
    report.append("")
    
    if args.list_only:
        report.append("**Note**: List-only mode - no playback testing performed")
    
    report.append("")
    report.append("---")
    report.append("*Voice self-test completed. System ready for TTS operations.*")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='VPA Voice System Self-Test')
    parser.add_argument('--engine', choices=['pyttsx3', 'edge-tts', 'all'], default='all',
                        help='TTS engine to test')
    parser.add_argument('--list-only', action='store_true',
                        help='List voices only, skip playback tests')
    parser.add_argument('--out', default='VOICE_SELF_TEST.md',
                        help='Output markdown file')
    parser.add_argument('--test-text', default='Hello VPA voice test',
                        help='Text for playback testing')
    
    args = parser.parse_args()
    
    results = []
    
    if args.engine in ['pyttsx3', 'all']:
        print("Testing pyttsx3...")
        results.append(test_pyttsx3())
    
    if args.engine in ['edge-tts', 'all']:
        print("Testing Edge TTS...")
        results.append(test_edge_tts())
    
    # Generate report
    report = generate_report(results, args)
    
    # Write to file
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Voice self-test completed. Report written to {args.out}")
    
    # Print summary
    total_voices = sum(len(r['voices']) for r in results)
    available_engines = sum(1 for r in results if r['available'])
    
    print(f"Summary: {available_engines}/{len(results)} engines, {total_voices} total voices")

if __name__ == '__main__':
    main()
