#!/usr/bin/env python3
"""
IMAP Mail Transfer Tool - Main Entry Point
"""
import argparse
import logging
import signal
import sys
from typing import Optional

from .config import load_config_from_args, TransferConfig
from .cache import CacheManager
from .imap_client import IMAPClient
from .transfer import TransferEngine
from .auto_transfer import AutoTransferEngine
from .utils import (
    IMAPTransferError, IMAPConnectionError, IMAPFolderError,
    ConfigValidationError, format_size
)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments as argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='IMAP Mail Transfer Tool - Transfer emails between IMAP servers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transfer
  %(prog)s --source-host imap.source.com --source-user user@source.com \\
           --dest-host imap.dest.com --dest-user user@dest.com --folder INBOX

  # Using environment variables for passwords
  export SOURCE_PASS=secret1
  export DEST_PASS=secret2
  %(prog)s --source-host imap.source.com --source-user user@source.com \\
           --dest-host imap.dest.com --dest-user user@dest.com --folder INBOX

  # With custom settings
  %(prog)s --source-host imap.source.com --source-user user@source.com \\
           --source-pass secret1 --dest-host imap.dest.com \\
           --dest-user user@dest.com --dest-pass secret2 \\
           --folder INBOX --port 993 --timeout 120 --retry-count 5
        """
    )
    
    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--source-host',
        required=True,
        help='Source IMAP server hostname'
    )
    required.add_argument(
        '--source-user',
        required=True,
        help='Source IMAP server username'
    )
    required.add_argument(
        '--dest-host',
        required=True,
        help='Destination IMAP server hostname'
    )
    required.add_argument(
        '--dest-user',
        required=True,
        help='Destination IMAP server username'
    )
    required.add_argument(
        '--folder',
        required=False,
        help='Folder name to transfer (e.g., INBOX). Omit to use --auto-mode'
    )
    
    # Optional password arguments
    parser.add_argument(
        '--source-pass',
        help='Source IMAP server password (or use SOURCE_PASS env variable)'
    )
    parser.add_argument(
        '--dest-pass',
        help='Destination IMAP server password (or use DEST_PASS env variable)'
    )
    
    # Optional configuration arguments
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument(
        '--port',
        type=int,
        default=993,
        help='IMAP port (default: 993 for SSL)'
    )
    optional.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Connection timeout in seconds (default: 60)'
    )
    optional.add_argument(
        '--retry-count',
        type=int,
        default=3,
        help='Number of retry attempts for network errors (default: 3)'
    )
    optional.add_argument(
        '--retry-delay',
        type=int,
        default=5,
        help='Initial delay between retries in seconds (default: 5)'
    )
    optional.add_argument(
        '--log-file',
        default='transfer.log',
        help='Log file path (default: transfer.log)'
    )
    optional.add_argument(
        '--cache-db',
        default='transfer_cache.db',
        help='Cache database path (default: transfer_cache.db)'
    )
    optional.add_argument(
        '--max-message-size',
        type=int,
        default=52428800,
        help='Maximum message size in bytes (default: 52428800 = 50MB)'
    )
    optional.add_argument(
        '--auto-mode',
        action='store_true',
        help='Automatically discover and transfer all folders from source server'
    )
    
    return parser.parse_args()


def setup_logging(log_file: str) -> logging.Logger:
    """
    Configure Python logging with file and console handlers
    
    Args:
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('IMAPTransfer')
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    # Format: [TIMESTAMP] [LEVEL] [COMPONENT] Message
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    
    # File handler - DEBUG level for detailed logs
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file '{log_file}': {e}", file=sys.stderr)
    
    # Console handler - INFO level for user-facing messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global references for signal handling
_cache_manager: Optional[CacheManager] = None
_source_client: Optional[IMAPClient] = None
_dest_client: Optional[IMAPClient] = None
_logger: Optional[logging.Logger] = None


