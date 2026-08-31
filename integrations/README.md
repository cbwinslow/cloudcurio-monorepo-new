# CloudCurio AI Tool Integrations

Complete guide to integrating CloudCurio with popular AI coding assistants.

## Supported Tools

- **GitHub Copilot** - Native GitHub integration
- **Cursor** - AI-first code editor
- **Kilocode CLI** - Command-line AI assistant
- **Gemini CLI** - Google's AI assistant
- **OpenCode** - Open-source AI coding tool

## Quick Install

```bash
# Install for all tools
./scripts/install_integrations.sh all

# Install for specific tool
./scripts/install_integrations.sh copilot
./scripts/install_integrations.sh cursor
./scripts/install_integrations.sh kilocode
./scripts/install_integrations.sh gemini
./scripts/install_integrations.sh opencode
```

## What Gets Integrated

Each integration provides access to:

### 1. Tools (via MCP)
- `llm_completion` - Text generation
- `web_search` - Web searching
- `web_scrape` - Content extraction
- `file_read/write` - File operations
- `data_transform` - Data processing
- `system_monitor` - System monitoring

### 2. Agents
- `researcher` - Web research and synthesis
- `data_analyst` - Data analysis
- `code_reviewer` - Code review
- `task_coordinator` - Multi-agent coordination
- `system_monitor` - Health monitoring

### 3. Skills (Slash Commands)
- `/research` - Research topics
- `/analyze` - Analyze data
- `/review` - Review code
- `/generate` - Generate content
- `/monitor` - Monitor system

### 4. Workflows
- Research and report generation
- Parallel data processing
- Democratic decision making

## Integration Details

### GitHub Copilot

**Location**: `.github/copilot/instructions.md`

**Features**:
- Automatic context injection
- Tool usage patterns
- Code conventions
- Best practices

**Usage**:
```
# Copilot automatically reads instructions
# No additional configuration needed
```

### Cursor

**Location**: `~/.cursor/`

**Setup**:
1. Install integration: `./scripts/install_integrations.sh cursor`
2. Restart Cursor
3. Configure MCP servers in settings

**Usage**:
```
# In Cursor chat
"Use cloudcurio to research AI trends"
"Run the /analyze skill on data.csv"
```

### Kilocode CLI

**Location**: `~/.kilocode/extensions/cloudcurio.json`

**Setup**:
1. Install Kilocode: `npm install -g kilocode`
2. Install integration: `./scripts/install_integrations.sh kilocode`
3. Activate: `kilocode --extension cloudcurio`

**Usage**:
```bash
# Use tools
kilocode --tool web_search --query "Python async"

# Run agents
kilocode agent researcher --input "Research AI safety"

# Execute skills
kilocode skill /research topic="quantum computing"
```

### Gemini CLI

**Location**: `~/.gemini/tools/cloudcurio.yaml`

**Setup**:
1. Install Gemini CLI
2. Install integration: `./scripts/install_integrations.sh gemini`
3. Set API key: `export GOOGLE_API_KEY=your-key`

**Usage**:
```bash
# Use tools
gemini --tool llm_completion --prompt "Explain closures"

# Run agents
gemini agent code_reviewer --input "Review src/module.py"

# Execute skills
gemini skill /analyze source="data.csv"
```

### OpenCode

**Location**: `~/.opencode/extensions/cloudcurio.json`

**Setup**:
1. Install OpenCode
2. Install integration: `./scripts/install_integrations.sh opencode`
3. Restart OpenCode

**Usage**:
```
# In OpenCode
/cloudcurio research "AI agent frameworks"
/cloudcurio analyze data.csv
/cloudcurio review src/
```

## Manual Configuration

If automatic installation doesn't work, configure manually:

### 1. Set Environment Variables

```bash
export CLOUDCURIO_ROOT="/path/to/cloudcurio-monorepo"
export PYTHONPATH="$CLOUDCURIO_ROOT/src:$PYTHONPATH"
export OLLAMA_HOST="http://localhost:11434"
```

