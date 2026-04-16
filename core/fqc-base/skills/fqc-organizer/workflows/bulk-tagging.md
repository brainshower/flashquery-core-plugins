# Bulk Tagging Workflow

Use when the user wants to apply or remove tags across a set of documents matching some criteria.

## When to use
- "Tag all the Q1 deliverables as complete"
- "Add #type/research to all my research docs"
- "Remove the #status/draft tag from all client proposals"

## Tool sequence: `search_documents` → confirm → `apply_tags`

### 1. Find the candidate set

```
search_documents(
  tags: ["#project/q1", "#type/deliverable"],
  tag_match: "all",
  mode: "filesystem",
  limit: 50
)
```

Filesystem mode is preferred for bulk operations — no stale embeddings, no missed results.

### 2. Show candidates and confirm

> "I found 7 documents that match your criteria:
> - Q1 Kickoff Notes (clients/acme/q1-kickoff.md)
> - Q1 Design Deliverable (deliverables/q1-design.md)
> - ...
>
> I'll add `#status/complete` and remove `#status/draft` from all of them. OK to proceed?"

### 3. Execute with a single `apply_tags` call (batch-capable)

```
apply_tags(
  identifiers: ["path1.md", "path2.md", "path3.md", ...],
  add_tags: ["#status/complete"],
  remove_tags: ["#status/draft"]
)
```

`apply_tags` returns a line per document showing the final tag set. Review for errors.

### 4. Report results

Report how many documents were updated, which (if any) failed, and example final tag sets.

---

## Status tag handling

Only one `#status/*` tag is allowed per document. To change status, include the old status in `remove_tags` and the new one in `add_tags` in the same call.

---

## Tagging a memory

`apply_tags` also accepts a single `memory_id` (UUID string) instead of `identifiers`. The add/remove semantics are identical, but only one memory can be tagged per call — there is no batch form for memories.

```
apply_tags(
  memory_id: "c3d4e5f6-a7b8-9012-cdef-123456789012",
  add_tags: ["#client/acme"],
  remove_tags: ["#draft"]
)
```

**Validation behavior:** The tool requires at least one of `identifiers` or `memory_id`. Passing neither returns: `"Error: At least one of identifiers or memory_id must be provided."` The two parameters are conceptually mutually exclusive but not schema-enforced — if both are passed, the `identifiers` branch runs first and `memory_id` is silently ignored. Choose one per call.

When to reach for the memory form: a user says "tag that memory about Acme's budget as `#client/acme`" — find the memory via `search_memory` or `list_memories`, then apply tags to its ID. For bulk memory retagging across many IDs, loop the call (one per memory).
