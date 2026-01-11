"""
Toolsets package for podcast production workflows.

This package provides comprehensive tools for video analysis, audio processing,
content scheduling, and other podcast production tasks.
"""

from .base_tool import BaseTool
from .error_handling import (
    ToolError, ToolConfigError, ToolValidationError,
    VideoAnalysisError, AudioProcessingError,
    SchedulingError, SchedulingConflictError, SchedulingValidationError
)
from .config_loader import ConfigLoader
from .toolset_manager import ToolsetManager

__version__ = "1.0.0"
__author__ = "Podcast Production Team"
__license__ = "MIT"

# Common constants
DEFAULT_CONFIG_PATH = "toolsets_config.json"
DEFAULT_TEMP_DIR = "/tmp/podcast_toolsets"

# Tool categories
VIDEO_TOOLS = ["video_analysis"]
AUDIO_TOOLS = ["audio_processing"]
SCHEDULING_TOOLS = ["content_scheduling"]
MONITORING_TOOLS = ["system_monitoring"]

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "video_analysis": {
        "max_time_seconds": 120,
        "max_memory_mb": 512
    },
    "audio_processing": {
        "max_time_seconds": 300,
        "max_memory_mb": 1024
    },
    "content_scheduling": {
        "max_time_seconds": 60,
        "max_memory_mb": 256
    }
}
