"""Configuration management."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
from pydantic import BaseSettings, Field


class KaitenSettings(BaseSettings):
    """Kaiten API settings."""
    api_url: str = Field(..., env='KAITEN_API_URL')
    api_key: str = Field(..., env='KAITEN_API_KEY')
    
    class Config:
        env_prefix = 'KAITEN_'


class PlankaSettings(BaseSettings):
    """Planka API settings."""
    api_url: str = Field(..., env='PLANKA_API_URL') 
    api_key: str = Field(..., env='PLANKA_API_KEY')
    
    class Config:
        env_prefix = 'PLANKA_'


class MigrationSettings(BaseSettings):
    """Migration process settings."""
    workers: int = Field(5, env='MIGRATION_WORKERS')
    rate_limit_rps: int = Field(10, env='MIGRATION_RATE_LIMIT_RPS')
    retry_max_attempts: int = Field(5, env='MIGRATION_RETRY_MAX_ATTEMPTS')
    retry_backoff_factor: float = Field(2.0, env='MIGRATION_RETRY_BACKOFF_FACTOR')
    attachment_chunk_size: int = Field(8192, env='MIGRATION_ATTACHMENT_CHUNK_SIZE')
    dry_run: bool = Field(False, env='MIGRATION_DRY_RUN')
    force: bool = Field(False, env='MIGRATION_FORCE')
    
    class Config:
        env_prefix = 'MIGRATION_'


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    level: str = Field('INFO', env='LOG_LEVEL')
    format: str = Field('json', env='LOG_FORMAT')
    file: Optional[str] = Field(None, env='LOG_FILE')
    
    class Config:
        env_prefix = 'LOG_'


class DatabaseSettings(BaseSettings):
    """Database settings."""
    path: str = Field('migrations.db', env='DATABASE_PATH')
    
    class Config:
        env_prefix = 'DATABASE_'


@dataclass
class Settings:
    """Complete application settings."""
    kaiten: KaitenSettings
    planka: PlankaSettings
    migration: MigrationSettings
    logging: LoggingSettings
    database: DatabaseSettings


def load_config(config_path: str) -> Settings:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Loaded settings
    """
    # Load YAML config
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file) as f:
            yaml_config = yaml.safe_load(f)
    else:
        yaml_config = {}
    
    # Override with environment variables
    def _get_section(section_name: str) -> Dict[str, Any]:
        section = yaml_config.get(section_name, {})
        # Expand environment variables in values
        for key, value in section.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                section[key] = os.getenv(env_var, value)
        return section
    
    return Settings(
        kaiten=KaitenSettings(**_get_section('kaiten')),
        planka=PlankaSettings(**_get_section('planka')),
        migration=MigrationSettings(**_get_section('migration')),
        logging=LoggingSettings(**_get_section('logging')),
        database=DatabaseSettings(**_get_section('database'))
    )
