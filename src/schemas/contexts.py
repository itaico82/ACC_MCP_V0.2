"""
Context schemas for the ACC Issues API.

This module provides data models for project and account contexts in the ACC Issues API.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class AccountContext(BaseModel):
    """Model for an account context."""
    
    id: UUID = Field(..., description="Unique identifier of the account")
    name: str = Field(..., description="Name of the account")
    key: str = Field(..., description="Key identifier for the account")
    is_active: bool = Field(True, description="Whether the account is active")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class ProjectRole(BaseModel):
    """Model for a project role."""
    
    id: UUID = Field(..., description="Unique identifier of the role")
    name: str = Field(..., description="Name of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    permissions: List[str] = Field(default_factory=list, description="List of permission keys for the role")


class ProjectMember(BaseModel):
    """Model for a project member."""
    
    id: UUID = Field(..., description="Unique identifier of the member")
    user_id: str = Field(..., description="User ID of the member")
    name: str = Field(..., description="Name of the member")
    email: str = Field(..., description="Email of the member")
    role_id: UUID = Field(..., description="ID of the member's role in the project")
    is_active: bool = Field(True, description="Whether the member is active in the project")


class ProjectLocation(BaseModel):
    """Model for a project location."""
    
    id: UUID = Field(..., description="Unique identifier of the location")
    name: str = Field(..., description="Name of the location")
    description: Optional[str] = Field(None, description="Description of the location")
    is_active: bool = Field(True, description="Whether the location is active")


class ProjectCompany(BaseModel):
    """Model for a project company."""
    
    id: UUID = Field(..., description="Unique identifier of the company")
    name: str = Field(..., description="Name of the company")
    description: Optional[str] = Field(None, description="Description of the company")
    is_active: bool = Field(True, description="Whether the company is active")


class ProjectContext(BaseModel):
    """Model for a project context."""
    
    id: UUID = Field(..., description="Unique identifier of the project")
    name: str = Field(..., description="Name of the project")
    key: str = Field(..., description="Key identifier for the project")
    description: Optional[str] = Field(None, description="Description of the project")
    account_id: UUID = Field(..., description="ID of the account the project belongs to")
    start_date: Optional[datetime] = Field(None, description="Start date of the project")
    end_date: Optional[datetime] = Field(None, description="End date of the project")
    timezone: str = Field("UTC", description="Timezone of the project")
    status: str = Field(..., description="Status of the project")
    is_active: bool = Field(True, description="Whether the project is active")
    created_by: str = Field(..., description="ID of the user who created the project")
    created_at: datetime = Field(..., description="Timestamp when the project was created")
    updated_by: Optional[str] = Field(None, description="ID of the user who last updated the project")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the project was last updated")
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class ProjectContextWithDetails(ProjectContext):
    """Model for a project context with detailed information."""
    
    roles: Optional[List[ProjectRole]] = Field(None, description="Roles defined in the project")
    members: Optional[List[ProjectMember]] = Field(None, description="Members of the project")
    locations: Optional[List[ProjectLocation]] = Field(None, description="Locations in the project")
    companies: Optional[List[ProjectCompany]] = Field(None, description="Companies involved in the project")


class ProjectList(BaseModel):
    """Model for a list of projects with pagination."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    results: List[ProjectContext] = Field(..., description="List of projects")