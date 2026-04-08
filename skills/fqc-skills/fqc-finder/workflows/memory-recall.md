# Memory Recall Workflow

Use this workflow when the user wants to retrieve something they previously saved to memory — a preference, fact, observation, or key takeaway.

## When to use

- "What did I save about X?"
- "What did I remember about Acme's communication style?"
- "Show me all my memories tagged #client/acme"
- "Pull up that memory about the integration timeline"
- "What do I know about X?" (when context suggests it might be in memory, not just docs)

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

Use when the user describes what they're looking for — even vaguely.

```
search_memory(
  query: "Acme communication preferences",
  tags: [...],        // optional; narrow by tag if appropriate
  limit: 10,
  threshold: 0.7      // default; lower to 0.5 if you want broader results
)
```

Results include a similarity score, preview content (truncated at 200 chars), and a memory ID.

**If content is truncated:** Call `get_memory(memory_ids: "{id}")` to retrieve the full content.

**If `search_memory` errors** (embedding unavailable): Fall back to `list_memories` with relevant tag filters.

---

## Browsing: `list_memories`

Use when the user wants to see what's stored without a specific query — browsing by tag or looking at recent memories.

```
list_memories(
  tags: ["#client/acme"],   // optional; omit to browse all recent memories
  tag_match: "any",
  limit: 50                  // default
)
```

Returns memories sorted by recency (newest first), with content previewed at 200 characters.

**Common patterns:**

- "Show me all my memories tagged #client/acme" → `list_memories(tags: ["#client/acme"])`
- "What have I saved recently?" → `list_memories()` (no filters)
- "Show me everything I've noted about the website project" → `list_memories(tags: ["#project/website"])`

---

## Full content: `get_memory`

Use to retrieve the complete content of one or more specific memories by ID.

```
get_memory(memory_ids: "c3d4e5f6-a7b8-9012-cdef-123456789012")

// or batch:
get_memory(memory_ids: ["id1", "id2", "id3"])
```

Typically used as a follow-up after `search_memory` or `list_memories` when the preview is insufficient.

---

## Example flows

**"What did I save about Acme's communication preferences?"**
→ `search_memory(query: "Acme communication preferences", tags: ["#client/acme"])`
→ If top result looks right: `get_memory(memory_ids: "{id}")` for full content
→ Answer: "You saved a memory noting that Acme prefers async communication. Here's the full note: [content]"

**"Show me all my memories tagged #client/acme"**
→ `list_memories(tags: ["#client/acme"])`
→ Present the list, noting IDs for any the user might want to read in full

**"Pull up the memory about the integration timeline"**
→ `search_memory(query: "integration timeline")`
→ `get_memory(memory_ids: "{top result id}")`
→ Present full content
