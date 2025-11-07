"""
Configuration Manager Module
Manages configuration and validation
"""
import os
import argparse
from dataclasses import dataclass
from typing import Optional
from .utils import ConfigValidationError


@dataclass
class TransferConfig:
    """Transfer configuration with all parameters"""
    source_host: str
    source_user: str
    source_pass: str
    dest_host: str
    dest_user: str
    dest_pass: str
    folder: Optional[str] = None
    port: int = 993
    timeout: int = 60
    retry_count: int = 3
    retry_delay: int = 5
    log_file: str = "transfer.log"
    cache_db: str = "transfer_cache.db"
    max_message_size: int = 52428800  # 50MB in bytes



def validate_config(config: TransferConfig) -> bool:
    """
    Validates the transfer configuration
    
    Args:
        config: TransferConfig instance to validate
        
    Returns:
        True if valid
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Check required fields (folder is optional for auto-mode)
    required_fields = [
        ('source_host', config.source_host),
        ('source_user', config.source_user),
        ('source_pass', config.source_pass),
        ('dest_host', config.dest_host),
        ('dest_user', config.dest_user),
        ('dest_pass', config.dest_pass),
    ]
    
    for field_name, field_value in required_fields:
        if not field_value or not str(field_value).strip():
            raise ConfigValidationError(f"Required field '{field_name}' is missing or empty")
    
    # Validate port number
    if not isinstance(config.port, int) or config.port < 1 or config.port > 65535:
        raise ConfigValidationError(f"Invalid port number: {config.port}. Must be between 1 and 65535")
    
    # Validate timeout
    if not isinstance(config.timeout, int) or config.timeout < 1:
        raise ConfigValidationError(f"Invalid timeout: {config.timeout}. Must be a positive integer")
    
    # Validate retry count
    if not isinstance(config.retry_count, int) or config.retry_count < 0:
        raise ConfigValidationError(f"Invalid retry_count: {config.retry_count}. Must be a non-negative integer")
    
    # Validate retry delay
    if not isinstance(config.retry_delay, int) or config.retry_delay < 0:
        raise ConfigValidationError(f"Invalid retry_delay: {config.retry_delay}. Must be a non-negative integer")
    
    # Validate max message size
    if not isinstance(config.max_message_size, int) or config.max_message_size < 1:
        raise ConfigValidationError(f"Invalid max_message_size: {config.max_message_size}. Must be a positive integer")
    
    return True



def load_config_from_args(args: argparse.Namespace) -> TransferConfig:
    """
    Creates TransferConfig from parsed command-line arguments
    Supports environment variables for passwords (SOURCE_PASS, DEST_PASS)
    
    Args:
        args: Parsed argparse.Namespace
        
    Returns:
        TransferConfig instance
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Get passwords from args or environment variables
    source_pass = args.source_pass if hasattr(args, 'source_pass') and args.source_pass else os.environ.get('SOURCE_PASS', '')
    dest_pass = args.dest_pass if hasattr(args, 'dest_pass') and args.dest_pass else os.environ.get('DEST_PASS', '')
    
    # Create config with required fields
    config = TransferConfig(
        source_host=getattr(args, 'source_host', ''),
        source_user=getattr(args, 'source_user', ''),
        source_pass=source_pass,
        dest_host=getattr(args, 'dest_host', ''),
        dest_user=getattr(args, 'dest_user', ''),
        dest_pass=dest_pass,
        folder=getattr(args, 'folder', None),
        port=getattr(args, 'port', 993),
        timeout=getattr(args, 'timeout', 60),
        retry_count=getattr(args, 'retry_count', 3),
        retry_delay=getattr(args, 'retry_delay', 5),
        log_file=getattr(args, 'log_file', 'transfer.log'),
        cache_db=getattr(args, 'cache_db', 'transfer_cache.db'),
        max_message_size=getattr(args, 'max_message_size', 52428800)
    )
    
    # Validate the configuration
    validate_config(config)
    
    return config
