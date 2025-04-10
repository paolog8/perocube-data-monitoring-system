#!/usr/bin/env python3
"""
Configuration handling for the Perocube data monitoring system.

This module provides configuration loading and access functions for the application.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path)

class Config:
    """
    Configuration handler for the Perocube data monitoring system.
    
    This class loads configuration from a YAML file and provides access to
    configuration values through attribute access or dictionary-like access.
    Environment variables take precedence over YAML config values.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration handler.
        
        Parameters:
        -----------
        config_file : str, optional
            Path to the configuration file. If not provided, will look for
            'app_config.yaml' in the config directory.
        """
        self._config = {}
        
        # If config_file is not provided, use the default location
        if config_file is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            config_file = str(project_root / 'config' / 'app_config.yaml')
            
        self.load_config(config_file)
        self._apply_environment_overrides()
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from a YAML file.
        
        Parameters:
        -----------
        config_file : str
            Path to the configuration file.
            
        Returns:
        --------
        bool
            True if the configuration was loaded successfully, False otherwise.
        """
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def _apply_environment_overrides(self):
        """
        Apply environment variable overrides to the configuration.
        
        Environment variables take precedence over configuration values.
        Looks for specific environment variables that map to configuration settings.
        """
        # Database configuration overrides
        if 'database' not in self._config:
            self._config['database'] = {}
            
        # Override database settings from environment variables if they exist
        db_settings = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        # Only override if the environment variable is set
        for key, value in db_settings.items():
            if value is not None:
                if key == 'port' and value.isdigit():
                    self._config['database'][key] = int(value)
                else:
                    self._config['database'][key] = value
                logger.debug(f"Override config from environment: database.{key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Parameters:
        -----------
        key : str
            The configuration key. Can be a dotted path (e.g., 'database.host').
        default : Any, optional
            The default value to return if the key is not found.
            
        Returns:
        --------
        Any
            The configuration value, or the default if not found.
        """
        # Handle dotted paths
        if '.' in key:
            parts = key.split('.')
            value = self._config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        else:
            return self._config.get(key, default)
    
    def __getattr__(self, key: str) -> Any:
        """
        Get a configuration value by attribute access.
        
        Parameters:
        -----------
        key : str
            The configuration key.
            
        Returns:
        --------
        Any
            The configuration value.
            
        Raises:
        -------
        AttributeError
            If the key is not found in the configuration.
        """
        if key in self._config:
            return self._config[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value by dictionary-like access.
        
        Parameters:
        -----------
        key : str
            The configuration key.
            
        Returns:
        --------
        Any
            The configuration value.
            
        Raises:
        -------
        KeyError
            If the key is not found in the configuration.
        """
        if key in self._config:
            return self._config[key]
        raise KeyError(key)
        
    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the configuration.
        
        Parameters:
        -----------
        key : str
            The configuration key.
            
        Returns:
        --------
        bool
            True if the key exists, False otherwise.
        """
        return key in self._config

# Create a default configuration instance
config = Config()