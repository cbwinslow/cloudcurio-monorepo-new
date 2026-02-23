#!/usr/bin/env bash
"""
CloudCurio Universal Integration Installer

Installs CloudCurio agents, tools, and skills for various AI coding assistants.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.10+"
        exit 1
    fi
    
    # Check if in CloudCurio repo
    if [ ! -f "$REPO_ROOT/pyproject.toml" ]; then
        print_error "Not in CloudCurio repository root"
        exit 1
    fi
    print_success "CloudCurio repository detected"
    
    # Check virtual environment
    if [ -d "$REPO_ROOT/venv" ]; then
        print_success "Virtual environment found"
    else
        print_warning "Virtual environment not found. Run ./scripts/bootstrap.sh first"
    fi
}

# Install for GitHub Copilot
install_copilot() {
    print_header "Installing for GitHub Copilot"
    
    mkdir -p "$REPO_ROOT/.github/copilot"
    
    if [ -f "$REPO_ROOT/.github/copilot/instructions.md" ]; then
        print_success "Copilot instructions already configured"
    else
        print_error "Copilot instructions not found"
        return 1
    fi
    
    print_success "GitHub Copilot integration ready"
    print_info "Copilot will automatically use instructions from .github/copilot/instructions.md"
}

# Install for Cursor
install_cursor() {
    print_header "Installing for Cursor"
    
    CURSOR_DIR="$HOME/.cursor"
    mkdir -p "$CURSOR_DIR"
    
    # Create symlink to MCP config
    if [ -f "$REPO_ROOT/configs/mcp-servers.json" ]; then
        ln -sf "$REPO_ROOT/configs/mcp-servers.json" "$CURSOR_DIR/mcp-servers.json"
        print_success "MCP servers configuration linked"
    fi
    
    # Copy integration config
    cp "$REPO_ROOT/.github/copilot/instructions.md" "$CURSOR_DIR/cloudcurio-instructions.md"
    print_success "Cursor integration ready"
    print_info "Configure Cursor to use MCP servers from $CURSOR_DIR/mcp-servers.json"
}

# Install for Kilocode
install_kilocode() {
    print_header "Installing for Kilocode CLI"
    
    KILOCODE_CONFIG="$HOME/.kilocode/extensions/cloudcurio.json"
    mkdir -p "$(dirname "$KILOCODE_CONFIG")"
    
    if [ -f "$REPO_ROOT/integrations/kilocode/cloudcurio.config.json" ]; then
        cp "$REPO_ROOT/integrations/kilocode/cloudcurio.config.json" "$KILOCODE_CONFIG"
        print_success "Kilocode configuration installed to $KILOCODE_CONFIG"
    else
        print_error "Kilocode config not found"
        return 1
    fi
    
    print_success "Kilocode integration ready"
    print_info "Use: kilocode --extension cloudcurio"
}

# Install for Gemini CLI
install_gemini() {
    print_header "Installing for Gemini CLI"
    
    GEMINI_CONFIG="$HOME/.gemini/tools/cloudcurio.yaml"
    mkdir -p "$(dirname "$GEMINI_CONFIG")"
    
    # Create Gemini config
    cat > "$GEMINI_CONFIG" << 'EOF'
project: cloudcurio-agents
version: 0.4.0

tools:
  provider: mcp
  server:
    command: python3
    args: ["-m", "cbw_foundry.mcp.unified_server"]
    env:
      PYTHONPATH: "$HOME/Documents/cloudcurio_monorepo/cloudcurio-monorepo/src"
      OLLAMA_HOST: "http://localhost:11434"

agents:
  specs_dir: agents/specs

skills:
  specs_dir: skills
  
settings:
  auto_load_tools: true
  enable_skills: true
EOF
    
    print_success "Gemini CLI configuration installed to $GEMINI_CONFIG"
    print_info "Use: gemini --tools cloudcurio"
}

# Install for OpenCode
install_opencode() {
    print_header "Installing for OpenCode"
    
    OPENCODE_DIR="$HOME/.opencode/extensions"
    mkdir -p "$OPENCODE_DIR"
    
    # Create OpenCode extension manifest
    cat > "$OPENCODE_DIR/cloudcurio.json" << EOF
{
  "name": "cloudcurio",
  "version": "0.4.0",
  "description": "CloudCurio AI Agent Framework",
  "type": "mcp-tools",
  "activate_on_startup": true,
  
  "mcp_server": {
    "command": "python3",
    "args": ["-m", "cbw_foundry.mcp.unified_server"],
    "cwd": "$REPO_ROOT",
    "env": {
      "PYTHONPATH": "$REPO_ROOT/src:$REPO_ROOT"
    }
  },
  
  "tools": $(cat "$REPO_ROOT/integrations/kilocode/cloudcurio.config.json" | jq '.tools'),
  "agents": $(cat "$REPO_ROOT/integrations/kilocode/cloudcurio.config.json" | jq '.agents'),
  "skills": $(cat "$REPO_ROOT/integrations/kilocode/cloudcurio.config.json" | jq '.skills')
}
EOF
    
    print_success "OpenCode extension installed to $OPENCODE_DIR/cloudcurio.json"
    print_info "Restart OpenCode to activate CloudCurio tools"
}

# Setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    # Add to shell RC file
    SHELL_RC=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "CLOUDCURIO_ROOT" "$SHELL_RC"; then
            echo "" >> "$SHELL_RC"
            echo "# CloudCurio Integration" >> "$SHELL_RC"
            echo "export CLOUDCURIO_ROOT=\"$REPO_ROOT\"" >> "$SHELL_RC"
            echo "export PYTHONPATH=\"\$CLOUDCURIO_ROOT/src:\$PYTHONPATH\"" >> "$SHELL_RC"
            print_success "Environment variables added to $SHELL_RC"
        else
            print_info "Environment already configured"
        fi
    fi
    
    # Create activation script
    cat > "$REPO_ROOT/activate_cloudcurio.sh" << 'EOF'
#!/usr/bin/env bash
# Activate CloudCurio environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export CLOUDCURIO_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$CLOUDCURIO_ROOT/src:$PYTHONPATH"

if [ -d "$CLOUDCURIO_ROOT/venv" ]; then
    source "$CLOUDCURIO_ROOT/venv/bin/activate"
    echo "CloudCurio environment activated"
else
    echo "Warning: venv not found. Run ./scripts/bootstrap.sh"
fi
EOF
    
    chmod +x "$REPO_ROOT/activate_cloudcurio.sh"
    print_success "Activation script created: activate_cloudcurio.sh"
}

# Main installation menu
show_menu() {
    clear
    print_header "CloudCurio Universal Installer"
    echo ""
    echo "Install CloudCurio integration for:"
    echo ""
    echo "  1) GitHub Copilot"
    echo "  2) Cursor"
    echo "  3) Kilocode CLI"
    echo "  4) Gemini CLI"
    echo "  5) OpenCode"
    echo "  6) All of the above"
    echo "  7) Setup environment only"
    echo "  0) Exit"
    echo ""
    read -p "Select option: " choice
    
    case $choice in
        1) install_copilot ;;
        2) install_cursor ;;
        3) install_kilocode ;;
        4) install_gemini ;;
        5) install_opencode ;;
        6) 
            install_copilot
            install_cursor
            install_kilocode
            install_gemini
            install_opencode
            ;;
        7) setup_environment ;;
        0) exit 0 ;;
        *) 
            print_error "Invalid option"
            sleep 2
            show_menu
            ;;
    esac
}

# Main script
main() {
    check_prerequisites
    setup_environment
    
    echo ""
    if [ $# -eq 0 ]; then
        show_menu
    else
        case "$1" in
            copilot) install_copilot ;;
            cursor) install_cursor ;;
            kilocode) install_kilocode ;;
            gemini) install_gemini ;;
            opencode) install_opencode ;;
            all)
                install_copilot
                install_cursor
                install_kilocode
                install_gemini
                install_opencode
                ;;
            *)
                echo "Usage: $0 [copilot|cursor|kilocode|gemini|opencode|all]"
                exit 1
                ;;
        esac
    fi
    
    echo ""
    print_header "Installation Complete!"
    echo ""
    print_info "Next steps:"
    echo "  1. Restart your AI coding assistant"
    echo "  2. Verify tools are available"
    echo "  3. Try a skill: /research topic=\"AI agents\""
    echo ""
    print_info "Documentation: $REPO_ROOT/docs/"
    print_info "Examples: $REPO_ROOT/agents/examples/"
}

main "$@"
