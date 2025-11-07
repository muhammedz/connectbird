"""
Utilities Module
Helper functions and classes
"""

import time
import re
from typing import Callable, Any
from datetime import datetime


# Custom Exception Hierarchy
class IMAPTransferError(Exception):
    """Base exception for all IMAP transfer errors"""
    pass


class IMAPConnectionError(IMAPTransferError):
    """Exception raised for IMAP connection failures"""
    pass


class IMAPFolderError(IMAPTransferError):
    """Exception raised for IMAP folder operation failures"""
    pass


class IMAPFetchError(IMAPTransferError):
    """Exception raised for IMAP message fetch failures"""
    pass


class IMAPAppendError(IMAPTransferError):
    """Exception raised for IMAP message append failures"""
    pass


class ConfigValidationError(IMAPTransferError):
    """Exception raised for configuration validation failures"""
    pass


# Utility Functions

def format_size(bytes: int) -> str:
    """
    Convert bytes to human-readable format (KB, MB, GB)
    
    Args:
        bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "500 KB")
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"


def parse_imap_date(date_str: str) -> str:
    """
    Parse and normalize IMAP date strings
    
    Args:
        date_str: IMAP date string (various formats)
        
    Returns:
        Normalized date string in format suitable for IMAP APPEND
    """
    if not date_str:
        return datetime.now().strftime("%d-%b-%Y %H:%M:%S %z")
    
    # If already in proper format, return as-is
    if re.match(r'\d{1,2}-[A-Za-z]{3}-\d{4}', date_str):
        return date_str
    
    # Try to parse common date formats
    try:
        # Try ISO format first
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d-%b-%Y %H:%M:%S %z")
    except (ValueError, AttributeError):
        pass
    
    try:
        # Try RFC 2822 format
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%d-%b-%Y %H:%M:%S %z")
    except (ValueError, TypeError, AttributeError):
        pass
    
    # If all parsing fails, return current time
    return datetime.now().strftime("%d-%b-%Y %H:%M:%S %z")


def sanitize_folder_name(folder: str) -> str:
    """
    Clean and sanitize folder names for IMAP compatibility
    
    Args:
        folder: Raw folder name
        
    Returns:
        Sanitized folder name
    """
    if not folder:
        return "INBOX"
    
    # Remove leading/trailing whitespace
    folder = folder.strip()
    
    # Replace problematic characters
    # IMAP folder names should avoid certain characters
    folder = re.sub(r'[<>:"|?*]', '_', folder)
    
    # Remove control characters
    folder = re.sub(r'[\x00-\x1f\x7f]', '', folder)
    
    # Collapse multiple spaces
    folder = re.sub(r'\s+', ' ', folder)
    
    # If empty after sanitization, return INBOX
    if not folder:
        return "INBOX"
    
    return folder


class RetryHandler:
    """
    Retry handler with exponential backoff for network operations
    """
    
    def __init__(self, max_retries: int = 3, delay: int = 5, logger=None):
        """
        Initialize retry handler
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay in seconds between retries
            logger: Optional logger for retry warnings
        """
        self.max_retries = max_retries
        self.delay = delay
        self.logger = logger
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic and exponential backoff
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    # Calculate exponential backoff delay
                    wait_time = self.delay * (2 ** attempt)
                    
                    # Log retry warning
                    if self.logger:
                        self.logger.warning(
                            f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}. "
                            f"Retrying in {wait_time} seconds..."
                        )
                    
                    time.sleep(wait_time)
                else:
                    # Last attempt failed, log error and raise
                    if self.logger:
                        self.logger.error(
                            f"All {self.max_retries} attempts failed. Last error: {str(e)}"
                        )
                    raise last_exception
        
        # Should not reach here, but raise last exception if it does
        if last_exception:
            raise last_exception
