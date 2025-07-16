"""
Command Line Interface for VPA.
Provides CLI commands and delegates to the main App class.
"""

import click
import logging
import sys
import os
from pathlib import Path
from typing import Optional
from vpa.core.app import App


def validate_config_path(config_path: Optional[str]) -> Optional[str]:
    """Validate and sanitize configuration file path."""
    if not config_path:
        return None
    
    try:
        path = Path(config_path).resolve()
        
        # Security: Prevent path traversal attacks
        if '..' in str(path) or str(path).startswith('/etc/') or str(path).startswith('C:\\Windows\\'):
            raise click.BadParameter(f"Invalid config path: {config_path}")
        
        # Check if path exists and is a file
        if path.exists() and not path.is_file():
            raise click.BadParameter(f"Config path is not a file: {config_path}")
        
        # Check file extension
        if path.suffix not in ['.yaml', '.yml', '.json']:
            click.echo(f"Warning: Config file should have .yaml, .yml, or .json extension", err=True)
        
        return str(path)
    except (OSError, ValueError) as e:
        raise click.BadParameter(f"Invalid config path: {e}")


def validate_log_level(log_level: str) -> str:
    """Validate log level parameter."""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    log_level_upper = log_level.upper()
    
    if log_level_upper not in valid_levels:
        raise click.BadParameter(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
    
    return log_level_upper


def validate_text_input(text: str) -> str:
    """Validate text input for speak command."""
    if not text or not text.strip():
        raise click.BadParameter("Text cannot be empty")
    
    # Limit text length for security and performance
    max_length = 1000
    if len(text) > max_length:
        raise click.BadParameter(f"Text too long. Maximum {max_length} characters allowed")
    
    # Basic sanitization
    sanitized = text.strip()
    
    # Remove potential command injection characters
    dangerous_chars = ['`', '$', '&', '|', ';', '<', '>']
    for char in dangerous_chars:
        if char in sanitized:
            click.echo(f"Warning: Removed potentially dangerous character: {char}", err=True)
            sanitized = sanitized.replace(char, '')
    
    return sanitized


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration with validation."""
    try:
        validated_level = validate_log_level(log_level)
        logging.basicConfig(
            level=getattr(logging, validated_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    except Exception as e:
        click.echo(f"Error setting up logging: {e}", err=True)
        # Fallback to INFO level
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


@click.group()
@click.option('--log-level', default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--config', help='Path to configuration file (.yaml, .yml, .json)')
@click.pass_context
def cli(ctx, log_level, config):
    """VPA - Virtual Personal Assistant CLI."""
    ctx.ensure_object(dict)
    
    # Validate and store log level
    try:
        validated_log_level = validate_log_level(log_level)
        ctx.obj['log_level'] = validated_log_level
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # Validate and store config path
    try:
        validated_config = validate_config_path(config)
        ctx.obj['config'] = validated_config
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    setup_logging(ctx.obj['log_level'])


@cli.command()
@click.pass_context
def start(ctx):
    """Start the VPA application."""
    config_path = ctx.obj.get('config')
    
    try:
        app = App(config_path)
        app.initialize()
        app.start()
        
        click.echo("VPA started successfully. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        try:
            while app.is_running():
                pass
        except KeyboardInterrupt:
            click.echo("\\nShutting down VPA...")
            app.stop()
            
    except Exception as e:
        click.echo(f"Error starting VPA: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Check VPA status."""
    config_path = ctx.obj.get('config')
    
    try:
        app = App(config_path)
        app.initialize()
        
        if app.is_running():
            click.echo("VPA Status: Running")
        else:
            click.echo("VPA Status: Not running")
            
        # Additional status information
        plugin_count = len(app.plugin_manager.loaded_plugins)
        click.echo(f"Loaded plugins: {plugin_count}")
        
    except Exception as e:
        click.echo(f"VPA Status: Error - {e}")


@cli.command()
@click.pass_context  
def config_show(ctx):
    """Show current configuration."""
    config_path = ctx.obj.get('config')
    
    try:
        app = App(config_path)
        app.initialize()
        
        config = app.config_manager.config
        click.echo("Current VPA Configuration:")
        click.echo(f"Config file: {app.config_manager.config_path}")
        
        for key, value in config.items():
            # Don't display sensitive information
            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                click.echo(f"  {key}: [HIDDEN]")
            else:
                click.echo(f"  {key}: {value}")
            
    except Exception as e:
        click.echo(f"Error reading config: {e}", err=True)


@cli.group()
@click.pass_context
def audio(ctx):
    """Audio system commands."""
    pass


@audio.command()
@click.argument('text')
@click.option('--voice', help='Voice to use for speaking')
@click.option('--rate', type=int, help='Speech rate (words per minute)')
@click.option('--volume', type=float, help='Volume level (0.0-1.0)')
@click.pass_context
def speak(ctx, text, voice, rate, volume):
    """Make VPA speak the given text."""
    config_path = ctx.parent.obj.get('config')
    
    try:
        # Validate text input
        validated_text = validate_text_input(text)
        
        # Validate optional parameters
        if rate is not None and (rate < 50 or rate > 400):
            raise click.BadParameter("Rate must be between 50 and 400 words per minute")
        
        if volume is not None and (volume < 0.0 or volume > 1.0):
            raise click.BadParameter("Volume must be between 0.0 and 1.0")
        
        app = App(config_path)
        app.initialize()
        
        # Get audio plugin
        audio_plugin = app.plugin_manager.get_plugin('audio')
        if not audio_plugin:
            click.echo("Error: Audio plugin not available", err=True)
            sys.exit(1)
        
        # Set voice parameters if provided
        if voice:
            try:
                audio_plugin.audio_engine.set_voice(voice)
            except Exception as e:
                click.echo(f"Warning: Could not set voice '{voice}': {e}", err=True)
        
        if rate:
            audio_plugin.audio_engine.set_rate(rate)
        
        if volume:
            audio_plugin.audio_engine.set_volume(volume)
        
        # Speak the text
        click.echo(f"Speaking: {validated_text}")
        audio_plugin.audio_engine.speak(validated_text)
        
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audio.command()
@click.pass_context
def list_voices(ctx):
    """List available voices."""
    config_path = ctx.parent.obj.get('config')
    
    try:
        app = App(config_path)
        app.initialize()
        
        # Get audio plugin
        audio_plugin = app.plugin_manager.get_plugin('audio')
        if not audio_plugin:
            click.echo("Error: Audio plugin not available", err=True)
            sys.exit(1)
        
        voices = audio_plugin.audio_engine.get_available_voices()
        
        if not voices:
            click.echo("No voices available")
            return
        
        click.echo("Available Voices:")
        click.echo("=" * 50)
        for voice in voices.values():
            click.echo(f"ID: {voice.voice_id}")
            click.echo(f"  Name: {voice.name}")
            click.echo(f"  Gender: {voice.gender}")
            click.echo(f"  Language: {voice.language}")
            click.echo(f"  Purpose: {voice.purpose}")
            click.echo(f"  Available: {voice.available}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audio.command()
@click.pass_context
def info(ctx):
    """Show audio system information."""
    config_path = ctx.parent.obj.get('config')
    
    try:
        app = App(config_path)
        app.initialize()
        
        # Get audio plugin
        audio_plugin = app.plugin_manager.get_plugin('audio')
        if not audio_plugin:
            click.echo("Audio plugin not loaded", err=True)
            return
        
        # Get engine info
        info = audio_plugin.audio_engine.get_engine_info()
        current_voice = audio_plugin.audio_engine.current_voice
        
        click.echo("VPA Audio System Information")
        click.echo("=" * 40)
        click.echo(f"Engine: {info['engine']}")
        click.echo(f"Version: {info.get('version', 'unknown')}")
        click.echo(f"Available Voices: {info['voices_available']}")
        click.echo(f"Currently Speaking: {info['is_speaking']}")
        
        if current_voice:
            click.echo(f"\nCurrent Voice:")
            click.echo(f"  Name: {current_voice.name}")
            click.echo(f"  Gender: {current_voice.gender}")
            click.echo(f"  Rate: {current_voice.rate} WPM")
            click.echo(f"  Volume: {int(current_voice.volume * 100)}%")
            click.echo(f"  Purpose: {current_voice.purpose}")
        else:
            click.echo("\nNo voice currently selected")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
