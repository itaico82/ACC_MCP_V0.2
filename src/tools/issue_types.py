"""
Issue types tools for the ACC Issues API.

This module provides MCP tools for working with issue types and subtypes.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from uuid import UUID

from src.schemas.issue_types import (
    IssueType,
    IssueSubtype,
    IssueTypeList
)
from src.tools.base import (
    ToolError,
    get_api_client,
    handle_response,
    require_project_context
)


logger = logging.getLogger(__name__)
API_BASE_PATH = "/api/v1"


def list_issue_types(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    include_subtypes: bool = False
) -> Dict:
    """List issue types for the current project.
    
    Args:
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        is_active: Filter by active status
        include_subtypes: Whether to include subtypes in the response
        
    Returns:
        Paginated list of issue types
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Build query parameters
    params = {
        "page": page,
        "limit": limit,
        "project_id": str(project_id)
    }
    
    if search:
        params["search"] = search
        
    if is_active is not None:
        params["is_active"] = json.dumps(is_active)
        
    if include_subtypes:
        params["include_subtypes"] = json.dumps(include_subtypes)
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/issue-types", params=params)
        result = handle_response(response, IssueTypeList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list issue types: {e}")
        raise ToolError(f"Failed to list issue types: {e}")


def get_issue_type(type_id: str, include_subtypes: bool = True) -> Dict:
    """Get an issue type by ID.
    
    Args:
        type_id: ID of the issue type to get
        include_subtypes: Whether to include subtypes in the response
        
    Returns:
        Issue type details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(type_id)
    except ValueError:
        raise ToolError(f"Invalid issue type ID: {type_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    if include_subtypes:
        params["include_subtypes"] = json.dumps(include_subtypes)
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/issue-types/{type_id}", params=params)
        result = handle_response(response, IssueType)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get issue type: {e}")
        raise ToolError(f"Failed to get issue type: {e}")


def list_issue_subtypes(
    type_id: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = True
) -> Dict:
    """List issue subtypes for a specific issue type.
    
    Args:
        type_id: ID of the issue type to get subtypes for
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        is_active: Filter by active status
        
    Returns:
        Paginated list of issue subtypes
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(type_id)
    except ValueError:
        raise ToolError(f"Invalid issue type ID: {type_id}")
    
    # Build query parameters
    params = {
        "page": page,
        "limit": limit,
        "project_id": str(project_id)
    }
    
    if search:
        params["search"] = search
        
    if is_active is not None:
        params["is_active"] = json.dumps(is_active)
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/issue-types/{type_id}/subtypes", params=params)
        # The response structure may vary based on API implementation
        # This is a simplified example assuming it returns a list-like structure
        result = handle_response(response)
        return result if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list issue subtypes: {e}")
        raise ToolError(f"Failed to list issue subtypes: {e}")


def get_issue_subtype(type_id: str, subtype_id: str) -> Dict:
    """Get an issue subtype by ID.
    
    Args:
        type_id: ID of the parent issue type
        subtype_id: ID of the issue subtype to get
        
    Returns:
        Issue subtype details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUIDs
    try:
        UUID(type_id)
    except ValueError:
        raise ToolError(f"Invalid issue type ID: {type_id}")
        
    try:
        UUID(subtype_id)
    except ValueError:
        raise ToolError(f"Invalid issue subtype ID: {subtype_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    # Make the API request
    try:
        response = client.get(
            f"{API_BASE_PATH}/issue-types/{type_id}/subtypes/{subtype_id}", 
            params=params
        )
        result = handle_response(response, IssueSubtype)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get issue subtype: {e}")
        raise ToolError(f"Failed to get issue subtype: {e}")