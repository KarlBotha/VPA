"""
Command Line Interface for VPA.
Provides CLI commands and delegates to the main App class.
"""

import click
import logging
import sys
from vpa.core.app import App


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_text_input(text: str) -> str:
    """Validate and sanitize text input."""
    if not text or not text.strip():
        raise click.BadParameter("Text cannot be empty")
    
    # Basic sanitization - remove potentially dangerous characters
    sanitized = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    if len(sanitized) > 1000:
        raise click.BadParameter("Text too long (max 1000 characters)")
    
    return sanitized.strip()


@click.group()
@click.option('--log-level', default='INFO', help='Set the logging level')
@click.option('--config', help='Path to configuration file')
@click.pass_context
def cli(ctx, log_level, config):
    """VPA - Virtual Personal Assistant CLI."""
    ctx.ensure_object(dict)
    ctx.obj['log_level'] = log_level
    ctx.obj['config'] = config
    setup_logging(log_level)


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
    click.echo("VPA Status: Not implemented yet")


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
            click.echo(f"  {key}: {value}")
            
    except Exception as e:
        click.echo(f"Error reading config: {e}", err=True)


# Audio commands group
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


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
