#!/usr/bin/env python
"""
Main entry point for the ACC MCP Server.

This module initializes the MCP server and handles incoming requests.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Import local modules
from src.config import settings
from src.server import MCPServer


async def shutdown(server: MCPServer) -> None:
    """Perform graceful shutdown of the server."""
    logger.info("Shutting down server...")
    await server.stop()
    logger.info("Server shutdown complete.")


async def main() -> None:
    """Initialize and run the MCP server."""
    logger.info("Starting ACC MCP Server v%s", "0.2.0")
    logger.info("API URL: %s", settings.acc_api_url)
    
    # Create and start the server
    server = MCPServer()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(server))
        )
    
    try:
        await server.start()
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except asyncio.CancelledError:
        logger.info("Server task was cancelled")
    finally:
        await shutdown(server)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Unhandled exception: %s", e)
        sys.exit(1)
    sys.exit(0)