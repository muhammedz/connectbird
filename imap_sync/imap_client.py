"""
IMAP Client Module
Handles IMAP server connections and operations
"""
import imaplib
import re
from typing import List, Tuple, Optional
from .utils import IMAPConnectionError, IMAPFolderError, IMAPFetchError, IMAPAppendError


class IMAPClient:
    """IMAP client wrapper for server connections and operations"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 993):
        """
        Initialize IMAP client with connection parameters
        
        Args:
            host: IMAP server hostname
            username: Account username
            password: Account password
            port: IMAP port (default: 993 for SSL)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """
        Establish SSL connection to IMAP server
        
        Returns:
            True if connection successful
            
        Raises:
            IMAPConnectionError: If connection fails
        """
        try:
            # Create SSL connection with certificate validation
            self._connection = imaplib.IMAP4_SSL(self.host, self.port)
            
            # Authenticate
            status, response = self._connection.login(self.username, self.password)
            
            if status != 'OK':
                raise IMAPConnectionError(
                    f"Authentication failed for user '{self.username}' on {self.host}:{self.port}: {response}"
                )
            
            return True
            
        except imaplib.IMAP4.error as e:
            raise IMAPConnectionError(
                f"IMAP protocol error connecting to {self.host}:{self.port}: {str(e)}"
            )
        except OSError as e:
            raise IMAPConnectionError(
                f"Network error connecting to {self.host}:{self.port}: {str(e)}"
            )
        except Exception as e:
            raise IMAPConnectionError(
                f"Unexpected error connecting to {self.host}:{self.port}: {str(e)}"
            )
    
    def disconnect(self) -> None:
        """
        Close IMAP connection properly
        Errors during disconnect are silently ignored to ensure cleanup completes
        """
        if self._connection:
            try:
                self._connection.logout()
            except Exception:
                # Ignore errors during disconnect - connection may already be closed
                pass
            finally:
                self._connection = None

    def select_folder(self, folder: str) -> int:
        """
        Select IMAP folder and return message count
        
        Args:
            folder: Folder name to select
            
        Returns:
            Number of messages in folder
            
        Raises:
            IMAPFolderError: If folder selection fails
        """
        if not self._connection:
            raise IMAPFolderError("Not connected to IMAP server")
        
        try:
            # Quote folder name if it contains spaces or special characters
            folder_to_select = folder
            if ' ' in folder or any(c in folder for c in ['&', '|', '/']):
                folder_to_select = f'"{folder}"'
            
            status, response = self._connection.select(folder_to_select)
            
            if status != 'OK':
                raise IMAPFolderError(
                    f"Failed to select folder '{folder}': {response}"
                )
            
            # Response contains message count as bytes
            message_count = int(response[0])
            return message_count
            
        except imaplib.IMAP4.error as e:
            raise IMAPFolderError(
                f"IMAP error selecting folder '{folder}': {str(e)}"
            )
        except (ValueError, IndexError) as e:
            raise IMAPFolderError(
                f"Invalid response when selecting folder '{folder}': {str(e)}"
            )
    
    def list_folders(self) -> List[str]:
        """
        List all available folders on the server
        
        Returns:
            List of folder names
        """
        if not self._connection:
            raise IMAPFolderError("Not connected to IMAP server")
        
        try:
            status, folders = self._connection.list()
            if status != 'OK':
                return []
            
            folder_list = []
            for folder_info in folders:
                folder_str = folder_info.decode('utf-7') if isinstance(folder_info, bytes) else str(folder_info)
                
                # Extract folder name from the response
                # Format: (flags) delimiter foldername
                # Example: (\HasNoChildren) "|" INBOX
                # Example: (\HasNoChildren) "|" "Folder Name"
                
                # Split by delimiter (| or /)
                # The folder name is after the last delimiter
                parts = folder_str.split('"|"')
                if len(parts) < 2:
                    parts = folder_str.split('" "')
                if len(parts) < 2:
                    parts = folder_str.split('|')
                if len(parts) < 2:
                    parts = folder_str.split('/')
                
                if len(parts) >= 2:
                    # Get the last part (folder name)
                    folder_name = parts[-1].strip()
                    
                    # Remove quotes if present
                    folder_name = folder_name.strip('"').strip()
                    
                    # Skip empty folder names or just separators
                    if folder_name and folder_name not in ['|', '/', '.', '..', '']:
                        folder_list.append(folder_name)
            
            return folder_list
            
        except Exception as e:
            raise IMAPFolderError(f"Error listing folders: {str(e)}")
    
    def folder_exists(self, folder: str) -> bool:
        """
        Check if folder exists on server
        
        Args:
            folder: Folder name to check
            
        Returns:
            True if folder exists
        """
        if not self._connection:
            raise IMAPFolderError("Not connected to IMAP server")
        
        try:
            status, response = self._connection.list('', folder)
            
            if status != 'OK':
                return False
            
            # If response is not None and contains data, folder exists
            return response[0] is not None
            
        except Exception:
            return False
    
    def create_folder(self, folder: str) -> bool:
        """
        Create folder if it doesn't exist
        
        Args:
            folder: Folder name to create
            
        Returns:
            True if created or already exists
            
        Raises:
            IMAPFolderError: If folder creation fails
        """
        if not self._connection:
            raise IMAPFolderError("Not connected to IMAP server")
        
        # Check if folder already exists
        if self.folder_exists(folder):
            return True
        
        try:
            # Quote folder name if it contains spaces or special characters
            folder_to_create = folder
            if ' ' in folder or any(c in folder for c in ['&', '|', '/']):
                folder_to_create = f'"{folder}"'
            
            status, response = self._connection.create(folder_to_create)
            
            if status != 'OK':
                raise IMAPFolderError(
                    f"Failed to create folder '{folder}': {response}"
                )
            
            return True
            
        except imaplib.IMAP4.error as e:
            raise IMAPFolderError(
                f"IMAP error creating folder '{folder}': {str(e)}"
            )

    def get_uid_list(self) -> List[str]:
        """
        Fetch all UIDs from currently selected folder
        
        Returns:
            List of UID strings
            
        Raises:
            IMAPFetchError: If UID retrieval fails
        """
        if not self._connection:
            raise IMAPFetchError("Not connected to IMAP server")
        
        try:
            # Search for all messages using UID
            status, response = self._connection.uid('search', None, 'ALL')
            
            if status != 'OK':
                raise IMAPFetchError(
                    f"IMAP search command failed: {response}"
                )
            
            # Response is a list with one element containing space-separated UIDs
            if not response or not response[0]:
                return []
            
            # Decode and split UIDs
            uid_string = response[0].decode('utf-8')
            uids = uid_string.split()
            
            return uids
            
        except imaplib.IMAP4.error as e:
            raise IMAPFetchError(
                f"IMAP protocol error retrieving UIDs: {str(e)}"
            )
        except (UnicodeDecodeError, AttributeError) as e:
            raise IMAPFetchError(
                f"Error parsing UID response: {str(e)}"
            )
        except Exception as e:
            raise IMAPFetchError(
                f"Unexpected error retrieving UIDs: {str(e)}"
            )

    def fetch_message(self, uid: str) -> Tuple[bytes, str, List[str]]:
        """
        Fetch single message by UID using streaming
        
        Args:
            uid: Message UID to fetch
            
        Returns:
            Tuple of (message_data, date, flags)
            - message_data: RFC822 message as bytes
            - date: Internal date string
            - flags: List of message flags
            
        Raises:
            IMAPFetchError: If message fetch fails
        """
        if not self._connection:
            raise IMAPFetchError("Not connected to IMAP server")
        
        try:
            # Fetch message data, internal date, and flags
            status, response = self._connection.uid(
                'fetch', 
                uid, 
                '(RFC822 INTERNALDATE FLAGS)'
            )
            
            if status != 'OK':
                raise IMAPFetchError(
                    f"IMAP fetch command failed for UID {uid}: {response}"
                )
            
            if not response or not response[0]:
                raise IMAPFetchError(
                    f"Empty response when fetching message UID {uid} - message may not exist"
                )
            
            # Parse the response
            # Response format: [(b'1 (FLAGS (...) INTERNALDATE "..." RFC822 {size}', b'message data'), b')']
            message_parts = response[0]
            
            if not isinstance(message_parts, tuple) or len(message_parts) < 2:
                raise IMAPFetchError(
                    f"Invalid response format for message UID {uid} - expected tuple with 2 elements"
                )
            
            # Extract message data (RFC822)
            message_data = message_parts[1]
            
            if not message_data:
                raise IMAPFetchError(
                    f"Empty message data for UID {uid}"
                )
            
            # Extract metadata from first part
            metadata = message_parts[0].decode('utf-8', errors='ignore')
            
            # Extract INTERNALDATE
            date_match = re.search(r'INTERNALDATE "([^"]+)"', metadata)
            date = date_match.group(1) if date_match else ''
            
            # Extract FLAGS
            flags_match = re.search(r'FLAGS \(([^)]*)\)', metadata)
            flags_str = flags_match.group(1) if flags_match else ''
            flags = [f.strip() for f in flags_str.split()] if flags_str else []
            
            return (message_data, date, flags)
            
        except imaplib.IMAP4.error as e:
            raise IMAPFetchError(
                f"IMAP protocol error fetching message UID {uid}: {str(e)}"
            )
        except (UnicodeDecodeError, AttributeError) as e:
            raise IMAPFetchError(
                f"Error parsing message metadata for UID {uid}: {str(e)}"
            )
        except Exception as e:
            raise IMAPFetchError(
                f"Unexpected error fetching message UID {uid}: {str(e)}"
            )

    def append_message(self, folder: str, message_data: bytes, 
                      date: str, flags: List[str]) -> str:
        """
        Append message to destination folder with original metadata
        
        Args:
            folder: Destination folder name
            message_data: RFC822 message data as bytes
            date: Original internal date string
            flags: List of message flags
            
        Returns:
            New UID assigned by destination server
            
        Raises:
            IMAPAppendError: If message append fails
        """
        if not self._connection:
            raise IMAPAppendError("Not connected to IMAP server")
        
        try:
            # Validate message data
            if not message_data:
                raise IMAPAppendError("Cannot append empty message data")
            
            # Format flags for IMAP APPEND command
            flags_str = ' '.join(flags) if flags else ''
            flags_tuple = tuple(flags) if flags else None
            
            # Quote folder name if it contains spaces or special characters
            folder_to_append = folder
            if ' ' in folder or any(c in folder for c in ['&', '|', '/']):
                folder_to_append = f'"{folder}"'
            
            # Append message with original date and flags
            status, response = self._connection.append(
                folder_to_append,
                flags_str,
                date if date else None,
                message_data
            )
            
            if status != 'OK':
                raise IMAPAppendError(
                    f"IMAP append command failed for folder '{folder}': {response}"
                )
            
            # Extract new UID from response
            # Response format: [b'[APPENDUID <uidvalidity> <uid>] ...']
            uid = ''
            if response and response[0]:
                response_str = response[0].decode('utf-8', errors='ignore')
                uid_match = re.search(r'APPENDUID \d+ (\d+)', response_str)
                if uid_match:
                    uid = uid_match.group(1)
            
            return uid
            
        except imaplib.IMAP4.error as e:
            raise IMAPAppendError(
                f"IMAP protocol error appending message to folder '{folder}': {str(e)}"
            )
        except (UnicodeDecodeError, AttributeError) as e:
            raise IMAPAppendError(
                f"Error parsing append response for folder '{folder}': {str(e)}"
            )
        except Exception as e:
            raise IMAPAppendError(
                f"Unexpected error appending message to folder '{folder}': {str(e)}"
            )
