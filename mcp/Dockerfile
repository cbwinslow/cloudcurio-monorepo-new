# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for ffmpeg (used by clip_generator, potentially video_analyzer)
# and any other native libraries needed by your Python dependencies.
# This assumes ffmpeg will be used by the wrapped Python scripts.
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# You might want to create a requirements.txt in mcp-servers/media-processing-mcp
# For now, install known direct dependencies
RUN pip install FastMCP requests opencv-python moviepy pydub librosa numpy scipy

# Copy the Python MCP server and the scripts it wraps
# Ensure the parent scripts directory is also copied so imports work
COPY server.py .
COPY ../../scripts ./scripts
COPY ../../episodes ./episodes # Example: if analysis needs to read directly from episodes

# Run the server
# The Python MCP server uses stdio transport by default.
# If you add an HTTP transport, you'd EXPOSE a port and change CMD accordingly.
CMD ["python", "server.py"]
