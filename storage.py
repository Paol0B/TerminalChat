"""
In-Memory Message Storage for Terminal Chat
Stores messages only in RAM, automatically cleared on exit.
No persistence to disk, no logging.
"""

from collections import deque
from datetime import datetime
import threading


class InMemoryStorage:
    """
    Stores chat messages in memory using thread-safe data structures.
    Messages are never written to disk and are cleared on exit.
    """
    
    def __init__(self, max_messages=1000):
        """
        Initialize in-memory storage.
        Args:
            max_messages: int - maximum number of messages to keep (prevents memory overflow)
        """
        self.messages = deque(maxlen=max_messages)
        self.lock = threading.Lock()
        self.max_messages = max_messages
    
    def add_message(self, sender, content):
        """
        Add a message to memory storage.
        Args:
            sender: str - anonymous identifier (e.g., "Anonymous#1234")
            content: str - message content
        Returns: dict - the stored message
        """
        with self.lock:
            message = {
                'sender': sender,
                'content': content,
                'timestamp': datetime.now()
            }
            self.messages.append(message)
            return message
    
    def get_messages(self, count=None):
        """
        Retrieve messages from storage.
        Args:
            count: int - number of recent messages to retrieve (None for all)
        Returns: list - list of message dictionaries
        """
        with self.lock:
            if count is None:
                return list(self.messages)
            else:
                return list(self.messages)[-count:]
    
    def clear(self):
        """
        Clear all messages from memory.
        Called on exit or when requested by user.
        """
        with self.lock:
            self.messages.clear()
    
    def get_count(self):
        """
        Get the number of messages in storage.
        Returns: int - message count
        """
        with self.lock:
            return len(self.messages)


class SessionManager:
    """
    Manages active chat sessions in memory.
    No session persistence - all data cleared on exit.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions = {}
        self.lock = threading.Lock()
    
    def create_session(self, session_id):
        """
        Create a new chat session.
        Args:
            session_id: str - unique session identifier
        Returns: InMemoryStorage - storage for this session
        """
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = InMemoryStorage()
            return self.sessions[session_id]
    
    def get_session(self, session_id):
        """
        Get an existing session.
        Args:
            session_id: str - session identifier
        Returns: InMemoryStorage or None
        """
        with self.lock:
            return self.sessions.get(session_id)
    
    def remove_session(self, session_id):
        """
        Remove and clear a session.
        Args:
            session_id: str - session identifier
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].clear()
                del self.sessions[session_id]
    
    def clear_all(self):
        """
        Clear all sessions.
        Called on server shutdown.
        """
        with self.lock:
            for session in self.sessions.values():
                session.clear()
            self.sessions.clear()
