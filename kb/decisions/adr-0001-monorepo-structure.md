---
title: "ADR-0001: Monorepo structure"
tags: [adr, architecture]
owner: cbwinslow
last_reviewed: 2026-01-15
status: Accepted
---

# ADR-0001: Monorepo Structure

## Status

**Accepted** - 2026-01-11

## Context

When building a comprehensive AI agent framework and tooling ecosystem, we need to decide on the repository structure. The key decision is between:

1. **Polyrepo (Multiple Repositories)**: Separate repos for each component
   - Agents in one repo
   - Tools in another repo
   - Framework core in yet another repo
   - Documentation separately
   
2. **Monorepo (Single Repository)**: All components in one unified repository
   - Everything in a single repo with organized subdirectories
   - Shared versioning and dependency management
   - Atomic commits across components

### Problem Statement

We need a repository structure that:

- **Supports rapid development** of new agents and tools
- **Maintains consistency** across all components
- **Simplifies dependency management** between related components
- **Enables atomic changes** when updates span multiple components
- **Facilitates knowledge sharing** and discoverability
- **Scales** as the project grows
- **Works well for solo developers** as well as teams

### Requirements

1. Easy to discover existing agents and tools
2. Simple to add new agents without complex setup
3. Shared tooling and infrastructure across all components
4. Consistent versioning and release process
5. Unified documentation and knowledge base
6. Efficient CI/CD pipelines
7. Clear ownership and responsibility boundaries

### Alternative Considered: Polyrepo

**Advantages:**
- Independent versioning per component
- Smaller checkout size
- Clear boundaries between components
- Different teams can own different repos

**Disadvantages:**
- Complex dependency management across repos
- Harder to make cross-cutting changes
- Duplicated tooling and CI/CD configuration
- Knowledge fragmentation
- Difficult to discover related work
- Version synchronization challenges
- Multiple PRs needed for related changes

### Example Scenario

Consider adding a new agent that requires:
1. A new tool implementation
2. Updates to the runtime adapter
3. New documentation
4. Test infrastructure changes

**In polyrepo:**
- 4 separate PRs across 4 repos
- Complex coordination to merge in correct order
- Version dependencies to track
- Multiple CI runs to wait for
- Risk of incompatible versions

**In monorepo:**
- 1 PR with all changes
- Single atomic commit
- All tests run together
- Easy to review holistically
- No version coordination needed

## Decision

**We will use a monorepo structure** as the single source of truth for all AI agents, tools, workflows, and framework code.

### Monorepo Organization

```
cloudcurio-monorepo/
├── agents/           # Agent specifications and implementations
│   ├── specs/        # YAML agent definitions
│   ├── library/      # Pre-built agent implementations
│   ├── orchestrator/ # Multi-agent coordination
│   ├── tools/        # Tool implementations
│   ├── toolsets/     # Domain-specific tool collections
│   ├── evals/        # Golden test suites
│   └── specialized/  # Domain expert agents
├── src/              # Core framework (cbw_foundry)
│   └── cbw_foundry/  # Python package
├── workflows/        # YAML workflow definitions
├── kb/               # Knowledge base
│   ├── runbooks/     # Operational procedures
│   ├── decisions/    # ADRs
│   ├── context/      # Environmental docs
│   └── rules/        # Standards and guidelines
├── docs/             # User-facing documentation
├── tests/            # Test suites
├── bin/              # CLI executables
├── registry/         # Auto-generated indexes
├── docker/           # Container definitions
├── scripts/          # Utility scripts
└── pyproject.toml    # Unified dependencies
```

### Key Principles

1. **One Master Toolbox**: Everything an agent developer needs in one place
2. **Hierarchical Organization**: Clear directory structure for easy navigation
3. **Separation of Concerns**: Framework vs. agents vs. tools vs. docs
4. **Discoverability**: Registry system for finding agents and tools
5. **Atomic Versioning**: Single version number for entire ecosystem
6. **Shared Infrastructure**: CI/CD, pre-commit hooks, quality tools
7. **Knowledge Centralization**: All docs, runbooks, ADRs in one place

## Consequences

### Positive Consequences

1. **Simplified Development**
   - Single `git clone` gets everything
   - One virtual environment for all work
   - Shared dependencies managed centrally
   - Consistent tooling across all components

2. **Atomic Changes**
   - Cross-cutting changes in single PR
   - No version synchronization issues
   - Easy to refactor across boundaries
   - Reduced integration problems

3. **Better Discoverability**
   - Browse all agents in one place
   - Easy to find related tools
   - Centralized documentation
   - Registry system for search

4. **Consistent Quality**
   - Shared pre-commit hooks
   - Unified CI/CD pipeline
   - Common testing infrastructure
   - Consistent code standards

