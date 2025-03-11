"""
Configuration settings for the ACC MCP Server.

This module loads and validates configuration settings from environment variables.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project settings
    project_name: str = "ACC MCP Server"
    version: str = "0.2.0"
    
    # OAuth configuration
    acc_client_id: str = Field(..., description="Autodesk Forge client ID")
    acc_client_secret: str = Field(..., description="Autodesk Forge client secret")
    acc_redirect_uri: str = Field(
        "http://127.0.0.1:8000/oauth/callback", 
        description="OAuth callback URL"
    )
    acc_callback_port: int = Field(8000, description="Port for OAuth callback server")
    
    # Project configuration
    acc_project_id: str = Field(..., description="ACC project ID")
    
    # API settings
    acc_api_url: str = Field(
        "https://developer.api.autodesk.com/construction/issues/v1",
        description="ACC Issues API base URL"
    )
    
    # Cache settings
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    token_cache_path: Optional[str] = Field(
        None, description="Path to token cache file"
    )
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    def get_token_cache_path(self) -> Path:
        """Get the path to the token cache file."""
        if self.token_cache_path:
            return Path(self.token_cache_path)
        
        # Default to a token-cache.json file in the project root
        root_dir = Path(__file__).parent.parent
        return root_dir / "token-cache.json"


# Create a global settings instance
settings = Settings()