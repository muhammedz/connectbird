#!/usr/bin/env python3
"""
Automatic Multi-Folder Transfer
Automatically discovers and transfers all folders from source to destination
"""
import logging
import sys
from typing import List, Dict
from dataclasses import dataclass

from .imap_client import IMAPClient
from .cache import CacheManager
from .transfer import TransferEngine, TransferResult
from .utils import IMAPFolderError


@dataclass
class FolderTransferResult:
    """Result for a single folder transfer"""
    folder_name: str
    success: bool
    result: TransferResult = None
    error: str = None


class AutoTransferEngine:
    """
    Automatic transfer engine that discovers and transfers all folders
    """
    
    def __init__(self, source_client: IMAPClient, dest_client: IMAPClient,
                 cache_manager: CacheManager, logger: logging.Logger,
                 max_message_size: int = 52428800, retry_count: int = 3,
                 retry_delay: int = 5):
        """
        Initialize AutoTransferEngine
        
        Args:
            source_client: Source IMAP client
            dest_client: Destination IMAP client
            cache_manager: Cache manager
            logger: Logger instance
            max_message_size: Maximum message size in bytes
            retry_count: Number of retry attempts
            retry_delay: Delay between retries
        """
        self.source_client = source_client
        self.dest_client = dest_client
        self.cache_manager = cache_manager
        self.logger = logger
        self.max_message_size = max_message_size
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        # Folders to skip (system folders that shouldn't be transferred)
        self.skip_folders = [
            '[Gmail]',  # Gmail system folder
            'Notes',    # Apple Notes
            'Contacts', # Contacts folder
        ]
    
    def should_skip_folder(self, folder_name: str) -> bool:
        """
        Check if folder should be skipped
        
        Args:
            folder_name: Folder name to check
            
        Returns:
            True if folder should be skipped
        """
        # Skip empty or invalid folder names
        if not folder_name or folder_name.strip() == '':
            return True
        
        # Skip folders with only special characters
        if folder_name in ['|', '/', '.', '..']:
            return True
        
        # Skip if folder name contains any skip pattern
        for skip_pattern in self.skip_folders:
            if skip_pattern in folder_name:
                return True
        
        return False
    
    def discover_folders(self) -> List[str]:
        """
        Discover all folders from source server
        
        Returns:
            List of folder names to transfer
        """
        self.logger.info("Discovering folders on source server...")
        
        try:
            all_folders = self.source_client.list_folders()
            
            # Filter out folders to skip
            folders_to_transfer = [
                folder for folder in all_folders 
                if not self.should_skip_folder(folder)
            ]
            
            self.logger.info(f"Found {len(all_folders)} total folders")
            self.logger.info(f"Will transfer {len(folders_to_transfer)} folders")
            
            if len(all_folders) != len(folders_to_transfer):
                skipped = len(all_folders) - len(folders_to_transfer)
                self.logger.info(f"Skipping {skipped} system folders")
            
            return folders_to_transfer
            
        except Exception as e:
            self.logger.error(f"Error discovering folders: {e}")
            return []
    
    def normalize_folder_name(self, folder_name: str, for_destination: bool = False) -> str:
        """
        Normalize folder name for destination server
        Some servers (like Connect365) require INBOX. prefix for subfolders
        
        Args:
            folder_name: Original folder name
            for_destination: If True, add INBOX. prefix if needed
            
        Returns:
            Normalized folder name
        """
        # INBOX never needs prefix
        if folder_name == 'INBOX':
            return folder_name
        
        # For destination, try with INBOX. prefix for all non-INBOX folders
        # Connect365 seems to require this for all folders
        if for_destination and not folder_name.startswith('INBOX.'):
            return f"INBOX.{folder_name}"
        
        return folder_name
    
    def ensure_destination_folder(self, folder_name: str) -> bool:
        """
        Ensure folder exists on destination server, create if needed
        
        Args:
            folder_name: Folder name to ensure
            
        Returns:
            True if folder exists or was created successfully
        """
        try:
            # Normalize folder name for destination
            dest_folder_name = self.normalize_folder_name(folder_name, for_destination=True)
            
            if not self.dest_client.folder_exists(dest_folder_name):
                self.logger.info(f"Creating destination folder: {dest_folder_name}")
                self.dest_client.create_folder(dest_folder_name)
                self.logger.info(f"✓ Created folder: {dest_folder_name}")
            else:
                self.logger.debug(f"Destination folder already exists: {dest_folder_name}")
            
            return True
            
        except IMAPFolderError as e:
            error_str = str(e)
            # Check if folder already exists - this is OK!
            if 'ALREADYEXISTS' in error_str or 'already exists' in error_str.lower():
                self.logger.info(f"✓ Destination folder already exists: {dest_folder_name}")
                return True
            
            self.logger.error(f"Failed to create destination folder '{folder_name}': {e}")
            # Try without prefix as fallback
            try:
                if not self.dest_client.folder_exists(folder_name):
                    self.logger.info(f"Retrying without prefix: {folder_name}")
                    self.dest_client.create_folder(folder_name)
                    self.logger.info(f"✓ Created folder: {folder_name}")
                return True
            except Exception as e2:
                # Check again if already exists
                if 'ALREADYEXISTS' in str(e2) or 'already exists' in str(e2).lower():
                    self.logger.info(f"✓ Destination folder already exists: {folder_name}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Unexpected error ensuring folder '{folder_name}': {e}")
            return False
    
    def transfer_folder(self, folder_name: str) -> FolderTransferResult:
        """
        Transfer a single folder
        
        Args:
            folder_name: Folder name to transfer
            
        Returns:
            FolderTransferResult with transfer statistics
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(f"TRANSFERRING FOLDER: {folder_name}")
        self.logger.info("=" * 60)
        
        try:
            # Select source folder
            try:
                message_count = self.source_client.select_folder(folder_name)
                self.logger.info(f"Source folder has {message_count} messages")
            except IMAPFolderError as e:
                error_msg = f"Failed to select source folder: {e}"
                self.logger.error(error_msg)
                return FolderTransferResult(
                    folder_name=folder_name,
                    success=False,
                    error=error_msg
                )
            
            # Ensure destination folder exists
            if not self.ensure_destination_folder(folder_name):
                error_msg = f"Failed to create destination folder"
                return FolderTransferResult(
                    folder_name=folder_name,
                    success=False,
                    error=error_msg
                )
            
            # Select destination folder (with normalized name)
            try:
                dest_folder_name = self.normalize_folder_name(folder_name, for_destination=True)
                try:
                    self.dest_client.select_folder(dest_folder_name)
                except IMAPFolderError:
                    # If selection fails, try without prefix
                    self.logger.debug(f"Failed to select with prefix, trying without: {folder_name}")
                    self.dest_client.select_folder(folder_name)
                    dest_folder_name = folder_name  # Use folder name without prefix for transfer
            except IMAPFolderError as e:
                error_msg = f"Failed to select destination folder: {e}"
                self.logger.error(error_msg)
                return FolderTransferResult(
                    folder_name=folder_name,
                    success=False,
                    error=error_msg
                )
            
            # Create transfer engine for this folder
            transfer_engine = TransferEngine(
                source_client=self.source_client,
                dest_client=self.dest_client,
                cache_manager=self.cache_manager,
                logger=self.logger,
                max_message_size=self.max_message_size,
                retry_count=self.retry_count,
                retry_delay=self.retry_delay
            )
            
            # Transfer messages (use normalized destination folder name)
            dest_folder_name = self.normalize_folder_name(folder_name, for_destination=True)
            result = transfer_engine.transfer_folder(folder_name, dest_folder_override=dest_folder_name)
            
            # Log folder summary
            self.logger.info("-" * 60)
            self.logger.info(f"Folder '{folder_name}' Complete:")
            self.logger.info(f"  Transferred: {result.transferred}")
            self.logger.info(f"  Skipped: {result.skipped}")
            self.logger.info(f"  Failed: {result.failed}")
            self.logger.info("-" * 60)
            
            return FolderTransferResult(
                folder_name=folder_name,
                success=(result.failed == 0),
                result=result
            )
            
        except KeyboardInterrupt:
            # Re-raise to allow graceful shutdown
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return FolderTransferResult(
                folder_name=folder_name,
                success=False,
                error=error_msg
            )
    
    def transfer_all_folders(self) -> Dict[str, FolderTransferResult]:
        """
        Discover and transfer all folders from source to destination
        
        Returns:
            Dictionary mapping folder names to their transfer results
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("AUTOMATIC MULTI-FOLDER TRANSFER")
        self.logger.info("=" * 60)
        
        # Discover folders
        folders = self.discover_folders()
        
        if not folders:
            self.logger.warning("No folders found to transfer")
            return {}
        
        # Display folders to be transferred
        self.logger.info("")
        self.logger.info("Folders to transfer:")
        for idx, folder in enumerate(folders, 1):
            self.logger.info(f"  {idx}. {folder}")
        self.logger.info("")
        
        # Transfer each folder
        results = {}
        
        for idx, folder in enumerate(folders, 1):
            self.logger.info(f"[{idx}/{len(folders)}] Processing folder: {folder}")
            
            try:
                result = self.transfer_folder(folder)
                results[folder] = result
                
            except KeyboardInterrupt:
                self.logger.warning(f"Transfer interrupted at folder '{folder}'")
                raise
            except Exception as e:
                self.logger.error(f"Critical error transferring folder '{folder}': {e}")
                results[folder] = FolderTransferResult(
                    folder_name=folder,
                    success=False,
                    error=str(e)
                )
                # Continue with next folder
                continue
        
        # Display final summary
        self.display_summary(results)
        
        return results
    
    def display_summary(self, results: Dict[str, FolderTransferResult]) -> None:
        """
        Display final transfer summary for all folders
        
        Args:
            results: Dictionary of folder transfer results
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("FINAL TRANSFER SUMMARY")
        self.logger.info("=" * 60)
        
        total_transferred = 0
        total_skipped = 0
        total_failed = 0
        total_size = 0
        successful_folders = 0
        failed_folders = 0
        
        for folder_name, result in results.items():
            if result.success and result.result:
                successful_folders += 1
                total_transferred += result.result.transferred
                total_skipped += result.result.skipped
                total_failed += result.result.failed
                total_size += result.result.total_size
            else:
                failed_folders += 1
        
        self.logger.info(f"Total folders processed: {len(results)}")
        self.logger.info(f"  Successful: {successful_folders}")
        self.logger.info(f"  Failed: {failed_folders}")
        self.logger.info("")
        self.logger.info(f"Total messages transferred: {total_transferred}")
        self.logger.info(f"Total messages skipped: {total_skipped}")
        self.logger.info(f"Total messages failed: {total_failed}")
        
        if total_size > 0:
            from .utils import format_size
            self.logger.info(f"Total data transferred: {format_size(total_size)}")
        
        # Display per-folder summary
        if results:
            self.logger.info("")
            self.logger.info("Per-folder summary:")
            self.logger.info("-" * 60)
            
            for folder_name, result in results.items():
                if result.success and result.result:
                    status = "✓"
                    details = f"{result.result.transferred} transferred, {result.result.skipped} skipped, {result.result.failed} failed"
                else:
                    status = "✗"
                    details = result.error if result.error else "Unknown error"
                
                self.logger.info(f"{status} {folder_name}: {details}")
        
        self.logger.info("=" * 60)
