---
name: Product Brain
version: 0.1.0
---

# Product Brain

A product knowledge management plugin for FlashQuery Core. Capture fragments, research, feature specs, and work items through conversation — the plugin handles filing, tagging, connection-surfacing, and periodic review.

## What it does

Product Brain gives you a structured vault for product thinking, organized around **projects**. Each project has an inbox for quick captures, folders for research notes, feature specs, and work items, and a daily log for continuity across sessions. An AI assistant routes content to the right place, surfaces connections between fragments, and synthesizes what you've accumulated into briefs on demand.

The plugin uses FlashQuery Core's three-layer storage model: Markdown documents in the vault (readable in Obsidian or any editor), structured database records for fast querying, and memories for ambient intelligence.

## Skills

The plugin includes 12 user-facing skills, organized by purpose:

### Getting started

| Skill | Description |
|-------|-------------|
| `init` | One-time setup — creates database tables, templates, tag vocabulary, and your first project |
| `add-project` | Add new projects, list existing ones, switch active project, or archive |
| `menu` | Contextual directory of available skills with suggested starting points |

### Daily workflow

| Skill | Description |
|-------|-------------|
| `orient` | Morning brief — where you left off, inbox status, open threads, flagged items |
| `capture` | Save a thought, link, observation, or task to the vault |
| `update` | Quick status changes — mark items as resolved, shipped, archived, or blocked |
| `close` | End-of-day wrap-up — logs what got done, sets up tomorrow's starting point |

### Synthesis and review

| Skill | Description |
|-------|-------------|
| `retrieve` | Search and find content across the vault |
| `brief` | Deep synthesis — feature briefs, milestone summaries, lineage traversal |
| `draft` | Turn accumulated research into a feature spec |
| `review-loop` | Process inbox items, route sparks, check open questions, surface connections |
| `organize` | Large-scale cleanup — triage backlogs, migrate notes, periodic housekeeping |

## Callback handlers

Three system-level handlers manage vault changes that happen outside skill invocations:

| Callback | Purpose |
|----------|---------|
| `on_document_discovered` | Routes new vault documents to the correct project, auto-registers templates |
| `on_document_changed` | Syncs database when files are edited externally (frontmatter, open questions, timestamps) |
| `on_document_deleted` | Soft-deletes database records, preserves provenance chains |

Callback specifications are in `references/callbacks/`.

## Reference files

| File | Purpose |
|------|---------|
| `references/schema.yaml` | Plugin schema defining all 5 database tables, folder claims, and memory config |
| `references/tags-default.md` | Default tag vocabulary (Workflow, Handoff, Classification, Source groups) |
| `references/templates/*.md` | Base document templates for spark, research note, feature spec, work item, and daily log |

## Document types

| Type | Template | Typical location |
|------|----------|-----------------|
| Spark | `spark.md` | `{project}/inbox/` |
| Research Note | `research-note.md` | `{project}/research/` |
| Feature Spec | `feature-spec.md` | `{project}/specs/` |
| Work Item | `work-item.md` | `{project}/work/` |
| Daily Log | `daily-log.md` | Project root |

## Getting started

1. Install the plugin
2. Run **Init** to set up the database tables, templates, and your first project
3. Run **Capture** to add your first item
4. Use **Orient** at the start of each session and **Close** at the end
5. Run **Review Loop** periodically to process accumulated inbox items
