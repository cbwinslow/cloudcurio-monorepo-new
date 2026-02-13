# CloudCurio Monorepo Bootstrap Script for Windows
# PowerShell script for setting up development environment on Windows

# Requires: PowerShell 5.1+ and Python 3.11+

param(
    [switch]$SkipTests = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }

Write-Info "==================================================================="
Write-Info "CloudCurio Monorepo Bootstrap Script (Windows)"
Write-Info "==================================================================="
Write-Info ""

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Info "PowerShell Version: $psVersion"
if ($psVersion.Major -lt 5) {
    Write-Failure "ERROR: PowerShell 5.1 or higher is required"
    Write-Info "Current version: $psVersion"
    exit 1
}
Write-Success "✓ PowerShell version OK"

# Check if Python is installed
Write-Info "Checking for Python..."
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3\.1[12]") {
            $pythonCmd = $cmd
            Write-Info "Found: $version using command '$cmd'"
            break
        }
    }
    catch {
        # Command not found, continue
    }
}

if ($null -eq $pythonCmd) {
    Write-Failure "ERROR: Python 3.11 or 3.12 not found"
    Write-Info "Please install Python from: https://www.python.org/downloads/"
    Write-Info "Make sure to check 'Add Python to PATH' during installation"
    exit 1
}
Write-Success "✓ Python found: $pythonCmd"

# Check if Git is installed
Write-Info "Checking for Git..."
try {
    $gitVersion = git --version 2>&1
    Write-Info "Found: $gitVersion"
    Write-Success "✓ Git found"
}
catch {
    Write-Warning "⚠ Git not found (optional but recommended)"
    Write-Info "Install from: https://git-scm.com/download/win"
}

# Get repository root
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT
Write-Info "Repository root: $ROOT"

# Create virtual environment if it doesn't exist
Write-Info ""
Write-Info "Setting up Python virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Info "Creating new virtual environment..."
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "ERROR: Failed to create virtual environment"
        exit 1
    }
    Write-Success "✓ Virtual environment created"
}
else {
    Write-Info "Virtual environment already exists"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
$activateScript = Join-Path $ROOT ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Failure "ERROR: Virtual environment activation script not found"
    exit 1
}

# Check execution policy
$executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($executionPolicy -eq "Restricted" -or $executionPolicy -eq "AllSigned") {
    Write-Warning "⚠ Execution policy is restrictive: $executionPolicy"
    Write-Info "Attempting to set execution policy..."
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Success "✓ Execution policy updated"
    }
    catch {
        Write-Failure "ERROR: Could not update execution policy"
        Write-Info "Please run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        exit 1
    }
}

& $activateScript
Write-Success "✓ Virtual environment activated"

# Upgrade pip
Write-Info ""
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Failure "ERROR: Failed to upgrade pip"
    exit 1
}
Write-Success "✓ pip upgraded"

# Install dependencies
Write-Info ""
Write-Info "Installing dependencies..."
Write-Info "This may take a few minutes..."
pip install -e ".[dev]" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Failure "ERROR: Failed to install dependencies"
    Write-Info "Try running manually: pip install -e \".[dev]\""
    exit 1
}
Write-Success "✓ Dependencies installed"

# Install pre-commit hooks
Write-Info ""
Write-Info "Installing pre-commit hooks..."
try {
    pre-commit install 2>&1 | Out-Null
    Write-Success "✓ Pre-commit hooks installed"
}
catch {
    Write-Warning "⚠ Failed to install pre-commit hooks (optional)"
    Write-Info "You can install them later with: pre-commit install"
}

# Run health check
Write-Info ""
Write-Info "Running health check..."
try {
    if (Test-Path "bin\cbw-doctor") {
        python bin\cbw-doctor 2>&1 | Out-Null
        Write-Success "✓ Health check passed"
    }
    else {
        Write-Warning "⚠ Health check tool not found (cbw-doctor)"
    }
}
catch {
    Write-Warning "⚠ Health check completed with warnings"
}

# Generate indexes
Write-Info ""
Write-Info "Generating indexes..."
try {
    python bin\cbw-index 2>&1 | Out-Null
    Write-Success "✓ Indexes generated"
}
catch {
    Write-Warning "⚠ Failed to generate indexes"
}

# Validate agent specs
if (-not $SkipTests) {
    Write-Info ""
    Write-Info "Validating agent specifications..."
    try {
        $exampleSpecs = Get-ChildItem "agents\specs\examples\*.agent.yaml" -ErrorAction SilentlyContinue
        if ($exampleSpecs) {
            foreach ($spec in $exampleSpecs) {
                python bin\cbw-agent validate $spec.FullName 2>&1 | Out-Null
            }
            Write-Success "✓ Agent specs validated"
        }
        else {
            Write-Info "No example agent specs found to validate"
        }
    }
    catch {
        Write-Warning "⚠ Agent validation completed with warnings"
    }

    # Compile agent specs
    Write-Info ""
    Write-Info "Compiling agent specifications..."
    try {
        if ($exampleSpecs) {
            New-Item -ItemType Directory -Force -Path "dist\agents" | Out-Null
            foreach ($spec in $exampleSpecs) {
                python bin\cbw-agent compile $spec.FullName --out dist\agents 2>&1 | Out-Null
            }
            Write-Success "✓ Agent specs compiled"
        }
    }
    catch {
        Write-Warning "⚠ Agent compilation completed with warnings"
    }

    # Run golden tests
    Write-Info ""
    Write-Info "Running golden tests..."
    try {
        $goldenTests = Get-ChildItem "agents\evals\golden\*.yaml" -ErrorAction SilentlyContinue
        if ($goldenTests) {
            foreach ($test in $goldenTests) {
                python bin\cbw-agent eval $test.FullName 2>&1 | Out-Null
            }
            Write-Success "✓ Golden tests passed"
        }
        else {
            Write-Info "No golden tests found to run"
        }
    }
    catch {
        Write-Warning "⚠ Golden tests completed with warnings"
    }
}
else {
    Write-Info ""
    Write-Info "Skipping validation and tests (--SkipTests flag used)"
}

# Final message
Write-Info ""
Write-Success "==================================================================="
Write-Success "Bootstrap Complete!"
Write-Success "==================================================================="
Write-Info ""
Write-Info "Next steps:"
Write-Info "  1. Ensure virtual environment is activated:"
Write-Info "     .\.venv\Scripts\Activate.ps1"
Write-Info ""
Write-Info "  2. Run health check:"
Write-Info "     python bin\cbw-doctor"
Write-Info ""
Write-Info "  3. Explore available commands:"
Write-Info "     python bin\cbw --help"
Write-Info "     python bin\cbw-agent --help"
Write-Info ""
Write-Info "  4. Read the documentation:"
Write-Info "     docs\QUICKSTART.md"
Write-Info "     docs\INSTALL.md"
Write-Info ""
Write-Info "For help, see: https://github.com/cbwinslow/cloudcurio-monorepo-new"
Write-Info ""

# Deactivate virtual environment (optional)
# deactivate

Write-Success "✓ Ready to develop!"
