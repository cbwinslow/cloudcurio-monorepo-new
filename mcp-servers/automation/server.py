#!/usr/bin/env python3
"""
MCP Automation Server

This server provides comprehensive automation tools for content analysis,
YouTube clip generation, social media distribution, SEO optimization,
and analytics tracking.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('automation_server.log')
    ]
)
logger = logging.getLogger("automation_server")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from automation_tools import (
        ContentAnalyzer,
        YouTubeClipGenerator,
        SocialMediaDistributor,
        SEOOptimizer,
        KeywordResearchTool,
        AnalyticsTracker,
        ContentScheduler
    )
    from mcp_server import MCPServer, MCPTool, MCPResponse
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import aiohttp
    
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    sys.exit(1)

class AutomationServer:
    """
    Main automation server class that integrates all automation tools.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the automation server.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.tools = {}
        self._initialize_tools()
        
        # Initialize MCP server
        self.mcp_server = None
        self._initialize_mcp_server()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="MCP Automation Server",
            description="Comprehensive automation tools for content analysis, YouTube clip generation, social media distribution, SEO optimization, and analytics tracking",
            version="1.0.0"
        )
        
        # Configure CORS
        self._configure_cors()
        
        # Register API endpoints
        self._register_endpoints()
        
        logger.info("Automation server initialized successfully")
    
    def _initialize_tools(self):
        """
        Initialize all automation tools.
        """
        try:
            # Content Analyzer
            self.tools['content_analyzer'] = ContentAnalyzer(self.config)
            logger.info("Initialized Content Analyzer")
            
            # YouTube Clip Generator
            self.tools['clip_generator'] = YouTubeClipGenerator(self.config)
            logger.info("Initialized YouTube Clip Generator")
            
            # Social Media Distributor
            self.tools['social_distributor'] = SocialMediaDistributor(self.config)
            logger.info("Initialized Social Media Distributor")
            
            # SEO Optimizer
            self.tools['seo_optimizer'] = SEOOptimizer(self.config)
            logger.info("Initialized SEO Optimizer")
            
            # Keyword Research Tool
            self.tools['keyword_research'] = KeywordResearchTool(self.config)
            logger.info("Initialized Keyword Research Tool")
            
            # Analytics Tracker
            self.tools['analytics_tracker'] = AnalyticsTracker(self.config)
            logger.info("Initialized Analytics Tracker")
            
            # Content Scheduler
            self.tools['content_scheduler'] = ContentScheduler(self.config)
            logger.info("Initialized Content Scheduler")
            
        except Exception as e:
            logger.error(f"Failed to initialize automation tools: {str(e)}")
            raise
    
    def _initialize_mcp_server(self):
        """
        Initialize the MCP server for tool integration.
        """
        try:
            # Create MCP server instance
            self.mcp_server = MCPServer(
                name="automation_server",
                description="MCP Automation Server for content automation tasks"
            )
            
            # Register MCP tools
            self._register_mcp_tools()
            
            logger.info("Initialized MCP Server")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {str(e)}")
            raise
    
    def _register_mcp_tools(self):
        """
        Register all automation tools as MCP tools.
        """
        try:
            # Content Analysis Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="analyze_content",
                    description="Analyze content for SEO, engagement, and optimization opportunities",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_url": {
                                "type": "string",
                                "description": "URL of content to analyze"
                            },
                            "content_type": {
                                "type": "string",
                                "description": "Type of content (video, audio, text, image)",
                                "enum": ["video", "audio", "text", "image"],
                                "default": "video"
                            },
                            "platform": {
                                "type": "string",
                                "description": "Target platform for optimization",
                                "enum": ["youtube", "website", "twitter", "instagram", "facebook", "tiktok"],
                                "default": "youtube"
                            }
                        },
                        "required": ["content_url"]
                    },
                    handler=self._handle_analyze_content
                )
            )
            
            # YouTube Clip Generation Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="generate_youtube_clips",
                    description="Generate optimized YouTube clips from source video",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": "URL of source video"
                            },
                            "clip_count": {
                                "type": "integer",
                                "description": "Number of clips to generate",
                                "minimum": 1,
                                "maximum": 20,
                                "default": 5
                            },
                            "clip_duration": {
                                "type": "integer",
                                "description": "Target duration per clip in seconds",
                                "minimum": 15,
                                "maximum": 120,
                                "default": 60
                            },
                            "optimize_for": {
                                "type": "string",
                                "description": "Optimization goal",
                                "enum": ["engagement", "views", "conversion"],
                                "default": "engagement"
                            }
                        },
                        "required": ["video_url"]
                    },
                    handler=self._handle_generate_clips
                )
            )
            
            # Social Media Distribution Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="distribute_content",
                    description="Distribute content to social media platforms",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_id": {
                                "type": "string",
                                "description": "ID of content to distribute"
                            },
                            "platforms": {
                                "type": "array",
                                "description": "List of target platforms",
                                "items": {
                                    "type": "string",
                                    "enum": ["twitter", "instagram", "facebook", "tiktok", "youtube", "linkedin"]
                                },
                                "default": ["twitter", "instagram", "youtube"]
                            },
                            "schedule_time": {
                                "type": "string",
                                "description": "Optional schedule time (ISO format)",
                                "format": "date-time"
                            },
                            "custom_message": {
                                "type": "string",
                                "description": "Optional custom message for distribution"
                            }
                        },
                        "required": ["content_id"]
                    },
                    handler=self._handle_distribute_content
                )
            )
            
            # SEO Optimization Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="optimize_seo",
                    description="Optimize content for SEO",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_url": {
                                "type": "string",
                                "description": "URL of content to optimize"
                            },
                            "target_keywords": {
                                "type": "array",
                                "description": "Optional list of target keywords",
                                "items": {"type": "string"}
                            },
                            "platform": {
                                "type": "string",
                                "description": "Target platform",
                                "enum": ["website", "youtube", "twitter", "instagram"],
                                "default": "website"
                            }
                        },
                        "required": ["content_url"]
                    },
                    handler=self._handle_optimize_seo
                )
            )
            
            # Keyword Research Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="research_keywords",
                    description="Perform keyword research for SEO optimization",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "seed_keywords": {
                                "type": "array",
                                "description": "List of seed keywords",
                                "items": {"type": "string"}
                            },
                            "content_url": {
                                "type": "string",
                                "description": "URL of content to analyze"
                            },
                            "platform": {
                                "type": "string",
                                "description": "Target platform",
                                "enum": ["website", "youtube", "twitter", "instagram"],
                                "default": "website"
                            }
                        },
                        "required": ["seed_keywords"]
                    },
                    handler=self._handle_research_keywords
                )
            )
            
            # Analytics Tracking Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="track_analytics",
                    description="Track content performance across platforms",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_id": {
                                "type": "string",
                                "description": "ID of content to track"
                            },
                            "platforms": {
                                "type": "array",
                                "description": "Optional list of platforms to track",
                                "items": {
                                    "type": "string",
                                    "enum": ["google_analytics", "youtube", "twitter", "instagram"]
                                }
                            },
                            "metrics": {
                                "type": "array",
                                "description": "Optional list of specific metrics to track",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["content_id"]
                    },
                    handler=self._handle_track_analytics
                )
            )
            
            # Content Scheduling Tool
            self.mcp_server.register_tool(
                MCPTool(
                    name="schedule_content",
                    description="Determine optimal scheduling times for content",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_id": {
                                "type": "string",
                                "description": "ID of content to schedule"
                            },
                            "platforms": {
                                "type": "array",
                                "description": "List of target platforms",
                                "items": {
                                    "type": "string",
                                    "enum": ["twitter", "instagram", "facebook", "tiktok", "youtube", "linkedin"]
                                },
                                "default": ["twitter", "instagram", "youtube"]
                            },
                            "content_type": {
                                "type": "string",
                                "description": "Type of content",
                                "enum": ["video", "image", "text", "link"],
                                "default": "video"
                            }
                        },
                        "required": ["content_id"]
                    },
                    handler=self._handle_schedule_content
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to register MCP tools: {str(e)}")
            raise
    
    def _configure_cors(self):
        """
        Configure CORS middleware for the FastAPI app.
        """
        try:
            cors_config = self.config.get('cors', {})
            allow_origins = cors_config.get('allow_origins', ["*"])
            allow_methods = cors_config.get('allow_methods', ["*"])
            allow_headers = cors_config.get('allow_headers', ["*"])
            
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=allow_origins,
                allow_credentials=True,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
            )
            
            logger.info("Configured CORS middleware")
            
        except Exception as e:
            logger.error(f"Failed to configure CORS: {str(e)}")
            raise
    
    def _register_endpoints(self):
        """
        Register FastAPI endpoints for the automation server.
        """
        try:
            # Health check endpoint
            @self.app.get("/health")
            async def health_check():
                """Health check endpoint."""
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "tools_initialized": len(self.tools),
                    "mcp_tools_registered": len(self.mcp_server.tools) if self.mcp_server else 0
                }
            
            # Content analysis endpoint
            @self.app.post("/api/analyze")
            async def analyze_content_endpoint(request: Request):
                """Content analysis endpoint."""
                try:
                    data = await request.json()
                    return self._handle_analyze_content(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Clip generation endpoint
            @self.app.post("/api/generate-clips")
            async def generate_clips_endpoint(request: Request):
                """YouTube clip generation endpoint."""
                try:
                    data = await request.json()
                    return self._handle_generate_clips(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Content distribution endpoint
            @self.app.post("/api/distribute")
            async def distribute_content_endpoint(request: Request):
                """Content distribution endpoint."""
                try:
                    data = await request.json()
                    return self._handle_distribute_content(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # SEO optimization endpoint
            @self.app.post("/api/optimize-seo")
            async def optimize_seo_endpoint(request: Request):
                """SEO optimization endpoint."""
                try:
                    data = await request.json()
                    return self._handle_optimize_seo(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Keyword research endpoint
            @self.app.post("/api/research-keywords")
            async def research_keywords_endpoint(request: Request):
                """Keyword research endpoint."""
                try:
                    data = await request.json()
                    return self._handle_research_keywords(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Analytics tracking endpoint
            @self.app.post("/api/track-analytics")
            async def track_analytics_endpoint(request: Request):
                """Analytics tracking endpoint."""
                try:
                    data = await request.json()
                    return self._handle_track_analytics(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Content scheduling endpoint
            @self.app.post("/api/schedule-content")
            async def schedule_content_endpoint(request: Request):
                """Content scheduling endpoint."""
                try:
                    data = await request.json()
                    return self._handle_schedule_content(data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            # MCP server endpoint
            @self.app.post("/mcp/execute")
            async def mcp_execute_endpoint(request: Request):
                """MCP tool execution endpoint."""
                try:
                    data = await request.json()
                    if not self.mcp_server:
                        raise HTTPException(status_code=500, detail="MCP server not initialized")
                    
                    result = await self.mcp_server.execute_tool(
                        data.get('tool_name'),
                        data.get('parameters', {})
                    )
                    return result
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            logger.info("Registered FastAPI endpoints")
            
        except Exception as e:
            logger.error(f"Failed to register endpoints: {str(e)}")
            raise
    
    # MCP Tool Handlers
    
    async def _handle_analyze_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content analysis requests.
        """
        try:
            content_url = params.get('content_url')
            content_type = params.get('content_type', 'video')
            platform = params.get('platform', 'youtube')
            
            if not content_url:
                raise ValueError("content_url is required")
            
            analyzer = self.tools['content_analyzer']
            result = analyzer.analyze(content_url, content_type, platform)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_generate_clips(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle YouTube clip generation requests.
        """
        try:
            video_url = params.get('video_url')
            clip_count = params.get('clip_count', 5)
            clip_duration = params.get('clip_duration', 60)
            optimize_for = params.get('optimize_for', 'engagement')
            
            if not video_url:
                raise ValueError("video_url is required")
            
            generator = self.tools['clip_generator']
            result = generator.generate_clips(video_url, clip_count, clip_duration, optimize_for)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Clip generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_distribute_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content distribution requests.
        """
        try:
            content_id = params.get('content_id')
            platforms = params.get('platforms', ['twitter', 'instagram', 'youtube'])
            schedule_time = params.get('schedule_time')
            custom_message = params.get('custom_message')
            
            if not content_id:
                raise ValueError("content_id is required")
            
            distributor = self.tools['social_distributor']
            result = distributor.distribute(content_id, platforms, schedule_time, custom_message)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content distribution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_optimize_seo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle SEO optimization requests.
        """
        try:
            content_url = params.get('content_url')
            target_keywords = params.get('target_keywords', [])
            platform = params.get('platform', 'website')
            
            if not content_url:
                raise ValueError("content_url is required")
            
            optimizer = self.tools['seo_optimizer']
            result = optimizer.optimize(content_url, target_keywords, platform)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_research_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle keyword research requests.
        """
        try:
            seed_keywords = params.get('seed_keywords', [])
            content_url = params.get('content_url')
            platform = params.get('platform', 'website')
            
            if not seed_keywords:
                raise ValueError("seed_keywords is required")
            
            researcher = self.tools['keyword_research']
            result = researcher.research(seed_keywords, content_url, platform)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_track_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analytics tracking requests.
        """
        try:
            content_id = params.get('content_id')
            platforms = params.get('platforms')
            metrics = params.get('metrics')
            
            if not content_id:
                raise ValueError("content_id is required")
            
            tracker = self.tools['analytics_tracker']
            result = tracker.track(content_id, platforms, metrics)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics tracking failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _handle_schedule_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content scheduling requests.
        """
        try:
            content_id = params.get('content_id')
            platforms = params.get('platforms', ['twitter', 'instagram', 'youtube'])
            content_type = params.get('content_type', 'video')
            
            if not content_id:
                raise ValueError("content_id is required")
            
            scheduler = self.tools['content_scheduler']
            result = scheduler.schedule_content(content_id, platforms, content_type)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the automation server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        try:
            logger.info(f"Starting automation server on {host}:{port}")
            
            # Run FastAPI server
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
        except Exception as e:
            logger.error(f"Server failed to start: {str(e)}")
            raise
    
    async def shutdown(self):
        """
        Gracefully shutdown the automation server.
        """
        try:
            logger.info("Shutting down automation server...")
            
            # Clean up resources
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'shutdown'):
                    try:
                        await tool.shutdown()
                    except:
                        pass
            
            logger.info("Automation server shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown failed: {str(e)}")
            raise

class MCPServer:
    """
    MCP (Model Context Protocol) server for tool integration.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the MCP server.
        
        Args:
            name: Server name
            description: Server description
        """
        self.name = name
        self.description = description
        self.tools = {}
    
    def register_tool(self, tool: 'MCPTool'):
        """
        Register an MCP tool.
        
        Args:
            tool: MCPTool instance to register
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Parameters for tool execution
            
        Returns:
            Dictionary containing execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            tool = self.tools[tool_name]
            result = await tool.handler(parameters)
            
            return {
                "status": "success",
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"MCP tool execution failed: {str(e)}")
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

class MCPTool:
    """
    MCP tool definition.
    """
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], handler: callable):
        """
        Initialize an MCP tool.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool input
            handler: Function to handle tool execution
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

class MCPResponse:
    """
    MCP response container.
    """
    
    def __init__(self, status: str, result: Optional[Dict[str, Any]] = None, 
                 error: Optional[str] = None):
        """
        Initialize an MCP response.
        
        Args:
            status: Response status
            result: Optional result data
            error: Optional error message
        """
        self.status = status
        self.result = result
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary.
        """
        response_dict = {
            "status": self.status,
            "timestamp": self.timestamp
        }
        
        if self.result:
            response_dict["result"] = self.result
        
        if self.error:
            response_dict["error"] = self.error
        
        return response_dict

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load server configuration from file.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
        
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_path} not found, using defaults")
        return get_default_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """
    Get default server configuration.
    """
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False
        },
        "cors": {
            "allow_origins": ["*"],
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        },
        "youtube_api_key": None,
        "google_analytics": {
            "enabled": False,
            "view_id": None,
            "credentials": None
        },
        "social_media_platforms": {
            "twitter": {
                "enabled": False,
                "api_key": None,
                "api_secret": None,
                "access_token": None,
                "access_token_secret": None
            },
            "instagram": {
                "enabled": False,
                "access_token": None,
                "business_id": None
            },
            "facebook": {
                "enabled": False,
                "access_token": None,
                "page_id": None
            },
            "tiktok": {
                "enabled": False,
                "access_token": None
            },
            "youtube": {
                "enabled": False,
                "api_key": None
            },
            "linkedin": {
                "enabled": False,
                "access_token": None
            }
        },
        "platform_apis": {
            "youtube": {
                "enabled": False,
                "api_key": None
            },
            "twitter": {
                "enabled": False,
                "api_key": None
            },
            "instagram": {
                "enabled": False,
                "access_token": None
            }
        },
        "platform_scheduling_data": {
            "youtube": {
                "video": [
                    {"day": "Tuesday", "time": "14:00", "score": 0.85},
                    {"day": "Wednesday", "time": "15:00", "score": 0.82},
                    {"day": "Thursday", "time": "13:00", "score": 0.78}
                ]
            },
            "twitter": {
                "video": [
                    {"day": "Monday", "time": "08:00", "score": 0.88},
                    {"day": "Wednesday", "time": "12:00", "score": 0.85},
                    {"day": "Friday", "time": "17:00", "score": 0.82}
                ]
            },
            "instagram": {
                "video": [
                    {"day": "Tuesday", "time": "11:00", "score": 0.90},
                    {"day": "Thursday", "time": "14:00", "score": 0.88},
                    {"day": "Saturday", "time": "09:00", "score": 0.85}
                ]
            }
        },
        "timezone": "UTC"
    }

def main():
    """
    Main entry point for the automation server.
    """
    try:
        # Load configuration
        config = load_config()
        
        # Create and run server
        server = AutomationServer(config)
        
        # Handle shutdown signals
        def handle_shutdown(signum, frame):
            logger.info(f"Received shutdown signal {signum}")
            asyncio.create_task(server.shutdown())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Run server
        server.run(
            host=config['server']['host'],
            port=config['server']['port']
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()