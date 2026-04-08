# Memory Cleanup Workflow

Use when the user wants to review and archive outdated or irrelevant memories in bulk.

## When to use
- "Clean up old memories about the website project"
- "Archive my outdated memories tagged #project/old-site"
- "Prune memories from last year that are no longer relevant"

## Tool sequence: `list_memories` → confirm → `archive_memory` (per ID)

### 1. Find the candidate memories

```
list_memories(
  tags: ["#project/website"],
  tag_match: "any",
  limit: 50
)
```

Or use semantic search:
```
search_memory(query: "old pricing model")
```

### 2. Show candidates and confirm

Memory cleanup requires human judgment. Present memories with content previews and creation dates:

> "Here are 8 memories tagged #project/website. Which would you like to archive?
>
> 1. [2025-03-12] 'Website v2 launch planned for Q2 2025' — likely outdated?
> 2. [2026-01-15] 'Website project paused pending budget approval'
> ...
>
> Tell me which numbers to archive, or say 'all' to archive everything listed."

If a preview is truncated, call `get_memory(memory_ids: "{id}")` for the full content before the user decides.

### 3. Execute: `archive_memory` (loop per memory)

`archive_memory` takes a single ID at a time — loop through the confirmed IDs:

```
archive_memory(memory_id: "c3d4e5f6-a7b8-9012-cdef-123456789012")
archive_memory(memory_id: "d4e5f6a7-b8c9-0123-defa-234567890123")
// ...
```

### 4. Report results

Tell the user how many memories were archived and note any failures.

---

## Reversibility note

`archive_memory` is a soft delete — archived memories are excluded from `search_memory` and `list_memories` but are preserved in the database. There is no unarchive tool; recovery would require direct database access. Mention this to users who seem to think archiving is permanent deletion.
