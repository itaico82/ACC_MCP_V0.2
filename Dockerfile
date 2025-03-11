FROM python:3.10-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && apt-get clean

# Install uv
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port for OAuth callback and service
EXPOSE 8000

# Environment setup (override in container with environment variables)
ENV ACC_API_URL=https://developer.api.autodesk.com/construction/issues/v1
ENV ACC_CALLBACK_PORT=8000

# Healthcheck to verify server is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the MCP server
CMD ["python", "-m", "src.main"]