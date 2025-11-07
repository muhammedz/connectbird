"""
Cache Manager Module
Handles SQLite database management and duplicate control
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime



class CacheManager:
    """
    Manages SQLite database for tracking transferred messages
    Provides duplicate detection and resume functionality
    """
    
    def __init__(self, db_path: str = "transfer_cache.db"):
        """
        Initialize CacheManager with database path
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def initialize(self) -> None:
        """
        Create database and tables if they don't exist
        Sets up the transferred_messages table with appropriate schema and indexes
        
        Raises:
            Exception: If database initialization fails
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create transferred_messages table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transferred_messages (
                    source_uid TEXT NOT NULL,
                    dest_uid TEXT NOT NULL,
                    folder TEXT NOT NULL,
                    transferred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_size INTEGER,
                    PRIMARY KEY (source_uid, folder)
                )
            """)
            
            # Create indexes for faster queries
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_folder 
                ON transferred_messages(folder)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transferred_at 
                ON transferred_messages(transferred_at)
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            raise Exception(f"Failed to initialize cache database at '{self.db_path}': {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error initializing cache database: {str(e)}")

    
    def is_transferred(self, source_uid: str, folder: str) -> bool:
        """
        Check if a message has already been transferred
        
        Args:
            source_uid: Source message UID
            folder: Folder name
            
        Returns:
            True if message already transferred, False otherwise
            Returns False if database query fails
        """
        if not self.cursor:
            return False
        
        try:
            # Use parameterized query to prevent SQL injection
            self.cursor.execute(
                "SELECT 1 FROM transferred_messages WHERE source_uid = ? AND folder = ?",
                (source_uid, folder)
            )
            
            return self.cursor.fetchone() is not None
            
        except sqlite3.Error as e:
            # Log error but don't crash - return False to allow transfer attempt
            return False
        except Exception:
            return False
    
    def get_transferred_uids(self, folder: str) -> List[str]:
        """
        Retrieve all transferred UIDs for a specific folder
        
        Args:
            folder: Folder name
            
        Returns:
            List of transferred source UIDs
            Returns empty list if database query fails
        """
        if not self.cursor:
            return []
        
        try:
            # Use parameterized query to prevent SQL injection
            self.cursor.execute(
                "SELECT source_uid FROM transferred_messages WHERE folder = ?",
                (folder,)
            )
            
            results = self.cursor.fetchall()
            return [row[0] for row in results]
            
        except sqlite3.Error as e:
            # Return empty list on error - will cause all messages to be transferred
            return []
        except Exception:
            return []

    
    def mark_transferred(self, source_uid: str, dest_uid: str, folder: str, 
                        message_size: Optional[int] = None) -> None:
        """
        Mark a message as transferred by inserting a record
        
        Args:
            source_uid: Source message UID
            dest_uid: Destination message UID
            folder: Folder name
            message_size: Optional message size in bytes
            
        Raises:
            Exception: If database insert fails
        """
        if not self.cursor or not self.conn:
            raise Exception("Cache database not initialized")
        
        try:
            # Insert new record with current timestamp
            self.cursor.execute(
                """
                INSERT INTO transferred_messages 
                (source_uid, dest_uid, folder, transferred_at, message_size)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source_uid, dest_uid, folder, datetime.now(), message_size)
            )
            
            # Commit immediately for crash safety
            self.conn.commit()
            
        except sqlite3.IntegrityError as e:
            # Duplicate entry - message already marked as transferred
            # This is not a critical error, just log it
            pass
        except sqlite3.Error as e:
            raise Exception(f"Database error marking message as transferred: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error marking message as transferred: {str(e)}")

    
    def get_statistics(self, folder: Optional[str] = None) -> Dict[str, int]:
        """
        Get transfer statistics
        
        Args:
            folder: Optional folder name to filter by. If None, returns stats for all folders
            
        Returns:
            Dictionary with statistics (total_transferred, total_size, etc.)
            Returns default values if database query fails
        """
        if not self.cursor:
            return {"total_transferred": 0, "total_size": 0}
        
        try:
            if folder:
                # Get statistics for specific folder
                self.cursor.execute(
                    """
                    SELECT COUNT(*), COALESCE(SUM(message_size), 0)
                    FROM transferred_messages 
                    WHERE folder = ?
                    """,
                    (folder,)
                )
            else:
                # Get statistics for all folders
                self.cursor.execute(
                    """
                    SELECT COUNT(*), COALESCE(SUM(message_size), 0)
                    FROM transferred_messages
                    """
                )
            
            result = self.cursor.fetchone()
            count, total_size = result if result else (0, 0)
            
            stats = {
                "total_transferred": count,
                "total_size": total_size if total_size else 0
            }
            
            # If no folder specified, also get per-folder breakdown
            if not folder:
                self.cursor.execute(
                    """
                    SELECT folder, COUNT(*) 
                    FROM transferred_messages 
                    GROUP BY folder
                    """
                )
                folder_counts = self.cursor.fetchall()
                for folder_name, count in folder_counts:
                    stats[f"folder_{folder_name}"] = count
            
            return stats
            
        except sqlite3.Error as e:
            # Return default values on error
            return {"total_transferred": 0, "total_size": 0}
        except Exception:
            return {"total_transferred": 0, "total_size": 0}
    
    def close(self) -> None:
        """
        Properly close database connection
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.conn:
            self.conn.close()
            self.conn = None
