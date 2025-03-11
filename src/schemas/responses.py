"""
Response schemas for the ACC Issues API.

This module provides standardized data models for API responses.
"""

from typing import Dict, Generic, List, Optional, TypeVar, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar('T')


class Pagination(BaseModel):
    """Model for pagination information."""
    
    offset: int = Field(..., description="Current offset in the result set")
    limit: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items in the result set")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_url: Optional[str] = Field(None, description="URL for the next page, if available")
    previous_url: Optional[str] = Field(None, description="URL for the previous page, if available")


class ErrorDetail(BaseModel):
    """Model for detailed error information."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field with error, if applicable")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class APIResponse(GenericModel, Generic[T]):
    """Generic model for API responses."""
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response data, if successful")
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of errors, if not successful")
    message: Optional[str] = Field(None, description="Response message")
    pagination: Optional[Pagination] = Field(None, description="Pagination information, if applicable")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class SuccessResponse(APIResponse[T]):
    """Generic model for successful API responses."""
    
    success: bool = Field(True, const=True, description="Always true for success responses")
    data: T = Field(..., description="Response data")
    errors: None = Field(None, const=True, description="No errors for success responses")


class ErrorResponse(APIResponse[None]):
    """Model for error API responses."""
    
    success: bool = Field(False, const=True, description="Always false for error responses")
    data: None = Field(None, const=True, description="No data for error responses")
    errors: List[ErrorDetail] = Field(..., description="List of errors")


class CreatedResponse(SuccessResponse[Dict[str, Union[str, UUID]]]):
    """Model for API responses after creating a resource."""
    
    message: str = Field("Resource created successfully", description="Success message")


class UpdatedResponse(SuccessResponse[Dict[str, Union[str, UUID]]]):
    """Model for API responses after updating a resource."""
    
    message: str = Field("Resource updated successfully", description="Success message")


class DeletedResponse(SuccessResponse[None]):
    """Model for API responses after deleting a resource."""
    
    message: str = Field("Resource deleted successfully", description="Success message")
    data: None = Field(None, const=True, description="No data for deletion responses")