---
title: KB Index
tags: [kb]
owner: cbwinslow
last_reviewed: 2026-01-15
---

# CloudCurio Monorepo Knowledge Base

Welcome to the CloudCurio Knowledge Base - your comprehensive guide to working with the monorepo.

## 📚 Table of Contents

### Getting Started
- [Installation Guide](../docs/INSTALL.md) - Complete setup instructions
- [Quickstart Tutorial](../docs/QUICKSTART.md) - Get running in 5 minutes
- [Using the Repo](runbooks/using_the_repo.md) - Daily workflows and operations

### Runbooks (Operational Procedures)
- [Using the Repo](runbooks/using_the_repo.md) - Daily workflow and commands
- [Adding New Agents](runbooks/adding_new_agent.md) - Agent development guide
- [Debugging Agents](runbooks/debugging_agents.md) - Troubleshooting agent issues
- [Deploying to Production](runbooks/deployment.md) - Production deployment procedures

### Architecture & Decisions
- [ADR-0001: Monorepo Structure](decisions/adr-0001-monorepo-structure.md) - Why monorepo
- [ADR-0002: Agent Specification Format](decisions/adr-0002-agent-spec-format.md) - YAML vs JSON
- [ADR-0003: Runtime Adapter Pattern](decisions/adr-0003-runtime-adapters.md) - Framework abstraction
- [ADR-0004: Observability Strategy](decisions/adr-0004-observability.md) - Monitoring approach

### Context & Environment
- [Environment Documentation](context/environment.md) - Machine specs, OS, networking
- [Tool Ecosystem](context/tool_ecosystem.md) - Available tools and their purposes
- [Framework Comparisons](context/frameworks.md) - CrewAI vs LangChain vs PydanticAI

### Rules & Standards
- [Code Quality Rules](rules/code_quality_rules.md) - Coding standards and best practices
- [Agent Design Patterns](rules/agent_patterns.md) - Recommended agent architectures
- [Testing Requirements](rules/testing_standards.md) - Test coverage and quality gates
- [Documentation Standards](rules/documentation_standards.md) - How to write docs

## 🎯 Quick Navigation

### By Role

**Agent Developers**
1. Start with [Adding New Agents](runbooks/adding_new_agent.md)
2. Review [Agent Design Patterns](rules/agent_patterns.md)
3. Understand [Tool Ecosystem](context/tool_ecosystem.md)
4. Follow [Code Quality Rules](rules/code_quality_rules.md)

**Framework Contributors**
1. Read [ADR-0001: Monorepo Structure](decisions/adr-0001-monorepo-structure.md)
2. Understand [Runtime Adapter Pattern](decisions/adr-0003-runtime-adapters.md)
3. Follow [Testing Requirements](rules/testing_standards.md)
4. Review [Documentation Standards](rules/documentation_standards.md)

**DevOps Engineers**
1. Check [Environment Documentation](context/environment.md)
2. Review [Deployment Runbook](runbooks/deployment.md)
3. Understand [Observability Strategy](decisions/adr-0004-observability.md)

**New Team Members**
1. Read [Using the Repo](runbooks/using_the_repo.md)
2. Complete [Quickstart Tutorial](../docs/QUICKSTART.md)
3. Browse [Code Quality Rules](rules/code_quality_rules.md)
4. Try [Adding New Agents](runbooks/adding_new_agent.md)

## 📖 Document Types

### Runbooks
Step-by-step operational procedures for common tasks. These are living documents that should be updated as processes evolve.

**Format:** Task-oriented, imperative instructions  
**Audience:** All team members  
**Update Frequency:** As needed when processes change

### Architecture Decision Records (ADRs)
Documents explaining significant architectural decisions, their context, and consequences.

**Format:** Context, Decision, Consequences  
**Audience:** Technical leadership, contributors  
**Update Frequency:** Only amended, never deleted

### Context Documents
Environmental and ecosystem documentation providing situational awareness.

**Format:** Descriptive, informational  
**Audience:** All team members  
**Update Frequency:** Quarterly or when significant changes occur

### Rules & Standards
Normative documents defining how work should be done.

**Format:** Prescriptive, rule-based  
**Audience:** Contributors  
**Update Frequency:** Reviewed quarterly

## 🔍 Finding Information

### Search by Topic

**Agent Development**
- [Adding New Agents](runbooks/adding_new_agent.md)
- [Agent Design Patterns](rules/agent_patterns.md)
- [Debugging Agents](runbooks/debugging_agents.md)
- [Agent Specification Format](decisions/adr-0002-agent-spec-format.md)

**Tools & Integration**
- [Tool Ecosystem](context/tool_ecosystem.md)
- [Runtime Adapters](decisions/adr-0003-runtime-adapters.md)
- [Framework Comparisons](context/frameworks.md)

**Quality & Testing**
- [Code Quality Rules](rules/code_quality_rules.md)
- [Testing Requirements](rules/testing_standards.md)

**Operations**
- [Using the Repo](runbooks/using_the_repo.md)
- [Deployment](runbooks/deployment.md)
- [Observability](decisions/adr-0004-observability.md)

## 🤝 Contributing to KB

### Adding New Documents

1. **Choose the right category**: Runbook, ADR, Context, or Rules
2. **Use the template**: Copy from existing document in same category
3. **Follow naming convention**: `lowercase-with-dashes.md`
4. **Update this index**: Add your document to the relevant section
5. **Add frontmatter**: Include title, tags, owner, last_reviewed

### Updating Existing Documents

1. **Update content** as needed
2. **Update last_reviewed** date in frontmatter
3. **Update index** if title or organization changes
4. **Commit with clear message**: "docs(kb): update [document-name]"

### Document Frontmatter Template

```yaml
---
title: "Document Title"
tags: [category, topic, keywords]
owner: github_username
last_reviewed: YYYY-MM-DD
---
```

## 📋 Document Status

| Document | Status | Last Reviewed | Owner |
|----------|--------|---------------|-------|
| kb/index.md | ✅ Current | 2026-01-15 | cbwinslow |
| runbooks/using_the_repo.md | ✅ Current | 2026-01-15 | cbwinslow |
| runbooks/adding_new_agent.md | ✅ Current | 2026-01-15 | cbwinslow |
| context/environment.md | ✅ Current | 2026-01-15 | cbwinslow |
| decisions/adr-0001-monorepo-structure.md | ✅ Current | 2026-01-15 | cbwinslow |
| rules/code_quality_rules.md | 🔄 Review Needed | 2026-01-11 | cbwinslow |

**Status Legend:**
- ✅ Current: Up to date and accurate
- 🔄 Review Needed: Older than 90 days
- ⚠️ Outdated: Known to be inaccurate
- 🚧 In Progress: Being actively updated

## 🆘 Need Help?

- **Can't find what you need?** Check the main [README](../README.md)
- **Found an error?** Open an issue or submit a PR
- **Have a question?** Ask in GitHub Discussions
- **Need operational support?** See [Using the Repo](runbooks/using_the_repo.md)

---

**Last Updated:** 2026-01-15  
**Maintained By:** @cbwinslow
