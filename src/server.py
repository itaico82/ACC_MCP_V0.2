"""
MCP Server implementation for ACC Issues API.

This module provides the core MCP server implementation that handles
tool registration and execution.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union

from src.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class MCPServer:
    """
    Model Context Protocol server for ACC Issues API.
    
    This class handles incoming tool requests and dispatches them
    to the appropriate handler function.
    """
    
    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.running = False
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._tool_handlers: Dict[str, Any] = {}
        
        # Register tools
        self._register_tools()
    
    async def start(self) -> None:
        """Start the MCP server."""
        if self.running:
            logger.warning("Server is already running")
            return
        
        logger.info("Starting MCP server")
        
        # Setup JSON-RPC over stdin/stdout
        self.running = True
        
        # Report that the server is ready
        logger.info("MCP server is ready")
        
        # Start processing input
        asyncio.create_task(self._process_input())
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if not self.running:
            logger.warning("Server is not running")
            return
        
        logger.info("Stopping MCP server")
        self.running = False
    
    def _register_tool(self, tool_name: str, tool_spec: Dict[str, Any], handler: Any) -> None:
        """Register a tool with the server.
        
        Args:
            tool_name: The name of the tool
            tool_spec: The tool specification in JSON Schema format
            handler: The function that handles tool execution
        """
        self._tools[tool_name] = tool_spec
        self._tool_handlers[tool_name] = handler
        logger.info(f"Registered tool: {tool_name}")
    
    def _register_tools(self) -> None:
        """Register all available tools."""
        # Import handlers when needed to avoid circular imports
        from src.tools.issues import (
            create_issue, 
            list_issues, 
            get_issue,
            search_issues,
            add_comment
        )
        
        # Define and register tools
        self._register_tool(
            "create_issue",
            {
                "name": "create_issue",
                "description": "Create a new issue in Autodesk Construction Cloud",
                "parameters": {
                    "properties": {
                        "title": {
                            "type": "string", 
                            "description": "Title of the issue (max 100 characters)"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Detailed description of the issue (max 1000 characters)"
                        },
                        "issue_type": {
                            "type": "string", 
                            "description": "Description of issue type/category (will be mapped to appropriate type)"
                        },
                        "status": {
                            "type": "string", 
                            "description": "Issue status (must be valid for the selected issue subtype)"
                        },
                        "location_details": {
                            "type": "string", 
                            "description": "Physical location description (max 250 characters)"
                        },
                        "due_date": {
                            "type": "string", 
                            "description": "Due date in ISO8601 format (YYYY-MM-DD)"
                        },
                        "assigned_to": {
                            "type": "string", 
                            "description": "Person, role, or company to assign (will use ID if known)"
                        },
                        "custom_attributes": {
                            "type": "object", 
                            "description": "Custom attributes specific to the issue type and subtype"
                        }
                    },
                    "required": ["title"]
                }
            },
            create_issue
        )
        
        self._register_tool(
            "list_issues",
            {
                "name": "list_issues",
                "description": "Get a filtered list of issues from Autodesk Construction Cloud",
                "parameters": {
                    "properties": {
                        "status": {
                            "type": "string", 
                            "description": "Filter by issue status (comma-separated for multiple)"
                        },
                        "issue_type_id": {
                            "type": "string", 
                            "description": "Filter by issue type/category ID"
                        },
                        "assigned_to": {
                            "type": "string", 
                            "description": "Filter by assignee"
                        },
                        "due_date": {
                            "type": "string", 
                            "description": "Filter by due date range (e.g., '2023-01-01..2023-02-01')"
                        },
                        "created_by": {
                            "type": "string", 
                            "description": "Filter by creator"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Maximum number of issues to return (max 200)"
                        },
                        "offset": {
                            "type": "integer", 
                            "description": "Pagination offset"
                        },
                        "sort": {
                            "type": "string", 
                            "description": "Field to sort by (prefix with '-' for descending)"
                        }
                    },
                    "required": []
                }
            },
            list_issues
        )
        
        self._register_tool(
            "get_issue",
            {
                "name": "get_issue",
                "description": "Get details of a specific issue by ID or display ID",
                "parameters": {
                    "properties": {
                        "issue_id": {
                            "type": "string", 
                            "description": "UUID of the issue to retrieve"
                        },
                        "display_id": {
                            "type": "integer", 
                            "description": "Display ID of the issue (numerical ID shown in UI)"
                        }
                    },
                    "required": ["issue_id"]
                }
            },
            get_issue
        )
        
        self._register_tool(
            "search_issues",
            {
                "name": "search_issues",
                "description": "Search for issues using natural language",
                "parameters": {
                    "properties": {
                        "query": {
                            "type": "string", 
                            "description": "Natural language search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            search_issues
        )
        
        self._register_tool(
            "add_comment",
            {
                "name": "add_comment",
                "description": "Add a comment to an existing issue",
                "parameters": {
                    "properties": {
                        "issue_id": {
                            "type": "string", 
                            "description": "UUID of the issue to comment on"
                        },
                        "body": {
                            "type": "string", 
                            "description": "Comment text"
                        }
                    },
                    "required": ["issue_id", "body"]
                }
            },
            add_comment
        )
    
    async def _process_input(self) -> None:
        """Process input from stdin and respond via stdout."""
        while self.running:
            try:
                # Read a line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    logger.warning("Received empty input, exiting")
                    self.running = False
                    break
                
                # Parse the JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {line}")
                    self._send_error(-32700, "Parse error", None)
                    continue
                
                # Process the request
                await self._handle_request(request)
                
            except Exception as e:
                logger.exception(f"Error processing input: {e}")
                self._send_error(-32603, f"Internal error: {str(e)}", None)
    
    async def _handle_request(self, request: Dict[str, Any]) -> None:
        """Handle a JSON-RPC request.
        
        Args:
            request: The JSON-RPC request
        """
        # Validate the request
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            self._send_error(-32600, "Invalid Request", request.get("id"))
            return
        
        if "method" not in request:
            self._send_error(-32600, "Method not specified", request.get("id"))
            return
        
        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Handle standard methods
        if method == "rpc.discover":
            self._handle_discover(request_id)
            return
        
        # Check if the method is a registered tool
        if method not in self._tool_handlers:
            self._send_error(-32601, f"Method not found: {method}", request_id)
            return
        
        # Execute the tool
        try:
            result = await self._tool_handlers[method](**params)
            self._send_result(result, request_id)
        except Exception as e:
            logger.exception(f"Error executing tool {method}: {e}")
            self._send_error(-32603, f"Tool execution error: {str(e)}", request_id)
    
    def _handle_discover(self, request_id: Optional[Union[str, int]]) -> None:
        """Handle the rpc.discover method.
        
        Args:
            request_id: The request ID
        """
        # Build the list of available tools
        tools = []
        for name, spec in self._tools.items():
            tools.append(spec)
        
        # Send the response
        self._send_result({"tools": tools}, request_id)
    
    def _send_result(self, result: Any, request_id: Optional[Union[str, int]]) -> None:
        """Send a JSON-RPC result response.
        
        Args:
            result: The result data
            request_id: The request ID
        """
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
        self._send_response(response)
    
    def _send_error(self, code: int, message: str, request_id: Optional[Union[str, int]]) -> None:
        """Send a JSON-RPC error response.
        
        Args:
            code: The error code
            message: The error message
            request_id: The request ID
        """
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
        self._send_response(response)
    
    def _send_response(self, response: Dict[str, Any]) -> None:
        """Send a JSON-RPC response to stdout.
        
        Args:
            response: The response data
        """
        try:
            json_response = json.dumps(response)
            print(json_response, flush=True)
        except Exception as e:
            logger.exception(f"Error sending response: {e}")