"""
Data models for the ACC Issues API.

This package provides data models and validation for the ACC Issues API.
"""

# Issue models
from src.schemas.issues import (
    Issue, 
    IssueBase, 
    IssueCreate, 
    IssueList,
    IssueStatus as IssueStatusEnum,
    AssigneeType
)

# Issue type models
from src.schemas.issue_types import (
    IssueType, 
    IssueSubtype,
    IssueTypeList
)

# Custom attribute models
from src.schemas.custom_attributes import (
    AttributeType,
    AttributeDataType,
    SelectOption,
    CustomAttributeDefinition as CustomAttribute,
    CustomAttributeValue,
    CustomAttributeMapping,
    AttributeMappingEntity,
    CustomAttributeList,
    CustomAttributeMappingList
)

# Status models
from src.schemas.statuses import (
    StatusCategory,
    IssueStatusDefinition as IssueStatus,
    StatusMapping,
    StatusTransition,
    StatusWithTransitions,
    SubtypeStatusMapping,
    StatusList,
    StatusMappingList
)

# Context models
from src.schemas.contexts import (
    AccountContext,
    ProjectRole,
    ProjectMember,
    ProjectLocation,
    ProjectCompany,
    ProjectContext,
    ProjectContextWithDetails,
    ProjectList
)

# Response models
from src.schemas.responses import (
    Pagination,
    ErrorDetail,
    APIResponse,
    SuccessResponse,
    ErrorResponse,
    CreatedResponse,
    UpdatedResponse,
    DeletedResponse
)

__all__ = [
    # Issue models
    "Issue",
    "IssueBase",
    "IssueCreate",
    "IssueList",
    "IssueStatusEnum",
    "AssigneeType",
    
    # Issue type models
    "IssueType",
    "IssueSubtype",
    "IssueTypeList",
    
    # Custom attribute models
    "AttributeType",
    "AttributeDataType",
    "SelectOption",
    "CustomAttribute",
    "CustomAttributeValue",
    "CustomAttributeMapping",
    "AttributeMappingEntity",
    "CustomAttributeList",
    "CustomAttributeMappingList",
    
    # Status models
    "StatusCategory",
    "IssueStatus",
    "StatusMapping",
    "StatusTransition",
    "StatusWithTransitions",
    "SubtypeStatusMapping",
    "StatusList",
    "StatusMappingList",
    
    # Context models
    "AccountContext",
    "ProjectRole",
    "ProjectMember",
    "ProjectLocation",
    "ProjectCompany",
    "ProjectContext",
    "ProjectContextWithDetails",
    "ProjectList",
    
    # Response models
    "Pagination",
    "ErrorDetail",
    "APIResponse",
    "SuccessResponse",
    "ErrorResponse",
    "CreatedResponse",
    "UpdatedResponse",
    "DeletedResponse",
]