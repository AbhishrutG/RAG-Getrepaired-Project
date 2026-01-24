# N8N Workflow Builder - Claude Code Project

This project enables building n8n automation workflows through natural language prompts.

## Instance Details

- **N8N Cloud URL:** https://getrepaired.app.n8n.cloud
- **MCP Server:** n8n-mcp (configured in `.mcp.json`)
- **GitHub Repository:** https://github.com/AbhishrutG/n8n-workflows (private)

## Available Tools

### N8N MCP Server
Provides access to 1,084+ n8n nodes with full documentation, properties, and operations. Use MCP tools to:
- Search and discover nodes
- Get node documentation and configuration schemas
- Create, read, update, and delete workflows
- Execute workflows
- Manage credentials

### N8N Skills (7 skills installed)
1. **n8n-expression-syntax** - Correct `{{}}` patterns and variable access
2. **n8n-mcp-tools-expert** - Guide for effective MCP tool usage
3. **n8n-workflow-patterns** - Five proven architectural templates
4. **n8n-validation-expert** - Error interpretation and resolution
5. **n8n-node-configuration** - Operation-aware setup guidance
6. **n8n-code-javascript** - JavaScript implementation in Code nodes
7. **n8n-code-python** - Python implementation with limitations

## How to Build Workflows

When asked to create a workflow:

1. **Understand the requirement** - Clarify what automation the user needs
2. **Search for nodes** - Use MCP tools to find appropriate nodes
3. **Design the flow** - Plan the workflow architecture (trigger → processing → output)
4. **Create the workflow** - Use MCP tools to build the workflow in n8n
5. **Validate** - Check for errors and ensure proper configuration
6. **Auto-save to GitHub** - Save workflow JSON and commit (see below)

## Auto-Save to GitHub

After creating or updating a workflow, ALWAYS:

1. **Export the workflow JSON** from the API response
2. **Save to file:** `workflows/active/{workflow-name}.json`
   - Use kebab-case for filenames (e.g., `lead-capture-workflow.json`)
   - For archived workflows, save to `workflows/archive/`
3. **Commit and push:**
   ```bash
   git add workflows/
   git commit -m "Update workflow: {workflow-name}"
   git push
   ```

This ensures all workflows are version-controlled and backed up to GitHub.

## Key Gotchas

- **Webhook data:** Access via `$json.body` not `$json` directly
- **Python Code nodes:** No external libraries allowed (only built-ins)
- **Expression syntax:** Always use `{{ }}` for dynamic values
- **NodeType format:** MCP tools use specific format (check n8n-mcp-tools-expert skill)

## Workflow Patterns

1. **Webhook → Process → Respond** - For API endpoints
2. **Schedule → Fetch → Store** - For periodic data sync
3. **Trigger → Transform → Multi-output** - For event-driven processing
4. **Error handling** - Use Error Trigger nodes for resilience
5. **Sub-workflows** - Break complex logic into reusable pieces

## Common Commands

```
"Create a workflow that..."
"Add a node to handle..."
"Connect [service A] to [service B]"
"Schedule a workflow to run every..."
"Create a webhook that receives..."
```

## Safety Notes

- Always backup important workflows before AI modifications
- Test changes in a copy before applying to production workflows
- Validate all webhook URLs and credentials

## Project Structure

```
n8n builder/
├── CLAUDE.md          # This file - project instructions
├── .mcp.json          # MCP server configuration (DO NOT COMMIT)
├── .gitignore         # Git ignore rules
├── n8n-skills/        # Cloned skills repository
└── workflows/         # Workflow JSON backups (version controlled)
    ├── active/        # Currently active workflows
    └── archive/       # Archived/old workflows
```
