---
title: FlashQuery CRM Plugin
version: 1.4.0
---
# FlashQuery CRM Plugin

A dissolved CRM powered by FlashQuery Core. There is no CRM application — just your AI, connected to FQC via MCP, managing contacts, businesses, and interactions through conversation. Your data lives in formats you own: Postgres tables you can query directly, markdown files you can open in Obsidian, semantic memories stored in vector embeddings.

## Prerequisites

This plugin requires a working FlashQuery Core installation. It does **not** bundle FQC itself — FQC is shared infrastructure that all FQC plugins depend on, so it's installed once at the environment level.

- **FlashQuery Core MCP server** — installed and connected to your AI assistant. The CRM plugin calls FQC tools (`create_document`, `create_record`, `search_records`, `save_memory`, etc.) and will not function without them. See the [FlashQuery Core README](https://github.com/flashquery/flashquery-core) for installation instructions.
- **Supabase instance** — configured and connected to FQC. This is where your CRM records and document embeddings live.
- **Obsidian vault** (or any markdown-compatible file system) — for vault documents. Contact profiles, company overviews, and interaction timelines are stored as markdown files you can read and edit directly.

## Setup

1. Install this plugin in Claude Code or Cowork.
2. Tell your AI: **"Initialize CRM plugin"** — this runs the `initialize-plugin` skill, which registers the schema and creates four database tables.
3. During initialization, you'll be asked where CRM documents should live in your vault — either a single folder for everything (e.g., `CRM/`) or separate folders for contacts and companies (e.g., `CRM/Contacts/` and `CRM/Companies/`). This preference is saved as a memory so all skills know where to create documents, with plugin_scope as "CRM".
4. Start using it: `"Add a contact for Sarah Chen at Acme Corp. She's VP of Marketing."`

## Skills

| Skill | What it does |
|-------|-------------|
| **initialize-plugin** | One-time setup — registers the CRM schema with FQC, creates database tables |
| **add-contact** | Creates a new contact: vault document + linked database record + business wikilinks |
| **add-business** | Creates a new business: vault document + linked database record |
| **find-entity** | Searches for contacts and businesses by name, tags, relationships, or full detail |
| **log-interaction** | Records an interaction: database record + vault timeline entry + last_interaction update |
| **crm-intel** | Intelligence synthesis — meeting prep, dossiers, pipeline status, follow-up awareness |
| **crm-memory** | Save, search, and update impressions, preferences, and ambient intelligence |
| **update-entity** | Updates tags, pipeline stage, relationship type, or name on an existing contact or company |
| **add-opportunity** | Creates a new opportunity record linked to a contact and/or company for pipeline tracking |
| **archive-entity** | Soft-archives a contact or company across all three data layers (document, record, memories) |

## Data Architecture

The CRM uses FQC's three-layer storage model:

**Documents (vault)** — The human layer. Contact profiles and company overviews as markdown files, readable in Obsidian. Interaction history appended chronologically. Wikilinks between documents form the relationship graph. This is the primary data store.

**Records (Supabase)** — The query layer. Minimal structured fields for fast lookups, date-range queries, and tag-based filtering. Records help the AI *find* documents — they don't duplicate document content.

| Table | Key columns | Queries enabled |
|-------|-------------|-----------------|
| contacts | name, last_interaction, tags, fqc_id | Find by name; "who haven't I talked to in 30 days?"; pipeline stage filter |
| businesses | name, tags, fqc_id | Find by name; filter by industry tag |
| interactions | contact_id, business_id, date, tags | "All interactions with Sarah"; date-range queries; interaction type filter |
| opportunities | name, contact_id, business_id, close_date, tags | "Show me all active opportunities"; "what's closing this quarter?"; pipeline stage filter |

**Memories** — The AI-only layer. Impressions, communication preferences, deal signals, and company intelligence that surface when relevant. Also stores user behavioral preferences that shape how skills operate (e.g., "always lead briefings with opportunity status").

| Category | What it captures |
|----------|-----------------|
| communication_preferences | How contacts prefer to be reached, response patterns, best times |
| relationship_context | Rapport notes, sensitivities, personal details, communication dynamics |
| deal_context | Pricing signals, budget constraints, negotiation positions, decision timelines |
| company_intelligence | Market position, org changes, competitive signals, strategic direction |

## Templates

The `templates/` directory contains vault document templates:
- `contact_note.md` — Template for contact documents (6 sections: Contact Information, Relationship Context, Communication, Opportunities, Next Steps, Interaction Timeline)
- `company_profile.md` — Template for company documents (5 sections: Company Information, What They Do, Key Contacts, Opportunities, Notes)

Templates use `{{placeholder}}` syntax and HTML comments for AI guidance.

## References

The `references/` directory contains shared files used across skills. These are the canonical sources for the plugin's data model and vocabulary — edit them here if you want to customize the CRM for your setup.

- `schema.yaml` — The complete database schema: all four tables, their columns, types, and the memory category configuration. This is passed to `register_plugin` during initialization and serves as the authoritative data model reference for any skill that needs to understand the underlying structure. **If you add columns or change the schema, re-run "Initialize CRM" to apply the changes.**
- `tags.md` — The CRM tag taxonomy: native tag vocabulary, what user language maps to each tag, and how to handle user-defined custom tags.

## Design Principles

This plugin follows the five FQC plugin design principles:

- **P-01: Minimum Column Principle** — Records have the fewest columns possible. A column earns its place only if required for a structural query.
- **P-02: Tags Belong to the User** — Tags are the user's organizational vocabulary, visible in Obsidian's tag pane. Never system bookkeeping.
- **P-03: Wikilinks for Relationships** — Cross-entity associations use `[[wikilinks]]` in vault documents, not columns or tags.
- **P-04: Document Cognitive Load Test** — Templates pass the 30-second scan test. Lean sections, HTML comment guidance.
- **P-05: Three-Layer Routing Test** — Every attribute is routed to the right layer: document (human-readable), record (AI-queryable), or memory (AI-only).
