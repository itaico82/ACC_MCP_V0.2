"""
Issue status schemas for the ACC Issues API.

This module provides data models for issue statuses and their mappings to issue subtypes.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class StatusCategory(str, Enum):
    """Categories for issue statuses."""
    
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    VOID = "void"


class IssueStatusDefinition(BaseModel):
    """Model for a issue status definition."""
    
    id: UUID = Field(..., description="Unique identifier of the status")
    name: str = Field(..., description="Name of the status")
    description: Optional[str] = Field(None, description="Description of the status")
    category: StatusCategory = Field(..., description="Category of the status")
    color: Optional[str] = Field(None, description="Color code for the status")
    is_active: bool = Field(True, description="Whether the status is active")
    is_default: bool = Field(False, description="Whether the status is the default for its category")
    created_by: str = Field(..., description="ID of the user who created the status")
    created_at: datetime = Field(..., description="Timestamp when the status was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the status")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the status was last updated")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class StatusMapping(BaseModel):
    """Model for mapping statuses to issue subtypes."""
    
    id: UUID = Field(..., description="Unique identifier of the mapping")
    status_id: UUID = Field(..., description="ID of the status")
    subtype_id: UUID = Field(..., description="ID of the issue subtype")
    is_active: bool = Field(True, description="Whether the mapping is active")
    is_default: bool = Field(False, description="Whether this is the default status for the subtype")
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


class StatusTransition(BaseModel):
    """Model for status transitions between statuses."""
    
    id: UUID = Field(..., description="Unique identifier of the transition")
    from_status_id: UUID = Field(..., description="ID of the source status")
    to_status_id: UUID = Field(..., description="ID of the target status")
    subtype_id: UUID = Field(..., description="ID of the issue subtype")
    is_active: bool = Field(True, description="Whether the transition is active")
    created_by: str = Field(..., description="ID of the user who created the transition")
    created_at: datetime = Field(..., description="Timestamp when the transition was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the transition")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the transition was last updated")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class StatusWithTransitions(BaseModel):
    """Model for a status with its allowed transitions."""
    
    status: IssueStatusDefinition = Field(..., description="The status")
    allowed_transitions: List[UUID] = Field(
        default_factory=list, 
        description="List of status IDs this status can transition to"
    )


class SubtypeStatusMapping(BaseModel):
    """Model for all statuses mapped to a subtype with their transitions."""
    
    subtype_id: UUID = Field(..., description="ID of the issue subtype")
    statuses: List[StatusWithTransitions] = Field(
        ..., 
        description="List of statuses with their allowed transitions"
    )


class StatusList(BaseModel):
    """Model for a list of statuses with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[IssueStatusDefinition] = Field(..., description="List of statuses")


class StatusMappingList(BaseModel):
    """Model for a list of status mappings with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[StatusMapping] = Field(..., description="List of status mappings")