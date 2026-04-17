# FlashQuery Plugins

Official plugin marketplace for [FlashQuery Core](https://github.com/flashquery/flashquery-core) — the open source, local-first data management layer for AI workflows.

Plugins extend FlashQuery Core with domain-specific skills, database schemas, document templates, and workflow automation. Each plugin runs entirely through conversation — there is no separate application UI. Your AI assistant calls FlashQuery Core's MCP tools to manage structured data, vault documents, and semantic memories on your behalf.

Your data stays yours: Postgres tables you can query directly, Markdown files you can open in Obsidian, and vector embeddings stored in your own Supabase instance.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| **[FlashQuery CRM](./apps/crm)** | Contact and relationship management through conversation. Track contacts, businesses, interactions, opportunities, and pipeline status across three data layers. | 1.5.0 |
| **[Product Brain](./apps/product-brain)** | Product knowledge management. Capture sparks, research notes, feature specs, and work items in a structured vault with AI-assisted organization and synthesis. | 0.1.0 |
| **[FlashQuery Base](./core/fqc-base)** | Core skills for writing, finding, and organizing vault documents and memories, plus vault maintenance commands. | 1.0.0 |

## Getting Started

### Prerequisites

You need two things before installing plugins:

1. **FlashQuery Core** — installed and running as an MCP server connected to your AI assistant. Plugins call FlashQuery Core tools (`create_document`, `search_records`, `save_memory`, etc.) and will not function without them. See the [FlashQuery Core repo](https://github.com/flashquery/flashquery-core) for installation instructions.

2. **Claude Code** — the CLI tool from Anthropic. Plugins are distributed as a Claude Code marketplace. You can install Claude Code from [claude.com/claude-code](https://claude.com/claude-code).

### Add the Marketplace

Point Claude Code at this repository to access all available plugins:

```
/plugin marketplace add flashquery/flashquery-plugins
```

This registers the FlashQuery plugin marketplace in your Claude Code configuration. You only need to do this once.

### Browse Available Plugins

Once the marketplace is added, you can see what's available:

```
/plugin marketplace list
```

### Install a Plugin

Install any plugin by name:

```
/plugin install crm@flashquery-plugins
```

```
/plugin install product-brain@flashquery-plugins
```

```
/plugin install fqc-base@flashquery-plugins
```

### Initialize After Installing

Each plugin that manages data needs a one-time setup. After installing, tell your AI assistant to run the plugin's init skill:

- **FlashQuery CRM**: "Initialize CRM" — creates database tables and configures vault folder structure
- **Product Brain**: "Initialize Product Brain" — creates database tables, templates, tag vocabulary, and your first project

The init conversation will walk you through any configuration choices (like where to store documents in your vault).

### Update Plugins

Pull the latest versions of all plugins:

```
/plugin marketplace update flashquery-plugins
```

## How Plugins Work

A FlashQuery plugin is a bundle of **skills** — conversational workflows that your AI assistant follows when you ask it to do something. When you say "add a contact for Sarah Chen at Acme Corp," the AI reads the `add-contact` skill, which tells it exactly which FlashQuery Core tools to call, in what order, and with what parameters.

Plugins use FlashQuery Core's three-layer storage model:

- **Documents** — Markdown files in your vault, readable in Obsidian or any text editor. This is the human layer.
- **Records** — Structured rows in Postgres (via Supabase) for fast queries. This is the query layer.
- **Memories** — Semantic embeddings for ambient intelligence that surfaces at the right moment. This is the AI layer.

Every plugin skill routes information to the appropriate layer based on who needs it and how it will be accessed.

## Repository Structure

```
flashquery-plugins/
├── .claude-plugin/
│   └── marketplace.json        # Marketplace catalog
├── apps/
│   ├── crm/                    # FlashQuery CRM plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/             # 10 conversational skills
│   │   ├── references/         # Schema, tags, callbacks
│   │   ├── templates/          # Document templates
│   │   └── README.md
│   └── product-brain/          # Product Brain plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/             # 12 conversational skills
│       ├── references/         # Schema, tags, templates, callbacks
│       └── README.md
├── core/
│   └── fqc-base/               # Base skills plugin
└── README.md                   # This file
```

## Building Your Own Plugin

Plugins follow a standard structure that Claude Code understands:

```
your-plugin/
├── .claude-plugin/
│   └── plugin.json             # Plugin manifest (name, version, description)
├── skills/
│   └── your-skill/
│       └── SKILL.md            # Skill definition
├── references/
│   ├── schema.yaml             # Database tables and folder claims
│   └── tags.md                 # Tag vocabulary
└── README.md
```

The `schema.yaml` file defines your plugin's database tables and is passed to FlashQuery Core's `register_plugin` tool during initialization. Skills are Markdown files that describe step-by-step workflows using FlashQuery Core's MCP tools. See any plugin in this repository for a working example.

For design guidance, refer to the [Plugin Building Considerations](https://github.com/flashquery/flashquery-core-product/blob/main/Plugins%20and%20Skills/Plugin%20Building%20Considerations.md) document, which covers schema design, callback handlers, skill patterns, tag vocabularies, and the scanning pattern.

## Contributing

We welcome contributions — new plugins, improvements to existing ones, or documentation fixes. If you're building a plugin for a new domain, open an issue first to discuss the design. The Plugin Building Considerations document is required reading before submitting a new plugin.

## License

This repository is part of the FlashQuery project. See [LICENSE](./LICENSE) for details.

## Links

- [FlashQuery Core](https://github.com/flashquery/flashquery-core) — the MCP server that powers all plugins
- [Claude Code Plugin Docs](https://code.claude.com/docs/en/plugins) — how Claude Code plugins work
- [Plugin Marketplace Docs](https://code.claude.com/docs/en/plugin-marketplaces) — creating and distributing marketplaces
