"""
Issue type schemas for the ACC Issues API.

This module provides data models for issue types and subtypes in the ACC Issues API.
Note the terminology difference between the API and UI:
- API "type" = UI "category"
- API "subtype" = UI "type"
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class IssueSubtype(BaseModel):
    """Model for an issue subtype (UI: "type")."""
    
    id: UUID = Field(..., description="Unique identifier of the issue subtype")
    title: str = Field(..., description="Name of the issue subtype")
    description: Optional[str] = Field(None, description="Description of the issue subtype")
    is_active: bool = Field(True, description="Whether the issue subtype is active")
    created_by: str = Field(..., description="ID of the user who created the issue subtype")
    created_at: datetime = Field(..., description="Timestamp when the issue subtype was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the issue subtype")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the issue subtype was last updated")
    deleted_by: Optional[str] = Field(None, description="ID of the user who deleted the issue subtype")
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the issue subtype was deleted")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class IssueType(BaseModel):
    """Model for an issue type (UI: "category")."""
    
    id: UUID = Field(..., description="Unique identifier of the issue type")
    title: str = Field(..., description="Name of the issue type")
    description: Optional[str] = Field(None, description="Description of the issue type")
    is_active: bool = Field(True, description="Whether the issue type is active")
    subtypes: Optional[List[IssueSubtype]] = Field(None, description="Subtypes belonging to this type")
    created_by: str = Field(..., description="ID of the user who created the issue type")
    created_at: datetime = Field(..., description="Timestamp when the issue type was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the issue type")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the issue type was last updated")
    deleted_by: Optional[str] = Field(None, description="ID of the user who deleted the issue type")
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the issue type was deleted")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class IssueTypeList(BaseModel):
    """Model for a list of issue types with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[IssueType] = Field(..., description="List of issue types")