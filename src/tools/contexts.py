"""
Context tools for the ACC Issues API.

This module provides MCP tools for managing project and account contexts.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from uuid import UUID

from src.schemas.contexts import (
    ProjectContext,
    ProjectContextWithDetails,
    ProjectList
)
from src.tools.base import (
    ContextManager,
    ToolError,
    get_api_client,
    handle_response
)


logger = logging.getLogger(__name__)
API_BASE_PATH = "/api/v1"


def list_projects(
    account_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    is_active: Optional[bool] = True
) -> Dict:
    """List projects.
    
    Args:
        account_id: Optional account ID to filter by
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        is_active: Filter by active status
        
    Returns:
        Paginated list of projects
        
    Raises:
        ToolError: If the API request fails
    """
    client = get_api_client()
    
    # Build query parameters
    params = {
        "page": page,
        "limit": limit
    }
    
    if account_id:
        try:
            # Validate UUID
            UUID(account_id)
            params["account_id"] = account_id
        except ValueError:
            raise ToolError(f"Invalid account ID: {account_id}")
    
    if search:
        params["search"] = search
        
    if is_active is not None:
        params["is_active"] = json.dumps(is_active)
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/projects", params=params)
        result = handle_response(response, ProjectList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise ToolError(f"Failed to list projects: {e}")


def get_project(project_id: str) -> Dict:
    """Get a project by ID.
    
    Args:
        project_id: ID of the project to get
        
    Returns:
        Project details
        
    Raises:
        ToolError: If the API request fails
    """
    client = get_api_client()
    
    # Validate UUID
    try:
        UUID(project_id)
    except ValueError:
        raise ToolError(f"Invalid project ID: {project_id}")
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/projects/{project_id}")
        result = handle_response(response, ProjectContextWithDetails)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise ToolError(f"Failed to get project: {e}")


def set_current_project(project_id: str) -> Dict:
    """Set the current project context.
    
    Args:
        project_id: ID of the project to set as current
        
    Returns:
        Status message
        
    Raises:
        ToolError: If the API request fails
    """
    # Validate UUID
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise ToolError(f"Invalid project ID: {project_id}")
    
    # Verify the project exists
    try:
        project_details = get_project(project_id)
        account_id = project_details.get("account_id")
    except Exception as e:
        logger.error(f"Failed to verify project: {e}")
        raise ToolError(f"Failed to set project context: {e}")
    
    # Set the context
    context_manager = ContextManager()
    context_manager.current_project_id = project_uuid
    if account_id:
        context_manager.current_account_id = UUID(account_id)
    
    logger.info(f"Set current project context to: {project_id}")
    
    return {
        "success": True,
        "message": f"Current project set to: {project_details.get('name')} ({project_id})"
    }


def get_current_project() -> Dict:
    """Get the current project context.
    
    Returns:
        Current project details or an error if no project is set
        
    Raises:
        ToolError: If no project is set or the API request fails
    """
    context_manager = ContextManager()
    project_id = context_manager.current_project_id
    
    if not project_id:
        raise ToolError("No project context is currently set")
    
    # Get the project details
    return get_project(str(project_id))