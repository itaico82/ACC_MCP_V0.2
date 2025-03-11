"""
Issues tools for the ACC Issues API.

This module provides MCP tools for working with issues.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from src.schemas.issues import (
    Issue,
    IssueCreate,
    IssueList
)
from src.tools.base import (
    ToolError,
    get_api_client,
    handle_response,
    require_project_context
)


logger = logging.getLogger(__name__)
API_BASE_PATH = "/api/v1"


def list_issues(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    type_id: Optional[str] = None,
    subtype_id: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[str] = None,
    assigned_to: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Dict:
    """List issues for the current project.
    
    Args:
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        type_id: Filter by issue type ID
        subtype_id: Filter by issue subtype ID
        status: Filter by issue status
        created_by: Filter by creator user ID
        assigned_to: Filter by assignee user ID
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        from_date: Filter by creation date (from)
        to_date: Filter by creation date (to)
        
    Returns:
        Paginated list of issues
        
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
        
    if type_id:
        try:
            UUID(type_id)
            params["type_id"] = type_id
        except ValueError:
            raise ToolError(f"Invalid issue type ID: {type_id}")
    
    if subtype_id:
        try:
            UUID(subtype_id)
            params["subtype_id"] = subtype_id
        except ValueError:
            raise ToolError(f"Invalid issue subtype ID: {subtype_id}")
    
    if status:
        params["status"] = status
    
    if created_by:
        params["created_by"] = created_by
    
    if assigned_to:
        params["assigned_to"] = assigned_to
    
    if sort_by:
        params["sort_by"] = sort_by
    
    if sort_order:
        if sort_order.lower() not in ["asc", "desc"]:
            raise ToolError("Sort order must be 'asc' or 'desc'")
        params["sort_order"] = sort_order.lower()
    
    if from_date:
        try:
            # Validate date format
            datetime.fromisoformat(from_date.replace("Z", "+00:00"))
            params["from_date"] = from_date
        except ValueError:
            raise ToolError(f"Invalid from_date format: {from_date}, use ISO format")
    
    if to_date:
        try:
            # Validate date format
            datetime.fromisoformat(to_date.replace("Z", "+00:00"))
            params["to_date"] = to_date
        except ValueError:
            raise ToolError(f"Invalid to_date format: {to_date}, use ISO format")
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/issues", params=params)
        result = handle_response(response, IssueList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list issues: {e}")
        raise ToolError(f"Failed to list issues: {e}")


def get_issue(issue_id: str) -> Dict:
    """Get an issue by ID.
    
    Args:
        issue_id: ID of the issue to get
        
    Returns:
        Issue details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(issue_id)
    except ValueError:
        raise ToolError(f"Invalid issue ID: {issue_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/issues/{issue_id}", params=params)
        result = handle_response(response, Issue)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        raise ToolError(f"Failed to get issue: {e}")


def create_issue(
    title: str,
    type_id: str,
    subtype_id: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    custom_attributes: Optional[Dict[str, Any]] = None
) -> Dict:
    """Create a new issue.
    
    Args:
        title: Issue title
        type_id: Issue type ID
        subtype_id: Issue subtype ID
        description: Optional issue description
        status: Optional issue status
        assigned_to: Optional assignee ID
        due_date: Optional due date (ISO format)
        custom_attributes: Optional custom attributes
        
    Returns:
        Created issue details
        
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
    
    # Validate due date if provided
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            raise ToolError(f"Invalid due_date format: {due_date}, use ISO format")
    
    # Prepare issue data
    issue_data = {
        "title": title,
        "type_id": type_id,
        "subtype_id": subtype_id,
        "project_id": str(project_id)
    }
    
    if description:
        issue_data["description"] = description
    
    if status:
        issue_data["status"] = status
    
    if assigned_to:
        issue_data["assigned_to"] = assigned_to
    
    if due_date:
        issue_data["due_date"] = due_date
    
    if custom_attributes:
        issue_data["custom_attributes"] = custom_attributes
    
    # Make the API request
    try:
        response = client.post(f"{API_BASE_PATH}/issues", json=issue_data)
        result = handle_response(response, Issue)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to create issue: {e}")
        raise ToolError(f"Failed to create issue: {e}")


def update_issue(
    issue_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    custom_attributes: Optional[Dict[str, Any]] = None
) -> Dict:
    """Update an existing issue.
    
    Args:
        issue_id: ID of the issue to update
        title: Optional new title
        description: Optional new description
        status: Optional new status
        assigned_to: Optional new assignee ID
        due_date: Optional new due date (ISO format)
        custom_attributes: Optional new custom attributes
        
    Returns:
        Updated issue details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(issue_id)
    except ValueError:
        raise ToolError(f"Invalid issue ID: {issue_id}")
    
    # Validate due date if provided
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            raise ToolError(f"Invalid due_date format: {due_date}, use ISO format")
    
    # Prepare update data
    update_data = {
        "project_id": str(project_id)
    }
    
    if title:
        update_data["title"] = title
    
    if description:
        update_data["description"] = description
    
    if status:
        update_data["status"] = status
    
    if assigned_to:
        update_data["assigned_to"] = assigned_to
    
    if due_date:
        update_data["due_date"] = due_date
    
    if custom_attributes:
        update_data["custom_attributes"] = custom_attributes
    
    # Make the API request
    try:
        response = client.patch(f"{API_BASE_PATH}/issues/{issue_id}", json=update_data)
        result = handle_response(response, Issue)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to update issue: {e}")
        raise ToolError(f"Failed to update issue: {e}")