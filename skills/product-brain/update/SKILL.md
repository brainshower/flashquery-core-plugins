---
name: update
description: >
  Use this skill when the user wants to change the status of a Product Brain
  document — mark something as resolved, shipped, archived, done, blocked,
  or otherwise update its lifecycle state. Trigger on "mark X as resolved",
  "this is done", "archive this note", "ship the login feature spec",
  "X is blocked", "close out that work item", "this decision is made",
  "mark that as shipped", or any request to change a document's status without
  rewriting its content. Also trigger when the user says "update the status of X"
  or "change X to Y". This is intentionally lightweight — for content edits,
  use Capture (to add new content) or the user can edit directly in Obsidian.
---

# Update

Change the status of a Product Brain document. This is a thin, fast operation — it updates the database record and the vault document's frontmatter without rewriting the document body.

## When to use

Use this skill for lifecycle state changes: marking something as resolved, shipped, archived, or any other status transition. This isn't for editing document content — it's for recording that the state of something changed.

Valid statuses:
- `active` — the default state, currently relevant
- `resolved` — questions answered, research concluded, decision made
- `archived` — no longer relevant, kept for historical reference
- `shipped` — built and released (primarily for feature specs and work items)

## Steps

### 1. Identify the target document

The user might reference the document by name, topic, or description. Use `search_records` and/or `search_all` to find the right document:

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `query`: the user's reference to the document (semantic search on the record)

If the reference is ambiguous and multiple results match, present the top candidates and ask the user to confirm which one.

### 2. Update the database record

Call `update_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `id`: the record ID of the target document
- `fields`:
  ```json
  {
    "status": "<new status>",
    "updated_at": "<current ISO timestamp>"
  }
  ```

### 3. Update the vault document frontmatter

Call `update_doc_header` with:
- `identifier`: the `fqc_id` of the target document
- `frontmatter_updates`: `{ "status": "<new status>" }`

This keeps the file and database in sync. The `on_document_changed` callback would catch this too, but writing both together is cleaner.

### 4. Confirm

Tell the user what was updated — document title, old status → new status. Keep it brief.

If the status change implies a natural next step, offer it once:
- Marked a research note as `resolved` → "This has enough material to draft a feature spec — want me to run Draft?"
- Marked a feature spec as `shipped` → "Want me to archive the related work items too?"

## Notes

- This skill intentionally does not rewrite document bodies. If the user wants to edit content, they should edit in Obsidian or ask Capture to append new information.
- The `plugin_id` for all tool calls is `"product-brain"`.
- The Product Brain doc suggests Update may eventually be folded into Capture as a recognized intent. For now it exists as a standalone skill because the interaction pattern is different — Update is a quick status flip, Capture is a three-beat content flow.
