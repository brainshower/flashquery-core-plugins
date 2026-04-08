# Memory Cleanup Workflow

Use this workflow when the user wants to review and archive outdated or irrelevant memories in bulk.

## When to use

- "Clean up old memories about the website project"
- "Archive my outdated memories tagged #project/old-site"
- "Prune memories from last year that are no longer relevant"
- "I want to clean up what I've saved about Acme — a lot of it is outdated"

## Tool sequence: `list_memories` → confirm → `archive_memory` (loop)

---

## Steps

### 1. Find the candidate memories

Call `list_memories` with the relevant tag filters. This surfaces memories sorted by recency so you can identify old ones:

```
list_memories(
  tags: ["#project/website"],   // tag filter to scope the search
  tag_match: "any",
  limit: 50
)
```

If the user wants to clean up memories without a clear tag filter, use `list_memories` with no filters to browse recent memories, or use `search_memory` with a descriptive query:

```
search_memory(query: "old pricing model")
```

### 2. Show candidates and confirm

Memory cleanup requires human judgment — the AI can't always tell which memories are outdated. Present the candidates with their content previews and creation dates, and ask the user which to archive:

> "Here are 8 memories tagged #project/website. Which would you like to archive?
>
> 1. [2025-03-12] 'Website v2 launch planned for Q2 2025' — likely outdated?
> 2. [2025-08-01] 'Homepage redesign handed off to contractor team'
> 3. [2026-01-15] 'Website project paused pending budget approval'
> ...
>
> Tell me which numbers to archive, or say 'all' to archive everything listed."

If a memory preview is truncated (200 chars) and you need the full content to assess relevance, call `get_memory(memory_ids: "{id}")` on it.

### 3. Execute: `archive_memory` (loop per memory)

Unlike `archive_document`, `archive_memory` takes a single ID at a time. Loop through the confirmed IDs:

```
// For each memory_id the user wants to archive:
archive_memory(memory_id: "c3d4e5f6-a7b8-9012-cdef-123456789012")
archive_memory(memory_id: "d4e5f6a7-b8c9-0123-defa-234567890123")
// ...
```

Each call returns: `Memory archived (id: {id}). Tags updated to include #status/archived.`

### 4. Report results

Tell the user:
- How many memories were archived
- Which (if any) failed

---

## Notes

- `archive_memory` is a soft delete. Archived memories are excluded from `search_memory` and `list_memories` but are preserved in the database.
- Memories are not permanently deleted by any tool. If the user later wants to recover an archived memory, that would require direct database access.
- Mention this to the user if they seem to think archiving is permanent deletion.

---

## Example

**"Clean up old memories about the website project"**

```
// Step 1
list_memories(tags: ["#project/website"], limit: 50)

// Show user the list with dates and previews
// User says: "Archive numbers 1, 2, and 5"

// Step 3
archive_memory(memory_id: "{id1}")
archive_memory(memory_id: "{id2}")
archive_memory(memory_id: "{id5}")
```

**"Archive all my outdated memories about the old pricing model"**

```
// Step 1
search_memory(query: "old pricing model")

// Present results, confirm
// Step 3 — loop through confirmed IDs
```
