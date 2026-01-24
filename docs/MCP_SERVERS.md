# Model Context Protocol (MCP) Servers Guide

Integration guide for Model Context Protocol servers in CloudCurio.

## Table of Contents

- [Overview](#overview)
- [Available MCP Servers](#available-mcp-servers)
- [Configuration](#configuration)
- [Usage](#usage)
- [Custom MCP Servers](#custom-mcp-servers)

## Overview

Model Context Protocol (MCP) provides standardized interfaces for AI tools and integrations. CloudCurio includes MCP servers for automation and media processing.

### MCP Architecture

```
Agent → MCP Client → MCP Server → Tools/Resources
  ↓         ↓            ↓              ↓
 Spec   Protocol    Standard API   Implementation
```

## Available MCP Servers

### Automation Server

**Location**: `mcp-servers/automation/`

Provides automation tools:
- File operations
- Process management
- System commands
- Scheduling

**Tools:**
- `execute_command` - Run system commands
- `schedule_task` - Schedule automated tasks
- `file_watch` - Monitor file changes
- `process_monitor` - Monitor processes

**Usage:**

```yaml
# In agent spec
tools:
  - id: execute_command
    type: mcp
    entrypoint: automation:execute_command
    config:
      timeout: 30
      shell: bash
```

### Media Server

**Location**: `mcp-servers/media/`

Provides media processing tools:
- Audio processing
- Video editing
- Image manipulation
- Format conversion

**Tools:**
- `process_audio` - Audio editing and mixing
- `process_video` - Video editing and effects
- `convert_format` - Media format conversion
- `extract_audio` - Extract audio from video

**Usage:**

```yaml
# In agent spec
tools:
  - id: process_video
    type: mcp
    entrypoint: media:process_video
    config:
      quality: high
      format: mp4
```

## Configuration

### Server Configuration

`mcp-servers/config.json`:

```json
{
  "servers": {
    "automation": {
      "command": "node",
      "args": ["mcp-servers/automation/index.js"],
      "env": {
        "LOG_LEVEL": "info"
      }
    },
    "media": {
      "command": "node",
      "args": ["mcp-servers/media/index.js"],
      "env": {
        "FFMPEG_PATH": "/usr/bin/ffmpeg",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Environment Variables

```bash
# MCP Server paths
export MCP_SERVER_AUTOMATION="mcp-servers/automation"
export MCP_SERVER_MEDIA="mcp-servers/media"

# Tool-specific configuration
export FFMPEG_PATH="/usr/bin/ffmpeg"
export IMAGEMAGICK_PATH="/usr/bin/convert"
```

## Usage

### From Python

```python
from cbw_foundry.mcp import MCPClient

# Connect to MCP server
client = MCPClient(server="automation")

# List available tools
tools = client.list_tools()

# Execute tool
result = client.execute_tool(
    tool_name="execute_command",
    params={"command": "ls -la", "timeout": 10}
)

print(result)
```

### From Agent Specs

```yaml
api_version: v1
kind: Agent
metadata:
  name: automation_agent
  version: 1.0.0
spec:
  model_policy:
    preferred:
      provider: ollama
      model: qwen2.5-coder
  prompts:
    system: prompts/system/automation.md
  tools:
    - id: execute_command
      type: mcp
      entrypoint: automation:execute_command
    - id: schedule_task
      type: mcp
      entrypoint: automation:schedule_task
```

### From CLI

```bash
# List MCP servers
./bin/cbw mcp list

# List tools in server
./bin/cbw mcp tools automation

# Execute tool
./bin/cbw mcp exec automation execute_command \
  --params '{"command": "echo hello"}'
```

## Custom MCP Servers

### Creating a Custom Server

**Step 1: Server Structure**

```
mcp-servers/custom/
├── package.json
├── index.js
├── tools/
│   ├── tool1.js
│   └── tool2.js
└── README.md
```

**Step 2: Implement Server**

`mcp-servers/custom/index.js`:

```javascript
const { McpServer } = require('@modelcontextprotocol/sdk');

// Create server
const server = new McpServer({
  name: 'custom',
  version: '1.0.0'
});

// Register tools
server.tool({
  name: 'my_tool',
  description: 'Description of what the tool does',
  inputSchema: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        description: 'First parameter'
      },
      param2: {
        type: 'number',
        description: 'Second parameter'
      }
    },
    required: ['param1']
  }
}, async (input) => {
  // Tool implementation
  const { param1, param2 } = input;
  
  // Process
  const result = await processData(param1, param2);
  
  return {
    success: true,
    data: result
  };
});

// Start server
server.start({
  transport: 'stdio'
});
```

**Step 3: Register Server**

Add to `mcp-servers/config.json`:

```json
{
  "servers": {
    "custom": {
      "command": "node",
      "args": ["mcp-servers/custom/index.js"],
      "env": {
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

**Step 4: Use in Agents**

```yaml
tools:
  - id: my_custom_tool
    type: mcp
    entrypoint: custom:my_tool
    config:
      param1: "value"
```

### Testing MCP Servers

```javascript
// mcp-servers/custom/test/test_server.js
const assert = require('assert');
const { McpClient } = require('@modelcontextprotocol/sdk');

describe('Custom MCP Server', () => {
  let client;
  
  before(async () => {
    client = new McpClient({
      command: 'node',
      args: ['../index.js']
    });
    await client.connect();
  });
  
  after(async () => {
    await client.disconnect();
  });
  
  it('should list available tools', async () => {
    const tools = await client.listTools();
    assert(tools.length > 0);
    assert(tools.some(t => t.name === 'my_tool'));
  });
  
  it('should execute tool', async () => {
    const result = await client.executeTool('my_tool', {
      param1: 'test',
      param2: 42
    });
    
    assert.strictEqual(result.success, true);
    assert(result.data);
  });
});
```

## Best Practices

### 1. Error Handling

Implement comprehensive error handling:

```javascript
server.tool({
  name: 'my_tool'
}, async (input) => {
  try {
    // Validate input
    if (!input.param1) {
      throw new Error('param1 is required');
    }
    
    // Execute
    const result = await processData(input);
    
    return {
      success: true,
      data: result
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});
```

### 2. Input Validation

Use JSON Schema for validation:

```javascript
server.tool({
  name: 'my_tool',
  inputSchema: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        minLength: 1,
        maxLength: 100
      },
      param2: {
        type: 'number',
        minimum: 0,
        maximum: 100
      }
    },
    required: ['param1']
  }
}, handler);
```

### 3. Logging

Implement structured logging:

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

server.tool({
  name: 'my_tool'
}, async (input) => {
  logger.info('Tool called', { tool: 'my_tool', input });
  
  try {
    const result = await processData(input);
    logger.info('Tool succeeded', { tool: 'my_tool', result });
    return { success: true, data: result };
  } catch (error) {
    logger.error('Tool failed', { tool: 'my_tool', error: error.message });
    return { success: false, error: error.message };
  }
});
```

### 4. Resource Management

Clean up resources properly:

```javascript
const resources = new Map();

process.on('SIGINT', async () => {
  // Cleanup on shutdown
  for (const [id, resource] of resources) {
    await resource.cleanup();
  }
  process.exit(0);
});
```

### 5. Security

Validate and sanitize inputs:

```javascript
const sanitize = require('sanitize-html');

server.tool({
  name: 'execute_command'
}, async (input) => {
  // Sanitize input
  const command = sanitize(input.command, {
    allowedTags: [],
    allowedAttributes: {}
  });
  
  // Validate against whitelist
  const allowedCommands = ['ls', 'echo', 'cat'];
  const baseCommand = command.split(' ')[0];
  
  if (!allowedCommands.includes(baseCommand)) {
    throw new Error('Command not allowed');
  }
  
  // Execute safely
  const result = await executeCommand(command);
  return { success: true, data: result };
});
```

## Additional Resources

- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [API Reference](API.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
