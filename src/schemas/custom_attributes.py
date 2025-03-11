"""
Custom attributes schemas for the ACC Issues API.

This module provides data models for custom attributes and their mappings to issue types/subtypes.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AttributeType(str, Enum):
    """Valid types for custom attributes."""
    
    TEXT = "text"
    NUMERIC = "numeric"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"


class AttributeDataType(str, Enum):
    """Valid data types for custom attributes."""
    
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"


class SelectOption(BaseModel):
    """Model for a select option in a custom attribute."""
    
    id: UUID = Field(..., description="Unique identifier of the select option")
    value: str = Field(..., description="Display value of the select option")
    color: Optional[str] = Field(None, description="Color code for the select option")
    

class CustomAttributeDefinition(BaseModel):
    """Model for a custom attribute definition."""
    
    id: UUID = Field(..., description="Unique identifier of the custom attribute")
    name: str = Field(..., description="Name of the custom attribute")
    description: Optional[str] = Field(None, description="Description of the custom attribute")
    type: AttributeType = Field(..., description="Type of the custom attribute")
    data_type: AttributeDataType = Field(..., description="Data type of the custom attribute")
    is_required: bool = Field(False, description="Whether the custom attribute is required")
    is_active: bool = Field(True, description="Whether the custom attribute is active")
    options: Optional[List[SelectOption]] = Field(None, description="Options for select/multi-select attributes")
    default_value: Optional[Any] = Field(None, description="Default value for the custom attribute")
    created_by: str = Field(..., description="ID of the user who created the custom attribute")
    created_at: datetime = Field(..., description="Timestamp when the custom attribute was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the custom attribute")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the custom attribute was last updated")
    
    @validator('options')
    def validate_options(cls, v, values):
        """Validate that options are provided for select and multi-select attributes."""
        if values.get('type') in [AttributeType.SELECT, AttributeType.MULTI_SELECT] and not v:
            raise ValueError("Options must be provided for select and multi-select attributes")
        return v
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class CustomAttributeValue(BaseModel):
    """Model for a custom attribute value."""
    
    attribute_id: UUID = Field(..., description="ID of the custom attribute")
    value: Optional[Union[str, int, float, List[str], datetime]] = Field(
        None, description="Value of the custom attribute"
    )


class AttributeMappingEntity(str, Enum):
    """Valid entity types for custom attribute mappings."""
    
    ISSUE_TYPE = "issue_type"
    ISSUE_SUBTYPE = "issue_subtype"


class CustomAttributeMapping(BaseModel):
    """Model for mapping custom attributes to issue types/subtypes."""
    
    id: UUID = Field(..., description="Unique identifier of the mapping")
    attribute_id: UUID = Field(..., description="ID of the custom attribute")
    entity_type: AttributeMappingEntity = Field(..., description="Type of entity")
    entity_id: UUID = Field(..., description="ID of the entity")
    is_required: bool = Field(False, description="Whether the attribute is required for this mapping")
    is_active: bool = Field(True, description="Whether the mapping is active")
    created_by: str = Field(..., description="ID of the user who created the mapping")
    created_at: datetime = Field(..., description="Timestamp when the mapping was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the mapping")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the mapping was last updated")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class CustomAttributeList(BaseModel):
    """Model for a list of custom attributes with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[CustomAttributeDefinition] = Field(..., description="List of custom attributes")


class CustomAttributeMappingList(BaseModel):
    """Model for a list of custom attribute mappings with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[CustomAttributeMapping] = Field(..., description="List of attribute mappings")