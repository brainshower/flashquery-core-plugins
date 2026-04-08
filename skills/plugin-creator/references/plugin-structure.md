# Plugin Structure Reference

## Directory Layout

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json        ← required manifest
├── skills/                ← agent skills (Claude auto-invokes based on context)
│   └── skill-name/
│       ├── SKILL.md       ← required
│       └── references/    ← optional detailed docs
├── commands/              ← slash commands (user explicitly invokes)
│   └── command-name.md
├── agents/                ← subagent definitions
│   └── agent-name.md
├── hooks/
│   └── hooks.json         ← event hooks
├── .mcp.json              ← MCP server configs
├── settings.json          ← optional default settings
└── README.md
```

**Critical rule**: `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json`, and
`settings.json` live at the **plugin root** — NOT inside `.claude-plugin/`. Only
`plugin.json` goes inside `.claude-plugin/`.

---

## plugin.json — Full Schema

```json
{
  "name": "my-plugin",           // REQUIRED. kebab-case, no spaces. Becomes skill namespace.
  "version": "0.1.0",            // REQUIRED. semver (MAJOR.MINOR.PATCH)
  "description": "...",          // REQUIRED. One sentence shown in plugin manager.
  "author": {
    "name": "Author Name",       // Optional
    "email": "author@example.com" // Optional
  },
  "homepage": "https://...",     // Optional
  "repository": "https://...",   // Optional
  "license": "MIT",              // Optional
  "keywords": ["tag", "tag2"],   // Optional — aids discoverability

  // Optional: override auto-discovery paths
  "commands": "./commands",
  "agents": "./agents",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

### Name rules
- Lowercase, hyphens only (no underscores, no spaces, no special chars)
- Must start and end with an alphanumeric character
- Becomes the namespace prefix for all skills and commands:
  `skill-name` in a plugin named `code-tools` → invoked as `/code-tools:skill-name`

### Versioning
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Start at `0.1.0` for new plugins
- Increment PATCH for bug fixes, MINOR for new features, MAJOR for breaking changes

---

## .mcp.json — MCP Server Configs

Located at the plugin root. Same format as Claude Code's standard `.mcp.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

### Transport types

| Type | Use case | Auth |
|------|----------|------|
| `stdio` | Local binaries, Node/Python scripts | None needed |
| `sse` | Hosted servers with OAuth | OAuth 2.0 |
| `http` | REST-based remote servers | Bearer token / headers |

### Path portability
Always use `${CLAUDE_PLUGIN_ROOT}` for paths to files inside the plugin. Never hardcode
absolute paths — the plugin might be installed anywhere.

### Environment variables
For credentials, use `${ENV_VAR_NAME}` syntax and document required env vars in `README.md`:
```json
"env": { "SLACK_TOKEN": "${SLACK_BOT_TOKEN}" }
```

---

## hooks/hooks.json — Event Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/lint.sh",
            "timeout": 60
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Summarize what was accomplished in this session.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Available events

| Event | When |
|-------|------|
| `PreToolUse` | Before a tool call |
| `PostToolUse` | After a tool call |
| `Stop` | When Claude finishes a response |
| `SubagentStop` | When a subagent finishes |
| `SessionStart` | Session begins |
| `SessionEnd` | Session ends |
| `UserPromptSubmit` | User sends a message |
| `PreCompact` | Before context compaction |

### Hook types
- **`command`**: Runs a shell command. Good for deterministic checks (lint, format, test).
- **`prompt`**: Invokes Claude with a prompt. Good for complex logic that benefits from LLM reasoning.

---

## settings.json — Default Settings

Optional file to apply defaults when the plugin is enabled. Currently only `agent` is supported:

```json
{
  "agent": "agent-name"
}
```

Setting `agent` activates one of the plugin's agents as the main thread. This changes how
Claude Code behaves by default when the plugin is enabled.

---

## Packaging Format

A `.plugin` file is a standard ZIP archive. The plugin folder must be the top-level entry:

```
my-plugin.plugin (zip)
└── my-plugin/               ← top-level folder = plugin name
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/...
```

Build command:
```bash
cd /tmp && zip -r my-plugin.plugin my-plugin/ -x "*.DS_Store" -x "*/__pycache__/*" -x "*/evals/*"
```
