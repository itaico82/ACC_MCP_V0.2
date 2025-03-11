"""
Issue status tools for the ACC Issues API.

This module provides MCP tools for working with issue statuses.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from uuid import UUID

from src.schemas.statuses import (
    IssueStatus,
    StatusList,
    StatusMapping,
    StatusMappingList,
    SubtypeStatusMapping,
    StatusWithTransitions
)
from src.tools.base import (
    ToolError,
    get_api_client,
    handle_response,
    require_project_context
)


logger = logging.getLogger(__name__)
API_BASE_PATH = "/api/v1"


def list_statuses(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    category: Optional[str] = None
) -> Dict:
    """List issue statuses for the current project.
    
    Args:
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        is_active: Filter by active status
        category: Filter by status category
        
    Returns:
        Paginated list of issue statuses
        
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
        
    if category:
        params["category"] = category
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/statuses", params=params)
        result = handle_response(response, StatusList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list statuses: {e}")
        raise ToolError(f"Failed to list statuses: {e}")


def get_status(status_id: str) -> Dict:
    """Get a status by ID.
    
    Args:
        status_id: ID of the status to get
        
    Returns:
        Status details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(status_id)
    except ValueError:
        raise ToolError(f"Invalid status ID: {status_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/statuses/{status_id}", params=params)
        result = handle_response(response, IssueStatus)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise ToolError(f"Failed to get status: {e}")


def get_statuses_for_subtype(subtype_id: str, include_transitions: bool = True) -> Dict:
    """Get all statuses mapped to a specific issue subtype.
    
    Args:
        subtype_id: ID of the issue subtype
        include_transitions: Whether to include allowed transitions for each status
        
    Returns:
        List of statuses with their transitions
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(subtype_id)
    except ValueError:
        raise ToolError(f"Invalid issue subtype ID: {subtype_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    if include_transitions:
        params["include_transitions"] = json.dumps(include_transitions)
    
    # Make the API request
    try:
        response = client.get(
            f"{API_BASE_PATH}/issue-subtypes/{subtype_id}/statuses", 
            params=params
        )
        result = handle_response(response, SubtypeStatusMapping)
        return result.dict() if result else {"subtype_id": subtype_id, "statuses": []}
    except Exception as e:
        logger.error(f"Failed to get statuses for subtype: {e}")
        raise ToolError(f"Failed to get statuses for subtype: {e}")


def list_status_mappings(
    subtype_id: Optional[str] = None,
    status_id: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    is_active: Optional[bool] = True
) -> Dict:
    """List status mappings.
    
    Args:
        subtype_id: Optional filter by issue subtype ID
        status_id: Optional filter by status ID
        page: Page number for pagination
        limit: Number of items per page
        is_active: Filter by active status
        
    Returns:
        Paginated list of status mappings
        
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
    
    if subtype_id:
        try:
            UUID(subtype_id)
            params["subtype_id"] = subtype_id
        except ValueError:
            raise ToolError(f"Invalid issue subtype ID: {subtype_id}")
    
    if status_id:
        try:
            UUID(status_id)
            params["status_id"] = status_id
        except ValueError:
            raise ToolError(f"Invalid status ID: {status_id}")
        
    if is_active is not None:
        params["is_active"] = json.dumps(is_active)
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/status-mappings", params=params)
        result = handle_response(response, StatusMappingList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list status mappings: {e}")
        raise ToolError(f"Failed to list status mappings: {e}")