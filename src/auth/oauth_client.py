"""
OAuth client for Autodesk Construction Cloud.

This module handles the OAuth 2.0 authentication flow with Autodesk,
including token acquisition, refresh, and management.
"""

import asyncio
import logging
import secrets
import webbrowser
from typing import Dict, Optional, Tuple, Any

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7636 import create_s256_code_verifier

from src.auth.callback_server import CallbackServer
from src.auth.token_store import TokenStore
from src.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class OAuthClient:
    """
    OAuth client for Autodesk Construction Cloud.
    
    This class handles the 3-legged OAuth authentication flow with Autodesk,
    including token acquisition, refresh, and storage.
    """
    
    # Autodesk Forge OAuth endpoints
    AUTH_URL = "https://developer.api.autodesk.com/authentication/v2/authorize"
    TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"
    
    # Scope required for ACC Issues API
    SCOPE = "data:read data:write"
    
    def __init__(self) -> None:
        """Initialize the OAuth client."""
        self.client_id = settings.acc_client_id
        self.client_secret = settings.acc_client_secret
        self.redirect_uri = settings.acc_redirect_uri
        self.callback_port = settings.acc_callback_port
        
        # Create a token store
        self.token_store = TokenStore()
        
        # PKCE state
        self._code_verifier: Optional[str] = None
        self._state: Optional[str] = None
        
        # Create an OAuth session
        self._session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.SCOPE,
        )
    
    async def ensure_token(self) -> str:
        """
        Ensure we have a valid access token, initiating auth flow if needed.
        
        Returns:
            The access token string
        """
        # Check if we have a cached token
        token = self.token_store.get_token()
        
        if token and not self._is_token_expired(token):
            logger.debug("Using cached token")
            return token["access_token"]
        
        # Try to refresh the token if we have a refresh token
        if token and "refresh_token" in token:
            try:
                logger.info("Refreshing expired token")
                new_token = await self._refresh_token(token["refresh_token"])
                return new_token["access_token"]
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")
                # Fall through to full authentication
        
        # No valid token, need to authenticate
        logger.info("No valid token found, starting authentication flow")
        token = await self._authenticate()
        return token["access_token"]
    
    async def _authenticate(self) -> Dict[str, Any]:
        """
        Perform the full 3-legged OAuth authentication flow.
        
        Returns:
            The token response
        """
        # Generate PKCE code verifier and challenge
        code_verifier, code_challenge = self._generate_pkce_pair()
        self._code_verifier = code_verifier
        
        # Generate random state
        self._state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_url = self._build_authorization_url(code_challenge, self._state)
        
        # Start the callback server
        callback_server = CallbackServer(self.callback_port)
        callback_task = asyncio.create_task(callback_server.start())
        
        # Open browser for user to authenticate
        logger.info(f"Opening browser for authentication: {auth_url}")
        webbrowser.open(auth_url)
        
        try:
            # Wait for callback
            code, state = await callback_task
            
            # Verify state
            if state != self._state:
                raise ValueError("State mismatch, possible CSRF attack")
            
            # Exchange code for token
            token = await self._exchange_code_for_token(code)
            
            # Store the token
            self.token_store.save_token(token)
            
            return token
        
        finally:
            # Clean up
            self._code_verifier = None
            self._state = None
    
    async def _refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            The new token response
        """
        # Use a new session for token refresh
        refresh_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        
        # Make the refresh request
        token = refresh_session.refresh_token(
            self.TOKEN_URL,
            refresh_token=refresh_token,
        )
        
        # Store the refreshed token
        self.token_store.save_token(token)
        
        return token
    
    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for a token.
        
        Args:
            code: The authorization code
            
        Returns:
            The token response
        """
        if not self._code_verifier:
            raise ValueError("Code verifier not set")
        
        # Use a new session for token exchange
        token_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        
        # Make the token request
        token = token_session.fetch_token(
            self.TOKEN_URL,
            code=code,
            redirect_uri=self.redirect_uri,
            code_verifier=self._code_verifier,
        )
        
        return token
    
    def _build_authorization_url(self, code_challenge: str, state: str) -> str:
        """
        Build the authorization URL for the OAuth flow.
        
        Args:
            code_challenge: The PKCE code challenge
            state: The state parameter
            
        Returns:
            The authorization URL
        """
        return self._session.create_authorization_url(
            self.AUTH_URL,
            redirect_uri=self.redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method="S256",
            state=state,
        )[0]
    
    def _generate_pkce_pair(self) -> Tuple[str, str]:
        """
        Generate a PKCE code verifier and challenge pair.
        
        Returns:
            A tuple of (code_verifier, code_challenge)
        """
        code_verifier = create_s256_code_verifier()
        code_challenge = self._session.create_pkce_challenge(code_verifier)
        return code_verifier, code_challenge
    
    def _is_token_expired(self, token: Dict[str, Any]) -> bool:
        """
        Check if a token is expired.
        
        Args:
            token: The token to check
            
        Returns:
            True if the token is expired, False otherwise
        """
        return self._session.token_expired(token)