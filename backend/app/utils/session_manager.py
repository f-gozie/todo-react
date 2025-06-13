"""
Session Management for Music Sync Hub

This module provides secure session and token management to replace the 
temporary in-memory token caches.
"""

import json
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import os
from pathlib import Path

from app.core.config import SECRET_KEY, SESSION_LIFETIME_HOURS, TOKEN_REFRESH_BUFFER_MINUTES

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user sessions and token storage securely.
    
    For production use, this should be replaced with a proper database
    or secure session backend like Redis.
    """
    
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        logger.info(f"SessionManager initialized with session directory: {self.session_dir}")
    
    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.session_dir / f"{session_id}.json"
    
    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if a token is expired or needs refresh."""
        if 'expires_at' in token_data:
            expires_at = token_data['expires_at']
            # Add buffer time for refresh
            buffer_seconds = TOKEN_REFRESH_BUFFER_MINUTES * 60
            return expires_at <= (time.time() + buffer_seconds)
        
        # If no expiry info, assume it needs refresh after session lifetime
        created_at = token_data.get('created_at', 0)
        max_age = SESSION_LIFETIME_HOURS * 3600
        return (time.time() - created_at) > max_age
    
    def create_session(self) -> str:
        """Create a new session and return session ID."""
        import uuid
        session_id = str(uuid.uuid4())
        
        session_data = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'tokens': {}
        }
        
        session_file = self._get_session_file(session_id)
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID."""
        if not session_id:
            return None
            
        session_file = self._get_session_file(session_id)
        if not session_file.exists():
            logger.warning(f"Session file not found: {session_id}")
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            created_at = session_data.get('created_at', 0)
            max_age = SESSION_LIFETIME_HOURS * 3600
            
            if (time.time() - created_at) > max_age:
                logger.info(f"Session expired: {session_id}")
                self.destroy_session(session_id)
                return None
            
            # Update last accessed time
            session_data['last_accessed'] = time.time()
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            
            return session_data
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data."""
        if not session_id:
            return False
            
        session_file = self._get_session_file(session_id)
        
        try:
            session_data['last_accessed'] = time.time()
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            return True
            
        except IOError as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session."""
        if not session_id:
            return False
            
        session_file = self._get_session_file(session_id)
        
        try:
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Destroyed session: {session_id}")
            return True
            
        except IOError as e:
            logger.error(f"Error destroying session {session_id}: {e}")
            return False
    
    def store_service_token(self, session_id: str, service: str, token_data: Dict[str, Any]) -> bool:
        """Store a service token in the session."""
        session_data = self.get_session(session_id)
        if not session_data:
            logger.warning(f"Cannot store token - session not found: {session_id}")
            return False
        
        # Add timestamp if not present
        if 'created_at' not in token_data:
            token_data['created_at'] = time.time()
        
        session_data['tokens'][service] = token_data
        return self.update_session(session_id, session_data)
    
    def get_service_token(self, session_id: str, service: str) -> Optional[Dict[str, Any]]:
        """Get a service token from the session."""
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        
        token_data = session_data.get('tokens', {}).get(service)
        if not token_data:
            return None
        
        # Check if token is expired
        if self._is_token_expired(token_data):
            logger.info(f"Token expired for service {service} in session {session_id}")
            return None
        
        return token_data
    
    def remove_service_token(self, session_id: str, service: str) -> bool:
        """Remove a service token from the session."""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        if service in session_data.get('tokens', {}):
            del session_data['tokens'][service]
            return self.update_session(session_id, session_data)
        
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired session files. Returns number of cleaned sessions."""
        cleaned = 0
        max_age = SESSION_LIFETIME_HOURS * 3600
        current_time = time.time()
        
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    created_at = session_data.get('created_at', 0)
                    if (current_time - created_at) > max_age:
                        session_file.unlink()
                        cleaned += 1
                        logger.debug(f"Cleaned expired session: {session_file.stem}")
                        
                except (json.JSONDecodeError, IOError):
                    # Remove corrupted session files
                    session_file.unlink()
                    cleaned += 1
                    logger.warning(f"Removed corrupted session file: {session_file}")
                    
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired/corrupted sessions")
        
        return cleaned


# Global session manager instance
session_manager = SessionManager()


# Convenience functions for easier usage
def create_session() -> str:
    """Create a new session."""
    return session_manager.create_session()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data."""
    return session_manager.get_session(session_id)


def store_token(session_id: str, service: str, token_data: Dict[str, Any]) -> bool:
    """Store a service token."""
    return session_manager.store_service_token(session_id, service, token_data)


def get_token(session_id: str, service: str) -> Optional[Dict[str, Any]]:
    """Get a service token."""
    return session_manager.get_service_token(session_id, service)


def remove_token(session_id: str, service: str) -> bool:
    """Remove a service token."""
    return session_manager.remove_service_token(session_id, service)


def destroy_session(session_id: str) -> bool:
    """Destroy a session."""
    return session_manager.destroy_session(session_id) 