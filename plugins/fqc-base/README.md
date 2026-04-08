# fqc-base

Core FlashQuery skills for writing, finding, and organizing vault documents and memories, plus vault maintenance slash commands.

This plugin provides the foundational AI workflows for day-to-day use of FlashQuery Core. Install it alongside any FQC instance to give Claude the tool sequences it needs to work with your vault naturally.

---

## Skills

Skills are auto-invoked by Claude based on what you say. You don't call them directly.

### fqc-writer
**Triggers on:** "write this up," "create a document about," "draft a note on," "add a section to," "remember that," "save this for later," "update that memory," "forget that," and similar phrases.

Orchestrates document creation, modification, and memory management:
- Creates new vault documents with appropriate tags and optional linking
- Modifies existing documents (append content, update body, change tags, update metadata)
- Saves, updates, and archives memories

### fqc-finder
**Triggers on:** "find documents about," "what do we know about," "show me the notes from," "give me a briefing on," "what did I save about," "pull up that memory about," and similar phrases.

Orchestrates search and retrieval across your vault:
- Unified search across documents and memories (`search_all`)
- Document-focused search with tag/keyword/semantic modes
- Memory recall (semantic search + tag browsing)
- Briefings: structured overview of a topic using tags
- Plugin record search

### fqc-organizer
**Triggers on:** "clean up," "organize," "archive old documents," "bulk tag," "tag everything in this project as," "archive anything older than," and similar phrases.

Orchestrates bulk operations with a confirm-before-execute workflow:
- Bulk tagging of documents matching search criteria
- Archive sweeps (find candidates → show → confirm → archive)
- Bulk memory cleanup

---

## Commands

Commands are slash commands you invoke explicitly.

| Command | Description |
|---------|-------------|
| `/fqc-base:vault-scan` | Scan the vault to discover new, moved, and deleted files. Accepts optional `background` argument. |
| `/fqc-base:reconcile` | Reconcile the database against the filesystem — fixes stale paths, archives truly missing files. Accepts optional `dry-run` argument. |
| `/fqc-base:vault-health` | Full health check: scan + reconcile + hygiene audit in one comprehensive report. |

### When to use each

**`/fqc-base:vault-scan`** — after importing files into your vault outside the conversation. Walks the filesystem to update the database.

**`/fqc-base:reconcile`** — after moving or deleting files outside FQC. Walks the database to verify each file still exists, fixes moved paths, and permanently archives truly deleted files.

**`/fqc-base:vault-health`** — periodic maintenance or when something feels off. Runs both of the above plus a hygiene audit in one go.

---

## MCP Tools Required

This plugin's skills call the following FQC MCP tools. Your FQC instance must be running and connected for this plugin to work:

**Document tools:** `create_document`, `get_document`, `update_document`, `archive_document`, `search_documents`, `reconcile_documents`

**Compound document tools:** `append_to_doc`, `update_doc_header`, `insert_doc_link`, `apply_tags`, `get_doc_outline`, `get_briefing`, `search_all`

**Memory tools:** `save_memory`, `search_memory`, `update_memory`, `get_memory`, `list_memories`, `archive_memory`

**Maintenance tools:** `force_file_scan`

**Plugin/record tools (optional):** `search_records` — only needed if querying plugin records via fqc-finder.

---

## Plugin Composition

`fqc-base` is designed to be the foundation layer. Plugin-specific skills (like `fqc-crm`) can delegate to these core skills for vault and memory operations, then layer their own record tool orchestration on top.

For example, an `fqc-crm` skill that needs to create a contact note would use `fqc-writer`'s document creation logic, then call `create_record` directly to link the plugin record.
