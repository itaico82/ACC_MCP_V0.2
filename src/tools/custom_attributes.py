"""
Custom attributes tools for the ACC Issues API.

This module provides MCP tools for working with custom attributes and their mappings.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from uuid import UUID

from src.schemas.custom_attributes import (
    AttributeMappingEntity,
    CustomAttribute,
    CustomAttributeList,
    CustomAttributeMapping,
    CustomAttributeMappingList
)
from src.tools.base import (
    ToolError,
    get_api_client,
    handle_response,
    require_project_context
)


logger = logging.getLogger(__name__)
API_BASE_PATH = "/api/v1"


def list_custom_attributes(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    data_type: Optional[str] = None
) -> Dict:
    """List custom attributes for the current project.
    
    Args:
        page: Page number for pagination
        limit: Number of items per page
        search: Optional search term
        is_active: Filter by active status
        data_type: Filter by data type
        
    Returns:
        Paginated list of custom attributes
        
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
        
    if data_type:
        params["data_type"] = data_type
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/custom-attributes", params=params)
        result = handle_response(response, CustomAttributeList)
        return result.dict() if result else {"results": [], "pagination": {}}
    except Exception as e:
        logger.error(f"Failed to list custom attributes: {e}")
        raise ToolError(f"Failed to list custom attributes: {e}")


def get_custom_attribute(attribute_id: str) -> Dict:
    """Get a custom attribute by ID.
    
    Args:
        attribute_id: ID of the custom attribute to get
        
    Returns:
        Custom attribute details
        
    Raises:
        ToolError: If the API request fails or no project is set
    """
    client = get_api_client()
    project_id = require_project_context()
    
    # Validate UUID
    try:
        UUID(attribute_id)
    except ValueError:
        raise ToolError(f"Invalid custom attribute ID: {attribute_id}")
    
    # Build query parameters
    params = {
        "project_id": str(project_id)
    }
    
    # Make the API request
    try:
        response = client.get(f"{API_BASE_PATH}/custom-attributes/{attribute_id}", params=params)
        result = handle_response(response, CustomAttribute)
        return result.dict() if result else {}
    except Exception as e:
        logger.error(f"Failed to get custom attribute: {e}")
        raise ToolError(f"Failed to get custom attribute: {e}")


def get_custom_attributes_for_type(type_id: str) -> Dict:
    """Get custom attributes mapped to an issue type.
    
    Args:
        type_id: ID of the issue type
        
    Returns:
        List of custom attributes for the issue type
        
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
        "project_id": str(project_id),
        "entity_type": AttributeMappingEntity.ISSUE_TYPE,
        "entity_id": type_id
    }
    
    # Make the API request
    try:
        # First, get all mappings for this type
        response = client.get(f"{API_BASE_PATH}/custom-attribute-mappings", params=params)
        mappings_result = handle_response(response, CustomAttributeMappingList)
        
        if not mappings_result or not mappings_result.results:
            return {"type_id": type_id, "attributes": []}
        
        # For each mapping, get the full attribute details
        attribute_ids = [mapping.attribute_id for mapping in mappings_result.results]
        attributes = []
        
        for attr_id in attribute_ids:
            try:
                attr_response = client.get(
                    f"{API_BASE_PATH}/custom-attributes/{attr_id}", 
                    params={"project_id": str(project_id)}
                )
                attr_result = handle_response(response, CustomAttribute)
                if attr_result:
                    attributes.append(attr_result.dict())
            except Exception as inner_e:
                logger.warning(f"Failed to get attribute {attr_id}: {inner_e}")
        
        return {
            "type_id": type_id,
            "attributes": attributes
        }
    except Exception as e:
        logger.error(f"Failed to get custom attributes for type: {e}")
        raise ToolError(f"Failed to get custom attributes for type: {e}")


def get_custom_attributes_for_subtype(subtype_id: str) -> Dict:
    """Get custom attributes mapped to an issue subtype.
    
    Args:
        subtype_id: ID of the issue subtype
        
    Returns:
        List of custom attributes for the issue subtype
        
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
        "project_id": str(project_id),
        "entity_type": AttributeMappingEntity.ISSUE_SUBTYPE,
        "entity_id": subtype_id
    }
    
    # Make the API request
    try:
        # First, get all mappings for this subtype
        response = client.get(f"{API_BASE_PATH}/custom-attribute-mappings", params=params)
        mappings_result = handle_response(response, CustomAttributeMappingList)
        
        if not mappings_result or not mappings_result.results:
            return {"subtype_id": subtype_id, "attributes": []}
        
        # For each mapping, get the full attribute details
        attribute_ids = [mapping.attribute_id for mapping in mappings_result.results]
        attributes = []
        
        for attr_id in attribute_ids:
            try:
                attr_response = client.get(
                    f"{API_BASE_PATH}/custom-attributes/{attr_id}", 
                    params={"project_id": str(project_id)}
                )
                attr_result = handle_response(attr_response, CustomAttribute)
                if attr_result:
                    attributes.append(attr_result.dict())
            except Exception as inner_e:
                logger.warning(f"Failed to get attribute {attr_id}: {inner_e}")
        
        return {
            "subtype_id": subtype_id,
            "attributes": attributes
        }
    except Exception as e:
        logger.error(f"Failed to get custom attributes for subtype: {e}")
        raise ToolError(f"Failed to get custom attributes for subtype: {e}")