def signal_handler(signum: int, frame) -> None:
    """
    Handle interrupt signals (SIGINT, SIGTERM) for graceful shutdown
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global _logger
    
    signal_name = signal.Signals(signum).name
    if _logger:
        _logger.warning(f"\nReceived {signal_name} signal, shutting down gracefully...")
    else:
        print(f"\nReceived {signal_name} signal, shutting down gracefully...", file=sys.stderr)
    
    # Clean up resources
    cleanup_resources()
    
    # Exit with appropriate code
    sys.exit(128 + signum)


def cleanup_resources() -> None:
    """
    Clean up resources (close connections and cache)
    Called during normal exit or signal handling
    """
    global _cache_manager, _source_client, _dest_client, _logger
    
    if _logger:
        _logger.info("Cleaning up resources...")
    
    # Disconnect IMAP clients
    if _source_client:
        try:
            _source_client.disconnect()
            if _logger:
                _logger.debug("Source IMAP connection closed")
        except Exception as e:
            if _logger:
                _logger.warning(f"Error closing source connection: {e}")
    
    if _dest_client:
        try:
            _dest_client.disconnect()
            if _logger:
                _logger.debug("Destination IMAP connection closed")
        except Exception as e:
            if _logger:
                _logger.warning(f"Error closing destination connection: {e}")
    
    # Close cache database
    if _cache_manager:
        try:
            _cache_manager.close()
            if _logger:
                _logger.debug("Cache database closed")
        except Exception as e:
            if _logger:
                _logger.warning(f"Error closing cache: {e}")


def main() -> int:
    """
    Main orchestration function
    Coordinates all components and manages the transfer process
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    global _cache_manager, _source_client, _dest_client, _logger
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Setup logging
        _logger = setup_logging(args.log_file)
        _logger.info("=" * 60)
        _logger.info("IMAP Mail Transfer Tool")
        _logger.info("=" * 60)
        
        # Check if auto-mode or single folder mode
        auto_mode = getattr(args, 'auto_mode', False)
        
        # Validate folder requirement
        if not auto_mode and not getattr(args, 'folder', None):
            _logger.error("Error: --folder is required unless --auto-mode is specified")
            _logger.info("Use --auto-mode to automatically transfer all folders")
            return 1
        
        # Load and validate configuration
        _logger.info("Loading configuration...")
        try:
            config = load_config_from_args(args)
            _logger.debug(f"Configuration loaded: {config.source_host} -> {config.dest_host}")
            if auto_mode:
                _logger.info("Mode: AUTOMATIC (all folders)")
            else:
                _logger.info(f"Mode: SINGLE FOLDER ({config.folder})")
        except ConfigValidationError as e:
            _logger.error(f"Configuration validation failed: {e}")
            return 1
        
        # Initialize cache manager
        _logger.info(f"Initializing cache database: {config.cache_db}")
        try:
            _cache_manager = CacheManager(config.cache_db)
            _cache_manager.initialize()
            _logger.debug("Cache database initialized")
        except Exception as e:
            _logger.error(f"Failed to initialize cache database: {e}")
            cleanup_resources()
            return 1
        
        # Create IMAP clients
        _logger.info("Creating IMAP client connections...")
        _source_client = IMAPClient(
            host=config.source_host,
            username=config.source_user,
            password=config.source_pass,
            port=config.port
        )
        _dest_client = IMAPClient(
            host=config.dest_host,
            username=config.dest_user,
            password=config.dest_pass,
            port=config.port
        )
        
        # Connect to source server
        _logger.info(f"Connecting to source server: {config.source_host}:{config.port}")
        try:
            _source_client.connect()
            _logger.info("✓ Connected to source server")
        except IMAPConnectionError as e:
            _logger.error(f"Failed to connect to source server: {e}")
            cleanup_resources()
            return 1
        
        # Connect to destination server
        _logger.info(f"Connecting to destination server: {config.dest_host}:{config.port}")
        try:
            _dest_client.connect()
            _logger.info("✓ Connected to destination server")
        except IMAPConnectionError as e:
            _logger.error(f"Failed to connect to destination server: {e}")
            cleanup_resources()
            return 1
        
        # AUTO-MODE: Transfer all folders automatically
        if auto_mode:
            _logger.info("")
            _logger.info("=" * 60)
            _logger.info("AUTOMATIC MULTI-FOLDER TRANSFER MODE")
            _logger.info("=" * 60)
            _logger.info("This will automatically discover and transfer ALL folders")
            _logger.info("from source to destination server.")
            _logger.info("=" * 60)
            _logger.info("")
            
            # Create auto transfer engine
            auto_engine = AutoTransferEngine(
                source_client=_source_client,
                dest_client=_dest_client,
                cache_manager=_cache_manager,
                logger=_logger,
                max_message_size=config.max_message_size,
                retry_count=config.retry_count,
                retry_delay=config.retry_delay
            )
            
            # Transfer all folders
            results = auto_engine.transfer_all_folders()
            
            # Clean up resources
            cleanup_resources()
            
            # Return appropriate exit code
            failed_folders = sum(1 for r in results.values() if not r.success)
            if failed_folders > 0:
                _logger.warning(f"Transfer completed with {failed_folders} failed folders")
                return 1
            else:
                _logger.info("All folders transferred successfully")
                return 0
        
        # SINGLE FOLDER MODE: Transfer specific folder
        _logger.info(f"Verifying source folder: {config.folder}")
        try:
            if not _source_client.folder_exists(config.folder):
                _logger.error(f"Source folder '{config.folder}' does not exist")
                _logger.info("")
                _logger.info("=" * 60)
                _logger.info("AVAILABLE FOLDERS ON SOURCE SERVER:")
                _logger.info("=" * 60)
                
                try:
                    available_folders = _source_client.list_folders()
                    if available_folders:
                        for idx, folder_name in enumerate(available_folders, 1):
                            _logger.info(f"  {idx}. {folder_name}")
                        _logger.info("")
                        _logger.info("=" * 60)
                        _logger.info("PLEASE UPDATE YOUR CONFIGURATION:")
                        _logger.info("=" * 60)
                        _logger.info(f"Edit 'run_transfer.sh' and change:")
                        _logger.info(f'  FOLDER="{config.folder}"')
                        _logger.info(f"to one of the folders listed above.")
                        _logger.info("")
                        _logger.info("Common folder names:")
                        _logger.info("  - INBOX (English)")
                        _logger.info("  - Inbox (some servers)")
                        _logger.info("  - Sent (Sent messages)")
                        _logger.info("  - Drafts (Draft messages)")
                        _logger.info("=" * 60)
                    else:
                        _logger.error("Could not retrieve folder list from server")
                except Exception as e:
                    _logger.error(f"Error listing folders: {e}")
                
                cleanup_resources()
                return 1
            
            # Select source folder to get message count
            message_count = _source_client.select_folder(config.folder)
            _logger.info(f"✓ Source folder exists with {message_count} messages")
        except IMAPFolderError as e:
            _logger.error(f"Error accessing source folder: {e}")
            cleanup_resources()
            return 1
        
        # Create destination folder if needed
        _logger.info(f"Checking destination folder: {config.folder}")
        try:
            if not _dest_client.folder_exists(config.folder):
                _logger.info(f"Creating destination folder: {config.folder}")
                _dest_client.create_folder(config.folder)
                _logger.info("✓ Destination folder created")
            else:
                _logger.info("✓ Destination folder exists")
            
            # Select destination folder
            _dest_client.select_folder(config.folder)
        except IMAPFolderError as e:
            _logger.error(f"Error with destination folder: {e}")
            cleanup_resources()
            return 1
        
        # Create transfer engine
        _logger.info("Initializing transfer engine...")
        transfer_engine = TransferEngine(
            source_client=_source_client,
            dest_client=_dest_client,
            cache_manager=_cache_manager,
            logger=_logger,
            max_message_size=config.max_message_size,
            retry_count=config.retry_count,
            retry_delay=config.retry_delay
        )
        
        # Start transfer
        _logger.info("")
        _logger.info("Starting transfer process...")
        _logger.info("-" * 60)
        
        result = transfer_engine.transfer_folder(config.folder)
        
        # Display final statistics
        _logger.info("-" * 60)
        _logger.info("Transfer Complete!")
        _logger.info("=" * 60)
        _logger.info(f"Total messages:      {result.total_messages}")
        _logger.info(f"Transferred:         {result.transferred}")
        _logger.info(f"Skipped (cached):    {result.skipped}")
        _logger.info(f"Failed:              {result.failed}")
        _logger.info(f"Total size:          {format_size(result.total_size)}")
        _logger.info(f"Duration:            {result.duration_seconds:.1f} seconds")
        
        if result.transferred > 0:
            rate = result.transferred / result.duration_seconds
            _logger.info(f"Transfer rate:       {rate:.1f} messages/second")
        
        _logger.info("=" * 60)
        
        # Display final error summary if any
        if result.errors:
            _logger.warning("")
            _logger.warning("=" * 60)
            _logger.warning("ERROR SUMMARY")
            _logger.warning("=" * 60)
            _logger.warning(f"Total errors encountered: {len(result.errors)}")
            _logger.warning("")
            _logger.warning("Error details:")
            for error in result.errors[:10]:  # Show first 10 errors
                _logger.warning(f"  - {error}")
            if len(result.errors) > 10:
                _logger.warning(f"  ... and {len(result.errors) - 10} more errors")
            _logger.warning("")
            _logger.warning(f"Full error log available in: {config.log_file}")
            _logger.warning("=" * 60)
        
        # Clean up resources
        cleanup_resources()
        
        # Return appropriate exit code
        if result.failed > 0:
            _logger.warning("Transfer completed with errors")
            return 1
        else:
            _logger.info("Transfer completed successfully")
            return 0
        
    except KeyboardInterrupt:
        if _logger:
            _logger.warning("\nTransfer interrupted by user")
        cleanup_resources()
        return 130  # Standard exit code for SIGINT
        
    except Exception as e:
        if _logger:
            _logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        cleanup_resources()
        return 1


if __name__ == "__main__":
    sys.exit(main())
