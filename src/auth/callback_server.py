"""
OAuth callback server for handling the redirect in the 3-legged OAuth flow.

This module provides a simple HTTP server that listens for the OAuth callback
and extracts the authorization code and state parameters.
"""

import asyncio
import logging
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from aiohttp import web

# Configure logging
logger = logging.getLogger(__name__)


class CallbackServer:
    """
    HTTP server that handles the OAuth callback redirect.
    
    This server listens for the callback from Autodesk's OAuth service,
    extracts the authorization code and state, and returns them to the caller.
    """
    
    def __init__(self, port: int = 8000, path: str = "/oauth/callback") -> None:
        """
        Initialize the callback server.
        
        Args:
            port: The port to listen on
            path: The callback path
        """
        self.port = port
        self.path = path
        self.app = web.Application()
        self.runner: web.AppRunner = None
        self.site: web.TCPSite = None
        self.result_future: asyncio.Future = None
    
    async def start(self) -> Tuple[str, str]:
        """
        Start the callback server and wait for the OAuth callback.
        
        Returns:
            A tuple of (code, state) from the OAuth callback
        """
        # Set up routes
        self.app.add_routes([
            web.get(self.path, self._handle_callback),
        ])
        
        # Create a future to hold the result
        self.result_future = asyncio.get_event_loop().create_future()
        
        # Start the server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "127.0.0.1", self.port)
        await self.site.start()
        
        logger.info(f"Callback server listening on http://127.0.0.1:{self.port}{self.path}")
        
        try:
            # Wait for the callback
            code, state = await self.result_future
            return code, state
        finally:
            # Clean up
            await self._cleanup()
    
    async def _handle_callback(self, request: web.Request) -> web.Response:
        """
        Handle the OAuth callback request.
        
        This extracts the code and state parameters from the request
        and sends them back to the caller via the result future.
        
        Args:
            request: The HTTP request
            
        Returns:
            An HTTP response
        """
        # Parse query parameters
        params = parse_qs(urlparse(str(request.url)).query)
        
        # Check for error
        if "error" in params:
            error = params["error"][0]
            error_description = params.get("error_description", ["Unknown error"])[0]
            error_msg = f"OAuth error: {error} - {error_description}"
            logger.error(error_msg)
            self.result_future.set_exception(Exception(error_msg))
            return web.Response(
                text=f"""
                <html>
                <head><title>Authentication Error</title></head>
                <body>
                <h1>Authentication Error</h1>
                <p>{error_msg}</p>
                <p>You can close this window now.</p>
                </body>
                </html>
                """,
                content_type="text/html"
            )
        
        # Extract code and state
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        
        if not code:
            error_msg = "No authorization code received"
            logger.error(error_msg)
            self.result_future.set_exception(Exception(error_msg))
            return web.Response(
                text=f"""
                <html>
                <head><title>Authentication Error</title></head>
                <body>
                <h1>Authentication Error</h1>
                <p>{error_msg}</p>
                <p>You can close this window now.</p>
                </body>
                </html>
                """,
                content_type="text/html"
            )
        
        # Set the result
        self.result_future.set_result((code, state))
        
        # Return success page
        return web.Response(
            text="""
            <html>
            <head><title>Authentication Successful</title></head>
            <body>
            <h1>Authentication Successful</h1>
            <p>You have successfully authenticated with Autodesk.</p>
            <p>You can close this window now.</p>
            <script>window.close();</script>
            </body>
            </html>
            """,
            content_type="text/html"
        )
    
    async def _cleanup(self) -> None:
        """Clean up the server resources."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()