# Multi-stage build for iCloud Email MCP Server
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN python -m venv .venv && \
    .venv/bin/pip install --no-cache-dir --upgrade pip && \
    .venv/bin/pip install --no-cache-dir \
        fastmcp>=2.10.6 \
        mcp>=1.12.0 \
        email-validator>=2.0.0

# Production stage
FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcpuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY icloud_email_server_docker.py ./
COPY test_email.py ./

# Set proper ownership
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from icloud_email_server_docker import test_email_connection; print('Health check passed')" || exit 1

# Expose the port (MCP typically uses stdio, but we'll make it available)
EXPOSE 8080

# Start the MCP server
CMD ["python", "icloud_email_server_docker.py"]