### 2. Configure MCP Server

Add to your tool's MCP configuration:

```json
{
  "mcpServers": {
    "cloudcurio": {
      "command": "python3",
      "args": ["-m", "cbw_foundry.mcp.unified_server"],
      "cwd": "/path/to/cloudcurio-monorepo",
      "env": {
        "PYTHONPATH": "/path/to/cloudcurio-monorepo/src"
      }
    }
  }
}
```

### 3. Verify Installation

```bash
# Test MCP server
python3 -m cbw_foundry.mcp.unified_server --test

# Test skill system
python3 -c "from cbw_foundry.skills import discover_skills, get_registry; discover_skills('skills'); print(len(get_registry().list_skills()))"

# Test tools
python3 -c "from agents.tools.llm_tools import llm_completion_tool; print(llm_completion_tool())"
```

## Usage Examples

### Example 1: Research Workflow

```python
# Via any integrated tool
/research topic="AI safety" depth="comprehensive" sources=10
```

**What happens**:
1. `researcher` agent searches web
2. Extracts and analyzes content
3. Synthesizes findings
4. Generates report
5. Saves to `output/ai_safety_report.md`

### Example 2: Code Review

```python
# Via integrated tool
/review path="src/module.py" focus="security" severity="critical"
```

**What happens**:
1. `code_reviewer` agent reads file
2. Analyzes code for security issues
3. Checks best practices
4. Generates review report
5. Returns findings with severity levels

### Example 3: Data Analysis

```python
# Via integrated tool
/analyze source="sales_data.csv" operations="stats,filter,transform"
```

**What happens**:
1. `data_analyst` agent loads CSV
2. Calculates statistics
3. Filters and transforms data
4. Generates insights
5. Creates analysis report

### Example 4: Multi-Agent Workflow

```python
# Run via workflow
workflow run workflows/library/research_and_report.workflow.yaml \
  --var topic="AI trends"
```

**What happens**:
1. Multiple agents coordinate
2. Research → Analyze → Write → Review
3. Each agent passes results to next
4. Final report generated
5. Saved and delivered

## API Integration

### Python API

```python
from cbw_foundry.skills import execute_command

# Execute skill programmatically
result = execute_command('/research topic="AI agents"')
print(result)
```

### REST API (via MCP)

```bash
# Call MCP server directly
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "/research", "params": {"topic": "AI"}}'
```

## Troubleshooting

### Tools Not Loading

```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Verify installation
python3 -c "import cbw_foundry; print(cbw_foundry.__file__)"

# Test MCP server
python3 -m cbw_foundry.mcp.unified_server --test
```

### Skills Not Found

```bash
# Discover skills
python3 -c "from cbw_foundry.skills import discover_skills; discover_skills('skills')"

# List skills
./bin/cbw-skills list
```

### Agent Specs Invalid

```bash
# Validate specs
./bin/cbw-agent validate agents/specs/*.agent.yaml

# Check syntax
yamllint agents/specs/
```

### MCP Server Crashes

```bash
# Check logs
tail -f /tmp/cbw_mcp_server.log

# Run in debug mode
python3 -m cbw_foundry.mcp.unified_server --debug
```

## Advanced Configuration

### Custom Tool Registration

```python
from cbw_foundry.skills import register_skill, Skill, SkillParameter

# Define custom skill
skill = Skill(
    name="my_skill",
    command="/myskill",
    description="My custom skill",
    parameters=[SkillParameter(name="input", type="string", required=True)],
    handler=my_handler_function,
)

# Register
register_skill(skill)
```

### Plugin Development

See `templates/` for plugin templates:
- Agent templates
- Tool templates
- Skill templates
- Workflow templates

## Support

- **Documentation**: `docs/`
- **Examples**: `examples/use_cases/`
- **Templates**: `templates/`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Contributing

1. Create integration for new tool
2. Test thoroughly
3. Document setup process
4. Add to installer script
5. Submit PR

## License

MIT License - See LICENSE file
