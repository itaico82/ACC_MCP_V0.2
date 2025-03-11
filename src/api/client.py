"""
API client for Autodesk Construction Cloud Issues API.

This module provides a client for making authenticated requests to the ACC Issues API.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import aiohttp

from src.auth.oauth_client import OAuthClient
from src.config import settings
from src.utils.singleton import Singleton

# Configure logging
logger = logging.getLogger(__name__)


class ApiClient(metaclass=Singleton):
    """
    API client for Autodesk Construction Cloud Issues API.
    
    This class handles making authenticated requests to the ACC Issues API,
    including authentication, request building, and response handling.
    """
    
    def __init__(self) -> None:
        """Initialize the API client."""
        self.base_url = settings.acc_api_url
        self.oauth_client = OAuthClient()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def ensure_session(self) -> None:
        """Ensure we have an active session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def get(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a GET request to the API.
        
        Args:
            path: The API path (relative to base URL)
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        return await self._request("GET", path, params=params, headers=headers)
    
    async def post(
        self, 
        path: str, 
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a POST request to the API.
        
        Args:
            path: The API path (relative to base URL)
            data: The request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        return await self._request("POST", path, data=data, params=params, headers=headers)
    
    async def put(
        self, 
        path: str, 
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a PUT request to the API.
        
        Args:
            path: The API path (relative to base URL)
            data: The request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        return await self._request("PUT", path, data=data, params=params, headers=headers)
    
    async def patch(
        self, 
        path: str, 
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a PATCH request to the API.
        
        Args:
            path: The API path (relative to base URL)
            data: The request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        return await self._request("PATCH", path, data=data, params=params, headers=headers)
    
    async def delete(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a DELETE request to the API.
        
        Args:
            path: The API path (relative to base URL)
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        return await self._request("DELETE", path, params=params, headers=headers)
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a request to the API.
        
        Args:
            method: The HTTP method
            path: The API path (relative to base URL)
            data: The request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            The JSON response
        """
        await self.ensure_session()
        
        # Get access token
        token = await self.oauth_client.ensure_token()
        
        # Build headers
        request_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)
        
        # Build URL
        url = urljoin(self.base_url, path)
        
        # Log the request
        logger.debug(f"{method} {url}")
        
        # Make the request
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                raise_for_status=True
            ) as response:
                # Parse the JSON response
                return await response.json()
                
        except aiohttp.ClientResponseError as e:
            logger.error(f"API error: {e.status} {e.message}")
            
            # Try to extract more details from the response
            try:
                error_text = await e.response.text()
                logger.error(f"Error details: {error_text}")
            except Exception:
                pass
            
            # Re-raise with more context
            raise Exception(f"API error {e.status}: {e.message}")
        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def close(self) -> None:
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()