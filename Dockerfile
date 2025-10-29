# LiveKit Azure Live Interpreter Agent Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy plugin source code
COPY livekit-plugins/livekit-plugins-azure /app/livekit-plugins-azure

# Install the plugin
RUN pip install --no-cache-dir /app/livekit-plugins-azure

# Copy requirements.txt
COPY requirements.txt /app/requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy example agents
COPY examples /app/examples

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose port for agent (if needed)
EXPOSE 8080

# Default command - run the multi-language meeting agent
CMD ["python", "examples/multi_language_meeting.py", "start"]
