# Tool Registry

Comprehensive registry of all available tools in the CloudCurio ecosystem.

## Categories

### LLM Integration Tools
Located in: `agents/tools/llm_tools.py`

- **llm_completion** - Generate text completions using local or cloud LLMs
  - Supports: Ollama, OpenAI, OpenRouter, Anthropic
  - Use cases: Text generation, code completion, content creation

- **llm_embedding** - Generate text embeddings for semantic search
  - Supports: Ollama (nomic-embed-text)
  - Use cases: Similarity search, document indexing, clustering

### Web Interaction Tools
Located in: `agents/tools/web_tools.py`

- **web_scraper** - Extract content and data from web pages
  - Features: CSS selector support, BeautifulSoup parsing
  - Use cases: Data extraction, content monitoring, research

- **api_client** - Make HTTP requests to REST APIs
  - Methods: GET, POST, PUT, DELETE, PATCH
  - Features: Headers, query params, JSON payloads
  - Use cases: API integration, data fetching, webhooks

- **search_engine** - Search the web using DuckDuckGo
  - Features: No API key required, privacy-focused
  - Use cases: Research, fact-checking, discovery

### File System Tools
Located in: `agents/tools/file_tools.py`

- **file_reader** - Read text content from files
  - Features: Encoding support, size limits
  - Use cases: Configuration reading, log analysis, data loading

- **file_writer** - Write text content to files
  - Features: Write/append modes, auto-create directories
  - Use cases: Report generation, logging, data export

- **directory_tool** - List, create, and manage directories
  - Actions: list, create, delete
  - Features: Recursive listing, glob patterns
  - Use cases: File organization, cleanup, discovery

- **file_search** - Search for files by name and content
  - Search types: name pattern, content search
  - Features: Recursive search, pattern matching
  - Use cases: Code search, log analysis, file discovery

### Data Processing Tools
Located in: `agents/tools/data_tools.py`

- **json_processor** - Parse, validate, and transform JSON data
  - Actions: parse, stringify, validate, query
  - Features: JSON path queries, validation
  - Use cases: API data processing, configuration management

- **data_transform** - Transform, filter, and aggregate data
  - Operations: filter, map, sort, group, aggregate
  - Features: Conditional filtering, field mapping, aggregation functions
  - Use cases: Data analysis, reporting, ETL

- **csv_processor** - Parse and transform CSV data
  - Actions: parse, stringify
  - Features: Header support, delimiter configuration
  - Use cases: Data import/export, spreadsheet processing

### System Monitoring Tools
Located in: `agents/tools/system_tools.py`

- **system_info** - Get system information (OS, CPU, memory, disk)
  - Info types: os, cpu, memory, disk, network
  - Use cases: Diagnostics, capacity planning, monitoring

- **process_monitor** - Monitor running processes and resource usage
  - Actions: list, info, kill
  - Features: Top processes by CPU/memory, process details
  - Use cases: Performance monitoring, troubleshooting

- **resource_monitor** - Monitor CPU, memory, disk, and network usage
  - Features: Time-series sampling, averaging
  - Use cases: Performance analysis, capacity planning

- **health_check** - Check system health and resource availability
  - Features: Configurable thresholds, multi-metric checks
  - Use cases: Alerting, SLA monitoring, diagnostics

### Existing Tools
Located in: `agents/tools/`

- **echo_tool** - Simple echo tool for testing
  - Location: `python/echo_tool.py`

- **database_connector** - Database connection and query execution
  - Location: `database_connector.py`

## Tool Configuration

### Basic Configuration

```yaml
# In agent spec
tools:
  - id: llm_completion
    type: python
    entrypoint: agents/tools/llm_tools.py:llm_completion_tool
    config:
      provider: ollama
      model: qwen2.5-coder
      temperature: 0.7
```

### Advanced Configuration

```yaml
tools:
  - id: web_scraper
    type: python
    entrypoint: agents/tools/web_tools.py:web_scraper_tool
    config:
      timeout: 30
      user_agent: "MyBot/1.0"
      verify_ssl: true

  - id: file_reader
    type: python
    entrypoint: agents/tools/file_tools.py:file_reader_tool
    config:
      base_path: "/data"
      max_file_size: 10485760  # 10MB
```

