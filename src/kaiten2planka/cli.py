"""Command-line interface for kaiten2planka."""

import click
import yaml
import os
from pathlib import Path
from typing import Dict, Any

from .migration.engine import MigrationEngine
from .utils.logging import setup_logging


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


@click.group()
@click.option('--config', '-c', default='config.yaml', help='Path to config file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx: click.Context, config: str, verbose: bool) -> None:
    """Kaiten to Planka migration tool."""
    # Load configuration
    config_path = Path(config)
    if not config_path.exists():
        raise click.ClickException(f"Config file not found: {config_path}")
    
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config_path)
    
    # Set up logging
    log_level = 'DEBUG' if verbose else ctx.obj['config'].get('logging', {}).get('level', 'INFO')
    log_file = ctx.obj['config'].get('logging', {}).get('file')
    setup_logging(log_level=log_level, log_file=log_file)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Run without making any changes')
@click.option('--force', is_flag=True, help='Force re-migrate existing data')
@click.pass_context
def migrate(ctx: click.Context, dry_run: bool, force: bool) -> None:
    """Migrate data from Kaiten to Planka."""
    config = ctx.obj['config']
    
    # Override config with CLI options
    if dry_run:
        config['migration']['dry_run'] = True
    if force:
        config['migration']['force'] = True
    
    # Initialize and run migration engine
    engine = MigrationEngine(config)
    try:
        engine.run()
    except Exception as e:
        click.echo(f"Migration failed: {e}", err=True)
        raise click.Abort()


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
