# Autodesk Construction Cloud (ACC) MCP Server

A Model Context Protocol (MCP) server for Autodesk Construction Cloud Issues API. This server enables AI assistants like Claude to interact with ACC Issues - creating, querying, and managing construction issues.

## Overview

This MCP server follows schema-driven Python development principles to provide a robust interface to the Autodesk Construction Cloud Issues API with the following capabilities:

- Create new issues from natural language descriptions
- Query and filter existing issues
- Get detailed issue information
- Search issues with natural language
- Add comments to issues

## Key Features

- **3-Legged OAuth Authentication**: Securely handles the authentication flow with ACC
- **Smart Field Mapping**: Maps natural language to appropriate issue fields
- **Metadata Caching**: Efficiently caches project metadata to minimize API calls
- **Comprehensive Validation**: Validates all fields according to ACC requirements
- **Error Handling**: Provides clear and actionable error messages

## Prerequisites

- Python 3.10+
- Autodesk Construction Cloud account
- Autodesk Forge application with 3-legged OAuth configured

## Setup

### Environment Configuration

```bash
# OAuth Configuration
ACC_CLIENT_ID=your_client_id
ACC_CLIENT_SECRET=your_client_secret
ACC_REDIRECT_URI=http://127.0.0.1:8000/oauth/callback

# Project Configuration
ACC_PROJECT_ID=your_project_id

# Server Configuration
ACC_API_URL=https://developer.api.autodesk.com/construction/issues/v1
ACC_CALLBACK_PORT=8000
```

### Installation

```bash
# Clone the repository
git clone https://github.com/itaico82/ACC_MCP_V0.2.git
cd ACC_MCP_V0.2

# Create and activate a virtual environment
python -m uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip sync requirements.txt
```

## Usage

```bash
# Start the MCP server
python -m src.main
```

## Development

This project follows schema-driven development principles with a clear separation of concerns:

- `src/schemas/`: Data models generated from OpenAPI schema
- `src/auth/`: OAuth authentication handling
- `src/api/`: ACC API client implementation
- `src/tools/`: MCP tool implementations
- `src/utils/`: Utility functions and helpers

## License

MIT