## Usage Examples

### LLM Completion

```python
from agents.tools.llm_tools import llm_completion_tool

tool = llm_completion_tool({"provider": "ollama", "model": "qwen2.5-coder"})

result = tool.execute(prompt="Write a function to calculate fibonacci numbers", temperature=0.5)
print(result["text"])
```

### Web Scraping

```python
from agents.tools.web_tools import web_scraper_tool

tool = web_scraper_tool()
result = tool.execute(
    url="https://example.com",
    selector="article h2",  # Extract all h2 titles in articles
)
print(result["content"])
```

### Data Processing

```python
from agents.tools.data_tools import data_transform_tool

tool = data_transform_tool()
data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 87},
    {"name": "Charlie", "score": 92},
]

result = tool.execute(
    data=data,
    operation="filter",
    condition={"score": 90},  # Only scores >= 90
)
print(result["result"])
```

### System Monitoring

```python
from agents.tools.system_tools import health_check_tool

tool = health_check_tool()
result = tool.execute(
    thresholds={"cpu_percent": 80.0, "memory_percent": 85.0, "disk_percent": 90.0}
)

if not result["healthy"]:
    print("System health check failed!")
    print(result["checks"])
```

## Tool Development Guidelines

### Creating New Tools

1. **Inherit from base patterns** - Follow existing tool structure
2. **Use Pydantic for config** - Type-safe configuration
3. **Implement execute method** - Standard interface
4. **Return consistent format** - Always include status field
5. **Add factory function** - Enable easy instantiation
6. **Document thoroughly** - Docstrings and examples

### Tool Template

```python
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class MyToolConfig(BaseModel):
    """Configuration for MyTool."""

    param1: str = Field(description="Parameter 1")


class MyTool:
    """Brief description of what the tool does."""

    name: str = "my_tool"
    description: str = "Brief description for agents"

    def __init__(self, config: Optional[MyToolConfig] = None) -> None:
        """Initialize tool."""
        self.config = config or MyToolConfig()

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute tool operation."""
        try:
            # Implementation here
            return {"status": "success", "result": "data"}
        except Exception as e:
            logger.error(f"Tool failed: {e}")
            return {"status": "error", "error": str(e)}


def my_tool(config: Optional[Dict[str, Any]] = None) -> MyTool:
    """Factory function."""
    cfg = MyToolConfig(**config) if config else MyToolConfig()
    return MyTool(cfg)
```

## Best Practices

1. **Error Handling** - Always catch exceptions and return structured errors
2. **Logging** - Use logger for debugging and troubleshooting
3. **Timeouts** - Set reasonable timeouts for network operations
4. **Resource Limits** - Prevent memory/disk exhaustion
5. **Security** - Validate inputs, sanitize file paths
6. **Testing** - Write unit tests for each tool
7. **Documentation** - Clear docstrings and usage examples

## Future Tools

### Planned Additions

- **code_analyzer** - Static code analysis and linting
- **git_tools** - Git operations (clone, commit, push, etc.)
- **image_processor** - Image manipulation and analysis
- **video_processor** - Video editing and transcoding
- **audio_processor** - Audio processing and transcription
- **email_client** - Send and receive emails
- **calendar_tools** - Calendar integration and scheduling
- **notification_tools** - Send notifications (Slack, Discord, etc.)
- **vector_store** - Vector database operations
- **document_parser** - Parse PDFs, Word docs, etc.

## Contributing

To add a new tool:

1. Create the tool module in `agents/tools/`
2. Follow the tool template pattern
3. Add configuration via Pydantic models
4. Update this registry with documentation
5. Add usage examples
6. Write tests in `tests/tools/`
7. Submit PR with tool implementation

## Related Documentation

- [Tool Development Guide](../../docs/TOOL_DEVELOPMENT.md)
- [Agent Development Guide](../../docs/AGENT_DEVELOPMENT.md)
- [API Reference](../../docs/API.md)