5. **Knowledge Centralization**
   - All ADRs in one location
   - Unified knowledge base
   - Easier onboarding
   - Reduced context switching

6. **Simplified Releases**
   - Single version number
   - Coordinated releases
   - Clear release notes
   - No compatibility matrices

7. **Efficient CI/CD**
   - Run only affected tests
   - Shared build cache
   - Parallel test execution
   - Faster feedback

### Negative Consequences (and Mitigations)

1. **Larger Repository Size**
   - **Mitigation**: Git shallow clones, sparse checkout
   - **Reality**: Modern git handles this well
   - **Size**: ~200MB is manageable

2. **Potential for Tight Coupling**
   - **Mitigation**: Clear module boundaries in src/
   - **Mitigation**: Runtime adapter pattern
   - **Mitigation**: Tool independence

3. **Single Point of Failure**
   - **Mitigation**: Robust CI/CD
   - **Mitigation**: Branch protection rules
   - **Mitigation**: Required code reviews

4. **Longer CI Times**
   - **Mitigation**: Parallel test execution
   - **Mitigation**: Test only changed paths
   - **Mitigation**: Cached dependencies

5. **Access Control Complexity**
   - **Mitigation**: CODEOWNERS file
   - **Mitigation**: Branch protection
   - **Reality**: Less critical for smaller teams

### Trade-offs Accepted

1. **Repository Size vs. Developer Experience**
   - Accept larger repo for better DX
   - Modern tools handle size well

2. **Coupling Risk vs. Change Atomicity**
   - Accept coupling risk for atomic changes
   - Mitigate with clear interfaces

3. **CI Complexity vs. Consistency**
   - Accept complex CI for quality
   - Reuse across all components

## Implementation Details

### Repository Structure Rationale

**`agents/` directory:**
- Central location for all agent-related code
- Specs separate from implementations
- Tools co-located for discovery
- Evals alongside agents for testing

**`src/cbw_foundry/` core:**
- Framework code separate from agents
- Installable Python package
- Clear API boundaries
- Independent versioning possible if needed

**`kb/` knowledge base:**
- All documentation in one place
- Runbooks for operations
- ADRs for decisions
- Context for environment

**`registry/` auto-generated:**
- Enables agent/tool discovery
- JSON format for tooling
- Generated, not authored
- Git-tracked for transparency

### Dependency Management

**Single `pyproject.toml`:**
```toml
[project]
name = "cbw_foundry"
version = "0.4.0"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "click>=8.0",
    # All shared dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    # Development tools
]
```

Benefits:
- Single source of truth
- No version conflicts
- Easy to update all at once
- Clear what's required

### Versioning Strategy

**Unified Semantic Versioning:**
- Major.Minor.Patch for entire repo
- Breaking changes bump major
- New features bump minor
- Bug fixes bump patch

**Example:**
- v0.4.0 - Current FINAL release
- v0.4.1 - Bug fix release
- v0.5.0 - New agent framework
- v1.0.0 - Production-ready stable API

### CI/CD Pipeline

**Single GitHub Actions Workflow:**

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run linters
        run: make lint
      - name: Run tests
        run: make test
      - name: Validate agents
        run: make validate
      - name: Run evaluations
        run: make eval
```

Benefits:
- Single pipeline for all code
- Consistent quality gates
- Parallel execution
- Clear status checks

### Migration Path

**From polyrepo to monorepo (if needed):**

1. Create monorepo structure
2. Move repos to subdirectories
3. Preserve git history
4. Update import paths
5. Merge CI/CD configs
6. Update documentation
7. Archive old repos

## Related Decisions

- **ADR-0002**: Agent Specification Format (YAML vs JSON)
- **ADR-0003**: Runtime Adapter Pattern (framework independence)
- **ADR-0004**: Observability Strategy (monitoring approach)

## References

- [Monorepo.tools](https://monorepo.tools/) - Comprehensive monorepo resources
- [Google's Monorepo](https://research.google/pubs/pub45424/) - Why Google chose monorepo
- [Advantages of Monorepos](https://danluu.com/monorepo/) - Dan Luu's analysis
- [Monorepo vs Polyrepo](https://earthly.dev/blog/monorepo-vs-polyrepo/) - Detailed comparison

## Review Schedule

This ADR should be reviewed:
- When repository size exceeds 1GB
- When team size exceeds 20 developers
- When CI times exceed 30 minutes
- Annually as part of architecture review

## Notes

- Decision made based on solo/small team context
- May need to revisit for large teams (50+ developers)
- Modern tooling (GitHub, Git) handles monorepos well
- Developer experience is paramount

---

**Decision Date:** 2026-01-11  
**Decision Makers:** @cbwinslow  
**Last Reviewed:** 2026-01-15  
**Next Review:** 2027-01-15
