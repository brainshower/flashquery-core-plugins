# Component Schemas

Detailed format specifications for each plugin component type.

---

## Skills (`skills/skill-name/SKILL.md`)

Skills are auto-invoked by Claude based on context. They're the primary way to give
Claude specialized knowledge or workflows that load on demand.

### Frontmatter

```yaml
---
name: skill-name          # Required. Matches the directory name.
description: >            # Required. THIS is what triggers the skill —
  Use this skill when     # Claude reads name + description to decide
  the user asks to...     # whether to invoke it.
version: 0.1.0            # Optional
---
```

### Description best practices
- Write in third-person: "Use this skill when the user asks to..."
- Include specific trigger phrases in quotes: `"review API design"`, `"check endpoints"`
- Be specific about context, not just keywords
- Err on the side of being explicit — Claude undertriggers more than overtriggers

### Body structure
- Keep SKILL.md under ~3,000 words; move detail into `references/` files
- Write instructions in imperative form: "Parse the config file", not "You should parse..."
- Use `## Section Headers` to organize the content
- Reference `references/` files from the body with clear guidance on when to read them

### Directory structure

```
skills/skill-name/
├── SKILL.md              # Required
├── references/           # Optional — detailed docs loaded on demand
│   └── advanced.md
├── examples/             # Optional — sample inputs/outputs
└── scripts/              # Optional — utility scripts
```

### Example SKILL.md

```markdown
---
name: api-design
description: >
  Use this skill when the user asks to "design an API", "create API endpoints",
  "review API structure", or needs guidance on REST API best practices,
  endpoint naming, or request/response design. Also trigger when the user
  shares an API spec and asks for feedback.
version: 0.1.0
---

# API Design

Apply REST API best practices to design or review endpoint structure,
request/response formats, and naming conventions.

## Endpoint design principles
...
```

---

## Commands (`commands/command-name.md`)

Commands are explicitly invoked by the user with `/plugin-name:command-name [args]`.
They're instructions FOR Claude — written as directives, not user documentation.

### Frontmatter

```yaml
---
description: Brief description shown in /help   # Optional, max ~60 chars
allowed-tools: Read, Write, Bash(git:*)         # Optional — restricts tools
model: sonnet                                    # Optional: sonnet, opus, haiku
argument-hint: <file-path>                       # Optional — autocomplete hint
---
```

### Argument placeholders
- `$ARGUMENTS` — captures all text after the command name as a single string
- `$1`, `$2`, `$3` — positional arguments

### Special syntax
- `@path/to/file` — inlines file contents into the context
- `` !`bash command` `` — executes bash inline and inlines the output
- `${CLAUDE_PLUGIN_ROOT}` — portable reference to the plugin's installation directory

### Example command

```markdown
---
description: Review code for security vulnerabilities
allowed-tools: Read, Grep, Glob
argument-hint: [file-or-directory]
---

Review @$1 for security vulnerabilities. Check for:
- SQL injection opportunities
- XSS attack vectors
- Authentication and authorization gaps
- Insecure data handling or storage

For each finding, report: the file path and line number, a description of the
vulnerability, the severity (Critical / High / Medium / Low), and a specific
remediation suggestion.
```

### allowed-tools patterns

```yaml
# Specific built-in tools
allowed-tools: Read, Write, Edit, Bash

# Bash restricted to specific commands
allowed-tools: Bash(npm:*), Bash(git:*), Read

# MCP tools
allowed-tools: ["mcp__server-name__tool-name"]

# Mix
allowed-tools: Read, Grep, mcp__github__create_issue
```

---

## Agents (`agents/agent-name.md`)

Agents are specialized subagents Claude can spawn for autonomous multi-step tasks.
Less common than skills and commands — use when the task genuinely benefits from
an isolated subagent with its own system prompt and tool restrictions.

### Frontmatter

```yaml
---
name: agent-name      # Required. 3-50 chars, lowercase, hyphens only.
description: >        # Required. Include <example> blocks.
  Use this agent when...

  <example>
  Context: ...
  user: "Can you..."
  assistant: "I'll use the agent-name agent to..."
  </example>

model: inherit        # Required. inherit | sonnet | opus | haiku
color: blue           # Required. blue | cyan | green | yellow | magenta | red
tools: ["Read", "Grep"]  # Optional — restricts available tools
---
```

### Body
The markdown body is the agent's system prompt. Write it as a role definition and set of
instructions the agent should follow.

### Color guidelines
- Blue/Cyan: Analysis, review tasks
- Green: Success-oriented, generation
- Yellow: Validation, cautious tasks
- Red: Critical, security-focused
- Magenta: Creative tasks

---

## Hooks (`hooks/hooks.json`)

Hooks fire automatically on system events. Use for enforcing policies, running automated
checks, or loading context. Most plugins don't need hooks — use only when something must
happen automatically without user invocation.

### Full format

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/validate.sh",
            "timeout": 60
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Load project context from ${CLAUDE_PLUGIN_ROOT}/context.md before responding.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Hook types
- **`command`**: Runs a shell script. Input is passed as JSON on stdin. Use `jq` to
  extract fields. Deterministic, fast, no LLM cost.
- **`prompt`**: Claude evaluates a prompt. Supports `$TOOL_INPUT` and other variables.
  Flexible but adds latency and cost.

### Matcher
A regex pattern that filters which tool calls trigger the hook (for `PreToolUse` /
`PostToolUse`). Examples: `"Write"`, `"Bash"`, `"Write|Edit"`, `".*"` (all tools).

---

## MCP Servers (`.mcp.json`)

See `plugin-structure.md` for the full `.mcp.json` format. Key schema recap:

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@package/mcp-server"],
      "env": {}
    }
  }
}
```

The `server-name` key becomes part of the MCP tool names that Claude uses:
`mcp__<server-name>__<tool-name>`. Choose a clear, stable name.
