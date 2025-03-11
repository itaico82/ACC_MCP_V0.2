"""
MCP tools for the ACC Issues API.

This package provides the Model Context Protocol (MCP) tools for interacting with the ACC Issues API.
"""

from src.tools.issues import (
    list_issues,
    get_issue,
    create_issue,
    update_issue
)

from src.tools.issue_types import (
    list_issue_types,
    get_issue_type,
    list_issue_subtypes,
    get_issue_subtype
)

from src.tools.statuses import (
    list_statuses,
    get_status,
    get_statuses_for_subtype
)

from src.tools.custom_attributes import (
    list_custom_attributes,
    get_custom_attribute,
    get_custom_attributes_for_type,
    get_custom_attributes_for_subtype
)

from src.tools.contexts import (
    list_projects,
    get_project,
    set_current_project
)

__all__ = [
    # Issue tools
    "list_issues",
    "get_issue",
    "create_issue",
    "update_issue",
    
    # Issue type tools
    "list_issue_types",
    "get_issue_type",
    "list_issue_subtypes",
    "get_issue_subtype",
    
    # Status tools
    "list_statuses",
    "get_status",
    "get_statuses_for_subtype",
    
    # Custom attribute tools
    "list_custom_attributes",
    "get_custom_attribute",
    "get_custom_attributes_for_type",
    "get_custom_attributes_for_subtype",
    
    # Context tools
    "list_projects",
    "get_project",
    "set_current_project",
]