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
        # Import tools modules
        from src.tools.issues import (
            list_issues, 
            get_issue,
            create_issue,
            update_issue
        )
        
        from src.tools.issue_types import (
            list_issue_types,
            get_issue_type,
            list_issue_subtypes,
            get_issue_subtype
        )
        
        from src.tools.statuses import (
            list_statuses,
            get_status,
            get_statuses_for_subtype
        )
        
        from src.tools.custom_attributes import (
            list_custom_attributes,
            get_custom_attribute,
            get_custom_attributes_for_type,
            get_custom_attributes_for_subtype
        )
        
        from src.tools.contexts import (
            list_projects,
            get_project,
            set_current_project
        )
        
        # Register project context tools
        self._register_tool(
            "list_projects",
            {
                "name": "list_projects",
                "description": "List available projects in Autodesk Construction Cloud",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "string", 
                            "description": "Optional account ID to filter by"
                        },
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "is_active": {
                            "type": "boolean", 
                            "description": "Filter by active status"
                        }
                    },
                    "required": []
                }
            },
            list_projects
        )
        
        self._register_tool(
            "get_project",
            {
                "name": "get_project",
                "description": "Get details of a specific project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string", 
                            "description": "ID of the project to get"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            get_project
        )
        
        self._register_tool(
            "set_current_project",
            {
                "name": "set_current_project",
                "description": "Set the current project context for subsequent operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string", 
                            "description": "ID of the project to set as current"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            set_current_project
        )
        
        # Register issue type tools
        self._register_tool(
            "list_issue_types",
            {
                "name": "list_issue_types",
                "description": "List available issue types/categories in the current project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "is_active": {
                            "type": "boolean", 
                            "description": "Filter by active status"
                        },
                        "include_subtypes": {
                            "type": "boolean", 
                            "description": "Whether to include subtypes in the response"
                        }
                    },
                    "required": []
                }
            },
            list_issue_types
        )
        
        self._register_tool(
            "get_issue_type",
            {
                "name": "get_issue_type",
                "description": "Get details of a specific issue type/category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type_id": {
                            "type": "string", 
                            "description": "ID of the issue type to get"
                        },
                        "include_subtypes": {
                            "type": "boolean", 
                            "description": "Whether to include subtypes in the response"
                        }
                    },
                    "required": ["type_id"]
                }
            },
            get_issue_type
        )
        
        self._register_tool(
            "list_issue_subtypes",
            {
                "name": "list_issue_subtypes",
                "description": "List available issue subtypes for a specific issue type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type_id": {
                            "type": "string", 
                            "description": "ID of the issue type to get subtypes for"
                        },
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "is_active": {
                            "type": "boolean", 
                            "description": "Filter by active status"
                        }
                    },
                    "required": ["type_id"]
                }
            },
            list_issue_subtypes
        )
        
        self._register_tool(
            "get_issue_subtype",
            {
                "name": "get_issue_subtype",
                "description": "Get details of a specific issue subtype",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type_id": {
                            "type": "string", 
                            "description": "ID of the parent issue type"
                        },
                        "subtype_id": {
                            "type": "string", 
                            "description": "ID of the issue subtype to get"
                        }
                    },
                    "required": ["type_id", "subtype_id"]
                }
            },
            get_issue_subtype
        )
        
        # Register status tools
        self._register_tool(
            "list_statuses",
            {
                "name": "list_statuses",
                "description": "List available issue statuses in the current project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "is_active": {
                            "type": "boolean", 
                            "description": "Filter by active status"
                        },
                        "category": {
                            "type": "string", 
                            "description": "Filter by status category"
                        }
                    },
                    "required": []
                }
            },
            list_statuses
        )
        
        self._register_tool(
            "get_status",
            {
                "name": "get_status",
                "description": "Get details of a specific issue status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status_id": {
                            "type": "string", 
                            "description": "ID of the status to get"
                        }
                    },
                    "required": ["status_id"]
                }
            },
            get_status
        )
        
        self._register_tool(
            "get_statuses_for_subtype",
            {
                "name": "get_statuses_for_subtype",
                "description": "Get all statuses mapped to a specific issue subtype",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subtype_id": {
                            "type": "string", 
                            "description": "ID of the issue subtype"
                        },
                        "include_transitions": {
                            "type": "boolean", 
                            "description": "Whether to include allowed transitions for each status"
                        }
                    },
                    "required": ["subtype_id"]
                }
            },
            get_statuses_for_subtype
        )
        
        # Register custom attribute tools
        self._register_tool(
            "list_custom_attributes",
            {
                "name": "list_custom_attributes",
                "description": "List available custom attributes in the current project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "is_active": {
                            "type": "boolean", 
                            "description": "Filter by active status"
                        },
                        "data_type": {
                            "type": "string", 
                            "description": "Filter by data type"
                        }
                    },
                    "required": []
                }
            },
            list_custom_attributes
        )
        
        self._register_tool(
            "get_custom_attribute",
            {
                "name": "get_custom_attribute",
                "description": "Get details of a specific custom attribute",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "attribute_id": {
                            "type": "string", 
                            "description": "ID of the custom attribute to get"
                        }
                    },
                    "required": ["attribute_id"]
                }
            },
            get_custom_attribute
        )
        
        self._register_tool(
            "get_custom_attributes_for_type",
            {
                "name": "get_custom_attributes_for_type",
                "description": "Get custom attributes mapped to an issue type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type_id": {
                            "type": "string", 
                            "description": "ID of the issue type"
                        }
                    },
                    "required": ["type_id"]
                }
            },
            get_custom_attributes_for_type
        )
        
        self._register_tool(
            "get_custom_attributes_for_subtype",
            {
                "name": "get_custom_attributes_for_subtype",
                "description": "Get custom attributes mapped to an issue subtype",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subtype_id": {
                            "type": "string", 
                            "description": "ID of the issue subtype"
                        }
                    },
                    "required": ["subtype_id"]
                }
            },
            get_custom_attributes_for_subtype
        )
        
        # Register issue tools
        self._register_tool(
            "create_issue",
            {
                "name": "create_issue",
                "description": "Create a new issue in Autodesk Construction Cloud",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string", 
                            "description": "Title of the issue (max 100 characters)"
                        },
                        "type_id": {
                            "type": "string", 
                            "description": "ID of the issue type"
                        },
                        "subtype_id": {
                            "type": "string", 
                            "description": "ID of the issue subtype"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Detailed description of the issue (max 1000 characters)"
                        },
                        "status": {
                            "type": "string", 
                            "description": "Issue status (must be valid for the selected issue subtype)"
                        },
                        "assigned_to": {
                            "type": "string", 
                            "description": "ID of the user, role, or company to assign"
                        },
                        "due_date": {
                            "type": "string", 
                            "description": "Due date in ISO8601 format (YYYY-MM-DD)"
                        },
                        "custom_attributes": {
                            "type": "object", 
                            "description": "Custom attributes specific to the issue type and subtype"
                        }
                    },
                    "required": ["title", "type_id", "subtype_id"]
                }
            },
            create_issue
        )
        
        self._register_tool(
            "list_issues",
            {
                "name": "list_issues",
                "description": "List issues in the current project with various filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer", 
                            "description": "Page number for pagination"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Number of items per page"
                        },
                        "search": {
                            "type": "string", 
                            "description": "Optional search term"
                        },
                        "type_id": {
                            "type": "string", 
                            "description": "Filter by issue type ID"
                        },
                        "subtype_id": {
                            "type": "string", 
                            "description": "Filter by issue subtype ID"
                        },
                        "status": {
                            "type": "string", 
                            "description": "Filter by issue status"
                        },
                        "created_by": {
                            "type": "string", 
                            "description": "Filter by creator user ID"
                        },
                        "assigned_to": {
                            "type": "string", 
                            "description": "Filter by assignee user ID"
                        },
                        "sort_by": {
                            "type": "string", 
                            "description": "Field to sort by"
                        },
                        "sort_order": {
                            "type": "string", 
                            "description": "Sort order (asc or desc)"
                        },
                        "from_date": {
                            "type": "string", 
                            "description": "Filter by creation date (from)"
                        },
                        "to_date": {
                            "type": "string", 
                            "description": "Filter by creation date (to)"
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
                "description": "Get details of a specific issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string", 
                            "description": "ID of the issue to get"
                        }
                    },
                    "required": ["issue_id"]
                }
            },
            get_issue
        )
        
        self._register_tool(
            "update_issue",
            {
                "name": "update_issue",
                "description": "Update an existing issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string", 
                            "description": "ID of the issue to update"
                        },
                        "title": {
                            "type": "string", 
                            "description": "New title for the issue"
                        },
                        "description": {
                            "type": "string", 
                            "description": "New description for the issue"
                        },
                        "status": {
                            "type": "string", 
                            "description": "New status for the issue"
                        },
                        "assigned_to": {
                            "type": "string", 
                            "description": "New assignee for the issue"
                        },
                        "due_date": {
                            "type": "string", 
                            "description": "New due date for the issue"
                        },
                        "custom_attributes": {
                            "type": "object", 
                            "description": "Updated custom attributes"
                        }
                    },
                    "required": ["issue_id"]
                }
            },
            update_issue
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