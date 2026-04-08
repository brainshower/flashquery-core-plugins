# Memory Management Workflow

Use this workflow when the user wants to save, update, or archive a memory. Memories are persistent facts, preferences, observations, and key takeaways stored in FQC's database — not as vault files. They're designed to surface in future conversations so relevant context is always available without re-reading documents.

## Decision tree

```
What does the user want?
  ├── Save something new → save_memory
  ├── Update/correct an existing memory → search_memory → get_memory → update_memory
  └── Archive/forget a memory → search_memory → get_memory → archive_memory
```

---

## Saving a new memory

**Tool:** `save_memory`

Use when the user says "remember that," "save this for later," "keep track of," "note that," or when a workflow (like writing meeting notes) surfaces a key takeaway worth retaining across sessions.

1. Write a precise, self-contained memory:
   - Good: `"Acme Corp prefers async communication and dislikes back-to-back meetings."`
   - Bad: `"Acme communication preferences"` (too vague — won't match well in semantic search)
   - Include the relevant subject, context, and specifics. The richer the memory, the better it surfaces in future searches.

2. Call `save_memory`:
   - `content` — the memory text (precise and self-contained)
   - `tags` — categorize with relevant tags (e.g., `["#client/acme"]`, `["#project/website"]`)
   - `plugin_scope` — optional; use to scope the memory to a specific plugin domain (e.g., `"crm"`). Omit for general/global memories.

3. Parse the memory ID from the response: `Memory saved (id: {uuid}).` The ID is between `(id: ` and `)`.

4. Tell the user the memory was saved. If it was an incidental save (e.g., during document creation), briefly mention what was saved.

**What makes a good memory:**
- Facts about clients, contacts, projects, or preferences that might not be in a document
- Decisions made and the reasoning behind them
- Constraints, preferences, or requirements that recur across conversations
- Key outcomes from calls or meetings (the "so what" — not a transcript)

**What should stay as a document, not a memory:**
- Long-form content, structured notes, or anything the user might want to read in full
- Information that's already well-captured in a tagged vault document

---

## Updating an existing memory

**Tool sequence:** `search_memory` → `get_memory` → `update_memory`

Use when the user says "update that memory," "that's changed," "correct the memory about," or "that information is outdated."

1. **Find the memory:**
   Call `search_memory` with a descriptive query about what the memory contains.
   Example: `search_memory(query: "Acme communication preferences")`

2. **Confirm you have the right one:**
   Call `get_memory` with the ID from the search result to retrieve the full content.
   Present the current content to the user: "Here's the current memory: [content]. Is this the one you want to update?"
   (Skip explicit confirmation if the match is unambiguous and the user's intent is clear.)

3. **Update it:**
   Call `update_memory`:
   - `memory_id` — the ID of the memory to update
   - `content` — the new/corrected content
   - `tags` — new tags (omit to preserve existing tags)

4. Parse the new version ID from the response: `New version id: {uuid}.` Store this if you need to reference the memory again — the old ID still works for `get_memory` but `update_memory` and `archive_memory` expect the latest version's ID.

5. Tell the user what was changed.

**Note on versioning:** `update_memory` preserves the original — it creates a new version rather than overwriting. This is non-destructive; the history is kept internally.

---

## Archiving (forgetting) a memory

**Tool sequence:** `search_memory` → `get_memory` → `archive_memory`

Use when the user says "forget that," "that's no longer relevant," "archive the memory about," or "remove that memory."

1. **Find the memory:**
   Call `search_memory` with a descriptive query.

2. **Confirm the right one:**
   Call `get_memory` to retrieve the full content. Present it to the user before archiving: "Found this memory: [content]. Should I archive it?"
   (Skip if unambiguous and the user's intent is clear.)

3. **Archive it:**
   Call `archive_memory`:
   - `memory_id` — the memory to archive

4. Confirm to the user that the memory was archived. Note that it's a soft delete — it's hidden from search but not permanently gone.

---

## Example patterns

**"Remember that Acme prefers async communication"**
→ `save_memory` (content: "Acme Corp prefers async communication over real-time calls.", tags: `["#client/acme"]`)

**"Actually, Acme switched to weekly syncs — update that memory"**
→ `search_memory` ("Acme communication preferences") → `get_memory` (confirm) → `update_memory` (content: "Acme Corp moved to weekly sync calls as of Q2 2026; they previously preferred fully async communication.")

**"Forget the memory about the old pricing model"**
→ `search_memory` ("old pricing model") → `get_memory` (confirm) → `archive_memory`

**"Save a memory that the Q1 project review is on hold pending legal sign-off"**
→ `save_memory` (content: "Q1 project review is on hold pending legal sign-off as of April 2026.", tags: `["#project/q1-review", "#status/blocked"]`)
