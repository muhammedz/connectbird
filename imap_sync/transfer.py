"""
Transfer Engine Module
Manages message transfer logic and streaming control
"""

import gc
import logging
import time
from typing import List, Optional
from dataclasses import dataclass
from tqdm import tqdm

from .imap_client import IMAPClient
from .cache import CacheManager
from .utils import RetryHandler, format_size, IMAPFetchError, IMAPAppendError


@dataclass
class TransferResult:
    """Transfer result statistics"""
    total_messages: int
    transferred: int
    skipped: int
    failed: int
    total_size: int
    duration_seconds: float
    errors: List[str]


class TransferEngine:
    """
    Transfer engine for managing message transfer between IMAP servers
    Implements streaming transfer with memory management
    """
    
    def __init__(self, source_client: IMAPClient, dest_client: IMAPClient,
                 cache_manager: CacheManager, logger: logging.Logger,
                 max_message_size: int = 52428800, retry_count: int = 3,
                 retry_delay: int = 5):
        """
        Initialize TransferEngine with dependencies
        
        Args:
            source_client: Source IMAP client
            dest_client: Destination IMAP client
            cache_manager: Cache manager for duplicate detection
            logger: Logger instance
            max_message_size: Maximum message size in bytes (default: 50MB)
            retry_count: Number of retry attempts for network errors
            retry_delay: Initial delay between retries in seconds
        """
        self.source_client = source_client
        self.dest_client = dest_client
        self.cache_manager = cache_manager
        self.logger = logger
        self.max_message_size = max_message_size
        self.retry_handler = RetryHandler(max_retries=retry_count, delay=retry_delay, logger=logger)
        self._message_data = None  # For cleanup tracking
    
    def _get_untransferred_uids(self, source_uids: List[str], folder: str) -> List[str]:
        """
        Filter out already transferred messages by comparing with cache
        
        Args:
            source_uids: List of UIDs from source server
            folder: Folder name
            
        Returns:
            List of UIDs that need to be transferred
        """
        self.logger.debug(f"Filtering {len(source_uids)} UIDs against cache for folder '{folder}'")
        
        # Get already transferred UIDs from cache
        transferred_uids = set(self.cache_manager.get_transferred_uids(folder))
        
        # Filter out transferred UIDs
        untransferred = [uid for uid in source_uids if uid not in transferred_uids]
        
        self.logger.info(
            f"Found {len(untransferred)} untransferred messages "
            f"({len(transferred_uids)} already transferred)"
        )
        
        return untransferred
    
    def _cleanup_message(self) -> None:
        """
        Release message data from memory and invoke garbage collection
        Ensures memory is freed after each message transfer
        """
        # Delete message data reference
        if self._message_data is not None:
            del self._message_data
            self._message_data = None
        
        # Force garbage collection
        gc.collect()
    
    def _update_progress(self, progress_bar: tqdm, current: int, total: int,
                        uid: str, status: str) -> None:
        """
        Update progress bar with current transfer status
        
        Args:
            progress_bar: tqdm progress bar instance
            current: Current message number
            total: Total message count
            uid: Current message UID
            status: Status message
        """
        progress_bar.set_description(f"UID {uid}: {status}")
        progress_bar.update(1)
    
    def _transfer_single_message(self, uid: str, folder: str, dest_folder: str,
                                 progress_bar: Optional[tqdm] = None) -> bool:
        """
        Transfer a single message from source to destination with streaming
        Implements retry logic and memory cleanup
        
        Args:
            uid: Message UID to transfer
            folder: Source folder name (for cache)
            dest_folder: Destination folder name (for append)
            progress_bar: Optional progress bar for updates
            
        Returns:
            True if transfer successful, False otherwise
        """
        try:
            # Fetch message from source with retry logic
            def fetch_operation():
                return self.source_client.fetch_message(uid)
            
            try:
                self.logger.debug(f"Fetching message UID {uid} from source server")
                message_data, date, flags = self.retry_handler.execute(fetch_operation)
            except IMAPFetchError as e:
                self.logger.error(
                    f"Failed to fetch message UID {uid} after {self.retry_handler.max_retries} retries: {str(e)}"
                )
                return False
            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching message UID {uid}: {str(e)}",
                    exc_info=True
                )
                return False
            
            # Store reference for cleanup
            self._message_data = message_data
            
            # Check message size
            message_size = len(message_data)
            self.logger.debug(f"Message UID {uid} size: {format_size(message_size)}")
            
            if message_size > self.max_message_size:
                self.logger.warning(
                    f"Skipping message UID {uid}: size {format_size(message_size)} "
                    f"exceeds limit {format_size(self.max_message_size)}"
                )
                self._cleanup_message()
                return False
            
            # Append message to destination with retry logic
            # Note: dest_folder is passed from transfer_folder method
            def append_operation():
                return self.dest_client.append_message(dest_folder, message_data, date, flags)
            
            try:
                self.logger.debug(f"Appending message UID {uid} to destination server")
                dest_uid = self.retry_handler.execute(append_operation)
            except IMAPAppendError as e:
                self.logger.error(
                    f"Failed to append message UID {uid} after {self.retry_handler.max_retries} retries: {str(e)}"
                )
                self._cleanup_message()
                return False
            except Exception as e:
                self.logger.error(
                    f"Unexpected error appending message UID {uid}: {str(e)}",
                    exc_info=True
                )
                self._cleanup_message()
                return False
            
            # Mark as transferred in cache
            try:
                self.cache_manager.mark_transferred(uid, dest_uid, folder, message_size)
            except Exception as e:
                self.logger.error(
                    f"Failed to mark message UID {uid} as transferred in cache: {str(e)}",
                    exc_info=True
                )
                # Continue anyway - message was transferred successfully
            
            # Log success
            self.logger.debug(
                f"Successfully transferred message UID {uid} -> {dest_uid} "
                f"({format_size(message_size)})"
            )
            
            # Cleanup memory
            self._cleanup_message()
            
            return True
            
        except Exception as e:
            # Catch any unexpected errors
            self.logger.error(
                f"Unexpected error transferring message UID {uid}: {str(e)}",
                exc_info=True
            )
            self._cleanup_message()
            return False
    
    def transfer_folder(self, folder: str, dest_folder_override: Optional[str] = None) -> TransferResult:
        """
        Transfer all untransferred messages from a folder
        Orchestrates the complete transfer process with progress tracking
        
        Args:
            folder: Folder name to transfer (source folder)
            dest_folder_override: Optional destination folder name (if different from source)
            
        Returns:
            TransferResult with statistics
        """
        start_time = time.time()
        
        # Use destination folder override if provided, otherwise use source folder name
        dest_folder = dest_folder_override if dest_folder_override else folder
        
        self.logger.info(f"Starting transfer for folder '{folder}'")
        
        # Initialize statistics
        total_messages = 0
        transferred = 0
        skipped = 0
        failed = 0
        total_size = 0
        errors = []
        
        try:
            # Get source UIDs
            self.logger.info("Retrieving message UIDs from source server...")
            try:
                source_uids = self.source_client.get_uid_list()
                total_messages = len(source_uids)
            except IMAPFetchError as e:
                error_msg = f"Failed to retrieve UIDs from source server: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return TransferResult(
                    total_messages=0,
                    transferred=0,
                    skipped=0,
                    failed=0,
                    total_size=0,
                    duration_seconds=time.time() - start_time,
                    errors=errors
                )
            except Exception as e:
                error_msg = f"Unexpected error retrieving UIDs: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                return TransferResult(
                    total_messages=0,
                    transferred=0,
                    skipped=0,
                    failed=0,
                    total_size=0,
                    duration_seconds=time.time() - start_time,
                    errors=errors
                )
            
            if total_messages == 0:
                self.logger.info(f"No messages found in folder '{folder}'")
                return TransferResult(
                    total_messages=0,
                    transferred=0,
                    skipped=0,
                    failed=0,
                    total_size=0,
                    duration_seconds=time.time() - start_time,
                    errors=[]
                )
            
            self.logger.info(f"Found {total_messages} messages in source folder")
            
            # Filter untransferred UIDs
            try:
                untransferred_uids = self._get_untransferred_uids(source_uids, folder)
                skipped = total_messages - len(untransferred_uids)
            except Exception as e:
                error_msg = f"Error filtering transferred UIDs: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                # Assume all need transfer if cache check fails
                untransferred_uids = source_uids
                skipped = 0
            
            if len(untransferred_uids) == 0:
                self.logger.info("All messages already transferred")
                return TransferResult(
                    total_messages=total_messages,
                    transferred=0,
                    skipped=skipped,
                    failed=0,
                    total_size=0,
                    duration_seconds=time.time() - start_time,
                    errors=[]
                )
            
            # Create progress bar
            self.logger.info(f"Transferring {len(untransferred_uids)} messages...")
            progress_bar = tqdm(
                total=len(untransferred_uids),
                desc="Transferring",
                unit="msg",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            )
            
            # Transfer each message
            for idx, uid in enumerate(untransferred_uids, 1):
                try:
                    # Update progress
                    self._update_progress(progress_bar, idx, len(untransferred_uids),
                                        uid, "transferring")
                    
                    # Transfer single message
                    success = self._transfer_single_message(uid, folder, dest_folder, progress_bar)
                    
                    if success:
                        transferred += 1
                        # Get message size from cache for statistics
                        try:
                            stats = self.cache_manager.get_statistics(folder)
                            total_size = stats.get('total_size', 0)
                        except Exception as e:
                            self.logger.warning(f"Failed to get statistics from cache: {str(e)}")
                    else:
                        failed += 1
                        error_msg = f"UID {uid}: Transfer failed"
                        errors.append(error_msg)
                        
                except KeyboardInterrupt:
                    # Re-raise keyboard interrupt to allow graceful shutdown
                    self.logger.warning(f"Transfer interrupted at message UID {uid}")
                    raise
                except Exception as e:
                    # Handle unexpected errors gracefully - don't crash, continue with next message
                    failed += 1
                    error_msg = f"UID {uid}: Unexpected error - {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    # Continue with next message
                    continue
            
            # Close progress bar
            progress_bar.close()
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log summary
            self.logger.info(
                f"Transfer complete: {transferred} transferred, "
                f"{skipped} skipped, {failed} failed "
                f"in {duration:.1f} seconds"
            )
            
            # Log final error summary
            if errors:
                self.logger.warning(f"Encountered {len(errors)} errors during transfer")
                self.logger.warning("Error summary:")
                for error in errors[:20]:  # Log first 20 errors
                    self.logger.warning(f"  - {error}")
                if len(errors) > 20:
                    self.logger.warning(f"  ... and {len(errors) - 20} more errors (see log file for details)")
            
            return TransferResult(
                total_messages=total_messages,
                transferred=transferred,
                skipped=skipped,
                failed=failed,
                total_size=total_size,
                duration_seconds=duration,
                errors=errors
            )
            
        except KeyboardInterrupt:
            # Re-raise to allow main to handle graceful shutdown
            raise
        except Exception as e:
            # Handle critical errors
            duration = time.time() - start_time
            error_msg = f"Critical error during transfer: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            
            return TransferResult(
                total_messages=total_messages,
                transferred=transferred,
                skipped=skipped,
                failed=failed,
                total_size=total_size,
                duration_seconds=duration,
                errors=errors
            )
