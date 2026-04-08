---
name: fqc-writer
description: Create, modify, and organize vault documents and memories using FlashQuery Core. Use this skill whenever the user wants to write something up, draft a note, create a document, add content to an existing document, tag documents, link docs together, remember something for later, update a memory, or archive/forget a memory. Trigger on phrases like "write this up," "create a document about," "draft a note on," "add a section to," "save this as a doc," "tag this document," "link these two docs," "update the meeting notes," "remember that," "save this for later," "update that memory," "that memory is outdated," "forget that," or "archive the memory about." Even casual phrases like "jot this down" or "keep track of this" should trigger fqc-writer.
---

# fqc-writer

This skill orchestrates FlashQuery Core's document and memory write tools. Its job is to figure out what the user wants to capture or organize, choose the right tool sequence, and execute it cleanly.

## What this skill owns

- Creating new vault documents
- Modifying existing documents (body content, frontmatter, tags, links)
- Saving, updating, and archiving memories

## Routing heuristic

Read the user's intent and route to the appropriate workflow:

| User intent | Workflow |
|-------------|----------|
| Create a brand-new document | → [Document Creation](workflows/document-creation.md) |
| Add content to an existing document | → [Document Modification](workflows/document-modification.md) |
| Change tags, links, or metadata only | → [Document Modification](workflows/document-modification.md) |
| Archive one or more documents | → [Document Modification](workflows/document-modification.md) |
| Save a new memory ("remember that...") | → [Memory Management](workflows/memory-management.md) |
| Update or correct an existing memory | → [Memory Management](workflows/memory-management.md) |
| Archive or forget a memory | → [Memory Management](workflows/memory-management.md) |

If the request involves both creating a document AND saving a memory (e.g., writing up meeting notes that also surface a key takeaway), handle both in sequence: document creation first, then `save_memory`.

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
