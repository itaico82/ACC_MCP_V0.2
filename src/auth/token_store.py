"""
Token storage for OAuth tokens.

This module provides secure storage for OAuth tokens with encryption.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from src.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class TokenStore:
    """
    Secure storage for OAuth tokens.
    
    This class handles the secure storage and retrieval of OAuth tokens,
    using encryption to protect sensitive token data.
    """
    
    def __init__(self) -> None:
        """Initialize the token store."""
        self.token_path = settings.get_token_cache_path()
        self._ensure_token_dir_exists()
        
        # Generate a key for encryption
        self._key = self._derive_key()
        self._cipher = Fernet(self._key)
    
    def _ensure_token_dir_exists(self) -> None:
        """Ensure the token directory exists."""
        token_dir = self.token_path.parent
        token_dir.mkdir(parents=True, exist_ok=True)
    
    def _derive_key(self) -> bytes:
        """
        Derive an encryption key from a combination of system info and settings.
        
        This creates a deterministic key that's unique to the machine and app,
        but doesn't require the user to manage an encryption password.
        
        Returns:
            The derived encryption key
        """
        # Use a combination of system info and app settings
        # This isn't meant for high-security use cases, but provides
        # basic protection against casual access to the token file
        salt = b"ACC_MCP_Server_Token_Salt"
        
        # Create a seed from client ID and machine info
        seed = (
            settings.acc_client_id +
            settings.project_name +
            os.name +
            os.path.expanduser("~")
        ).encode()
        
        # Derive a key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(seed))
        
        return key
    
    def save_token(self, token: Dict[str, Any]) -> None:
        """
        Save an OAuth token to the store.
        
        Args:
            token: The token to save
        """
        try:
            # Convert token to JSON
            token_json = json.dumps(token)
            
            # Encrypt the token
            encrypted_token = self._cipher.encrypt(token_json.encode())
            
            # Write to file
            with open(self.token_path, "wb") as f:
                f.write(encrypted_token)
            
            logger.info(f"Token saved to {self.token_path}")
        
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def get_token(self) -> Optional[Dict[str, Any]]:
        """
        Get the stored OAuth token.
        
        Returns:
            The token, or None if no token is stored or it cannot be read
        """
        if not self.token_path.exists():
            logger.debug("No token file found")
            return None
        
        try:
            # Read the encrypted token
            with open(self.token_path, "rb") as f:
                encrypted_token = f.read()
            
            # Decrypt the token
            token_json = self._cipher.decrypt(encrypted_token).decode()
            
            # Parse the JSON
            token = json.loads(token_json)
            
            logger.debug(f"Token loaded from {self.token_path}")
            return token
        
        except (FileNotFoundError, json.JSONDecodeError, InvalidToken) as e:
            logger.warning(f"Failed to load token: {e}")
            return None
    
    def clear_token(self) -> None:
        """Clear the stored token."""
        if self.token_path.exists():
            try:
                os.remove(self.token_path)
                logger.info(f"Token removed from {self.token_path}")
            except Exception as e:
                logger.error(f"Failed to remove token: {e}")