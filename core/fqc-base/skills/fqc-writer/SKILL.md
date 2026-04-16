---
name: fqc-writer
description: Create, modify, and organize vault documents and memories using FlashQuery Core. Use this skill whenever the user wants to write something up, draft a note, create a document, add content to an existing document, insert content at a specific heading, replace the content of a specific section, prepend content to the top of a doc, tag documents, link docs together, remember something for later, update a memory, or archive/forget a memory. Trigger on phrases like "write this up," "create a document about," "draft a note on," "add a section to," "log this under the Interactions heading," "rewrite the Pricing section," "insert this after the Background heading," "put a status banner at the top," "save this as a doc," "tag this document," "link these two docs," "update the meeting notes," "remember that," "save this for later," "update that memory," "that memory is outdated," "forget that," or "archive the memory about." Even casual phrases like "jot this down" or "keep track of this" should trigger fqc-writer.
---

# fqc-writer

This skill orchestrates FlashQuery Core's document and memory write tools. Its job is to figure out what the user wants to capture or organize, choose the right tool sequence, and execute it cleanly.

## What this skill owns

- Creating new vault documents
- Modifying existing documents (body content, frontmatter, tags, links)
- Section-scoped edits: inserting at a specific heading/position, replacing a specific section's content
- Saving, updating, and archiving memories

Tool surface includes `create_document`, `update_document`, `append_to_doc`, `insert_in_doc`, `replace_doc_section`, `update_doc_header`, `apply_tags`, `insert_doc_link`, `archive_document`, `save_memory`, `update_memory`, `archive_memory`, plus `get_document` and `get_doc_outline` as read-side helpers.

## Routing heuristic

Read the user's intent and route to the appropriate workflow:

| User intent | Workflow |
|-------------|----------|
| Create a brand-new document | → [Document Creation](workflows/document-creation.md) |
| Append content to the end of a document | → [Document Modification](workflows/document-modification.md) |
| Insert at a specific heading/position, or replace a specific section | → [Section Editing](workflows/section-editing.md) |
| Rewrite the entire body of a document | → [Document Modification](workflows/document-modification.md) |
| Change tags, links, or metadata only | → [Document Modification](workflows/document-modification.md) |
| Archive one or more documents | → [Document Modification](workflows/document-modification.md) |
| Save a new memory ("remember that...") | → [Memory Management](workflows/memory-management.md) |
| Update or correct an existing memory | → [Memory Management](workflows/memory-management.md) |
| Archive or forget a memory | → [Memory Management](workflows/memory-management.md) |

If the request involves both creating a document AND saving a memory (e.g., writing up meeting notes that also surface a key takeaway), handle both in sequence: document creation first, then `save_memory`.

### Picking the right body-edit tool

Body edits span four tools — choose by where the edit anchors, not by habit:

- `append_to_doc` — tack content onto the end, no section awareness.
- `insert_in_doc` — add at a specific anchor (after/before a heading, end of a section, top, bottom).
- `replace_doc_section` — swap the body of one named section, preserving the rest.
- `update_document` — rewrite the full body (triggers re-embedding of the whole document).

If the user names a heading or describes a position, the section-editing tools are almost always the right pick — they preserve surrounding content, avoid unnecessary re-embeddings, and return the old section content for easy undo when replacing. Reach for `update_document` only when the whole body genuinely needs to change.

## Error handling

Always check `isError` on every tool response before proceeding. Common recoveries:
- **Write lock timeout** — retry once after 3 seconds. Tell the user if it fails again.
- **File not tracked (no fqc_id)** — call `get_document` first to auto-provision, then retry the mutation.
- **Tag validation failure** — check for multiple `#status/*` tags; use `apply_tags` with `remove_tags` to resolve conflicts before adding new ones.
- **File already exists** — use `update_document` or `append_to_doc` instead of `create_document`.

## Key conventions

- Always prefer `fqc_id` over vault paths for any reference you need to store or use later — paths can change when users rename or move files.
- After `create_document`, parse the `fqc_id` from the second line of the response (`fqc_id: {uuid}`).
- `apply_tags` is always preferred over passing `tags` in `update_document` for incremental add/remove. Use `update_document`'s `tags` parameter only when replacing the entire tag list.
- Embeddings are fire-and-forget — a document just created may not appear in semantic search immediately. This is normal; let the user know if they seem confused by this.
