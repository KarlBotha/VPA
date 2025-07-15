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


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
