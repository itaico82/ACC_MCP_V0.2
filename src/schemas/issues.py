"""
Issue-related schemas for the ACC Issues API.

This module provides data models and validation for issues in the ACC Issues API.
"""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class IssueStatus(str, Enum):
    """Valid issue statuses in ACC."""
    
    DRAFT = "draft"
    OPEN = "open"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    IN_REVIEW = "in_review"
    NOT_APPROVED = "not_approved"
    IN_DISPUTE = "in_dispute"
    CLOSED = "closed"


class AssigneeType(str, Enum):
    """Valid assignee types in ACC."""
    
    USER = "user"
    COMPANY = "company"
    ROLE = "role"


class IssueBase(BaseModel):
    """Base model for issue data."""
    
    title: str = Field(..., description="Title of the issue (max 100 characters)", max_length=100)
    description: Optional[str] = Field(
        None, description="Detailed description of the issue (max 1000 characters)", max_length=1000
    )
    status: Optional[IssueStatus] = Field(
        None, description="Current status of the issue"
    )
    assigned_to: Optional[str] = Field(
        None, description="ID of the assigned person, company, or role"
    )
    assigned_to_type: Optional[AssigneeType] = Field(
        None, description="Type of the assignee (user, company, role)"
    )
    due_date: Optional[date] = Field(
        None, description="Due date for the issue in ISO 8601 format (YYYY-MM-DD)"
    )
    start_date: Optional[date] = Field(
        None, description="Start date for the issue in ISO 8601 format (YYYY-MM-DD)"
    )
    location_details: Optional[str] = Field(
        None, description="Physical location description (max 250 characters)", max_length=250
    )
    
    @field_validator("assigned_to")
    def validate_assigned_to(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate that assigned_to_type is provided if assigned_to is provided."""
        assigned_to_type = values.get("assigned_to_type")
        if v is not None and assigned_to_type is None:
            raise ValueError("assigned_to_type must be provided when assigned_to is provided")
        return v


class IssueCreate(IssueBase):
    """Model for creating a new issue."""
    
    issue_type_id: Optional[UUID] = Field(
        None, description="ID of the issue type (category)"
    )
    issue_subtype_id: UUID = Field(
        ..., description="ID of the issue subtype (type)"
    )
    custom_attributes: Optional[Dict[str, Any]] = Field(
        None, description="Custom attributes for the issue"
    )


class Issue(IssueBase):
    """Model for a complete issue."""
    
    id: UUID = Field(..., description="Unique identifier of the issue")
    display_id: int = Field(..., description="Display ID of the issue (numerical ID shown in UI)")
    issue_type_id: UUID = Field(..., description="ID of the issue type (category)")
    issue_subtype_id: UUID = Field(..., description="ID of the issue subtype (type)")
    created_by: str = Field(..., description="ID of the user who created the issue")
    created_at: datetime = Field(..., description="Timestamp when the issue was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the issue")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the issue was last updated")
    closed_by: Optional[str] = Field(None, description="ID of the user who closed the issue")
    closed_at: Optional[datetime] = Field(None, description="Timestamp when the issue was closed")
    deleted: bool = Field(False, description="Whether the issue has been deleted")
    custom_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Custom attributes for the issue"
    )
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
        validate_assignment = True


class IssueList(BaseModel):
    """Model for a list of issues with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[Issue] = Field(..., description="List of issues")