# Memory Recall Workflow

Use this workflow when the user wants to retrieve something they previously saved to memory.

## When to use

- "What did I save about X?"
- "What did I remember about Acme's communication style?"
- "Show me all my memories tagged #client/acme"
- "Pull up that memory about the integration timeline"

## Decision tree

```
Does the user have a specific topic in mind?
  ├── Yes → use search_memory (semantic recall)
  └── No, they want to browse → use list_memories (tag-filtered or recent)
            ↓
Does the user need the full content of a specific memory?
  └── Yes → use get_memory with the ID
```

---

## Semantic recall: `search_memory`

```
search_memory(
  query: "Acme communication preferences",
  tags: [...],        // optional; narrow by tag if appropriate
  tag_match: "any",   // optional; defaults to "any". Pass "all" to require every tag.
  limit: 10,
  threshold: 0.7      // default; lower to 0.5 for broader results
)
```

Tag intersection is genuinely useful for memory recall because memories are often multi-tagged (`#client/acme` + `#topic/pricing`, for example). Pass `tag_match: "all"` when the user's question sits at the overlap of two or more topics:

```
search_memory(
  query: "pricing conversations",
  tags: ["#client/acme", "#topic/pricing"],
  tag_match: "all"
)
```

Results include a similarity score, preview content (truncated at 200 chars), and a memory ID. If content is truncated, call `get_memory(memory_ids: "{id}")`.

**If `search_memory` errors** (embedding unavailable): Fall back to `list_memories` with relevant tag filters.

---

## Browsing: `list_memories`

Use when the user wants to see what's stored without a specific query.

```
list_memories(
  tags: ["#client/acme"],   // optional
  tag_match: "any",
  limit: 50
)
```

Returns memories sorted by recency (newest first), content previewed at 200 characters.

**Common patterns:**
- "Show me all my memories tagged #client/acme" → `list_memories(tags: ["#client/acme"])`
- "What have I saved recently?" → `list_memories()` (no filters)

---

## Full content: `get_memory`

```
get_memory(memory_ids: "c3d4e5f6-a7b8-9012-cdef-123456789012")

// or batch:
get_memory(memory_ids: ["id1", "id2", "id3"])
```

Used as a follow-up after `search_memory` or `list_memories` when the preview is insufficient.

---

## Example flows

**"What did I save about Acme's communication preferences?"**
→ `search_memory(query: "Acme communication preferences", tags: ["#client/acme"])`
→ `get_memory(memory_ids: "{top result id}")` for full content
→ "You saved a memory noting that Acme prefers async communication. Full note: [content]"

**"Pull up the memory about the integration timeline"**
→ `search_memory(query: "integration timeline")`
→ `get_memory(memory_ids: "{top result id}")`
→ Present full content
