"""
Base module for MCP tools.

This module provides shared functionality for MCP tools.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast
from uuid import UUID

from pydantic import BaseModel, ValidationError

from src.api.client import APIClient
from src.schemas.responses import (
    APIResponse, 
    ErrorDetail, 
    ErrorResponse, 
    SuccessResponse
)
from src.utils.singleton import Singleton


T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)


class ContextManager(metaclass=Singleton):
    """Manager for current context (project, account, etc.)."""
    
    def __init__(self) -> None:
        """Initialize the context manager."""
        self._current_project_id: Optional[UUID] = None
        self._current_account_id: Optional[UUID] = None
        
    @property
    def current_project_id(self) -> Optional[UUID]:
        """Get the current project ID."""
        return self._current_project_id
    
    @current_project_id.setter
    def current_project_id(self, value: Optional[UUID]) -> None:
        """Set the current project ID."""
        self._current_project_id = value
        
    @property
    def current_account_id(self) -> Optional[UUID]:
        """Get the current account ID."""
        return self._current_account_id
    
    @current_account_id.setter
    def current_account_id(self, value: Optional[UUID]) -> None:
        """Set the current account ID."""
        self._current_account_id = value
        
    def clear(self) -> None:
        """Clear the current context."""
        self._current_project_id = None
        self._current_account_id = None


class ToolError(Exception):
    """Exception raised for errors in the MCP tools."""
    
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None) -> None:
        """Initialize the exception.
        
        Args:
            message: Error message
            details: Detailed error information
        """
        self.message = message
        self.details = details or []
        super().__init__(self.message)


def parse_response(response_data: Dict[str, Any], model_cls: Type[T]) -> T:
    """Parse API response into a Pydantic model.
    
    Args:
        response_data: Response data from the API
        model_cls: Pydantic model class to parse the data into
        
    Returns:
        Parsed model instance
        
    Raises:
        ToolError: If parsing fails
    """
    try:
        return model_cls.parse_obj(response_data)
    except ValidationError as e:
        logger.error(f"Failed to parse response: {e}")
        raise ToolError(f"Failed to parse response: {e}")


def handle_response(
    response: Dict[str, Any], 
    model_cls: Optional[Type[T]] = None
) -> Union[Dict[str, Any], T, None]:
    """Handle API response.
    
    Args:
        response: Response from the API
        model_cls: Optional Pydantic model class to parse the data into
        
    Returns:
        Processed response data
        
    Raises:
        ToolError: If the API returns an error
    """
    # Parse the response
    try:
        parsed = json.loads(response) if isinstance(response, str) else response
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response: {response}")
        raise ToolError(f"Failed to decode JSON response: {response}")
    
    # Check if it's an error response
    success = parsed.get("success", True)
    if not success:
        try:
            error_response = ErrorResponse.parse_obj(parsed)
            error_message = error_response.message or "Unknown error"
            logger.error(f"API returned an error: {error_message}")
            raise ToolError(error_message, error_response.errors)
        except ValidationError as e:
            logger.error(f"Failed to parse error response: {e}")
            raise ToolError(f"API returned an error: {parsed.get('message', 'Unknown error')}")
    
    # Return the data directly if no model class is provided
    if model_cls is None:
        return parsed.get("data")
        
    # Parse the data into the model
    try:
        data = parsed.get("data")
        if data is None:
            return None
        return model_cls.parse_obj(data)
    except ValidationError as e:
        logger.error(f"Failed to parse response data: {e}")
        raise ToolError(f"Failed to parse response data: {e}")


def get_api_client() -> APIClient:
    """Get the API client.
    
    Returns:
        API client instance
    """
    return APIClient()


def require_project_context() -> UUID:
    """Get the current project ID, raising an error if not set.
    
    Returns:
        Current project ID
        
    Raises:
        ToolError: If no project is set
    """
    context_manager = ContextManager()
    project_id = context_manager.current_project_id
    if project_id is None:
        logger.error("No project context set")
        raise ToolError(
            "No project context set. Use the set_current_project tool first."
        )
    return project_id