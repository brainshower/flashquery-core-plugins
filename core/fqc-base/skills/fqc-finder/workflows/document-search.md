# Document Search Workflow

Use this workflow when the user specifically wants to find vault documents.

## When to use

- "Find my notes on X"
- "Show me the documents about X"
- "Do I have a proposal for Acme?"
- "Show me what's been worked on recently"
- "Find all meeting notes tagged #client/acme"

## Tool: `search_documents`

Choose the mode based on the query type:

| Mode | When to use | What it does |
|------|-------------|--------------|
| `"filesystem"` (default) | Tag filtering, browsing recent docs, when embeddings may be stale | Scans vault, filters by tags/query substring, sorts by last-modified |
| `"semantic"` | Natural-language topic query | Semantic similarity search via pgvector |
| `"mixed"` | Want both relevance-ranked and exhaustive results | Semantic first, then filesystem to fill remaining slots |

## Steps

1. **Choose the mode:** Tag/recency filtering → `filesystem`. Topic-based query → `semantic` or `mixed`. Want completeness → `mixed`.

2. **Call `search_documents`:**
   ```
   search_documents(
     tags: [...],           // optional tag filters
     tag_match: "any",      // or "all" if multiple tags must all match
     query: "...",          // required for semantic/mixed; optional for filesystem
     mode: "mixed",
     limit: 10
   )
   ```

3. **Triage results efficiently.** To get fqc_ids for multiple results without reading file bodies, call `get_doc_outline` with an array of paths — returns database metadata for all at once.

4. **Synthesize and respond.** Answer the user's question, citing titles and paths.

## Common patterns

**"Find my meeting notes with Acme"**
```
search_documents(tags: ["#client/acme", "#type/meeting-notes"], mode: "filesystem")
```

**"Show me documents about competitor pricing"**
```
search_documents(query: "competitor pricing", mode: "semantic")
```

**"What have I been working on recently?"**
```
search_documents(mode: "filesystem")  // no filters — returns 20 most recent
```

**"Find all draft proposals"**
```
search_documents(tags: ["#type/proposal", "#status/draft"], tag_match: "all", mode: "filesystem")
```

## Getting full content

After search, to read a specific document:
```
get_document(identifier: "clients/acme/proposal.md")
```

To quickly check structure (headings, links, fqc_id):
```
get_doc_outline(identifiers: "clients/acme/proposal.md")
```

To batch-check metadata on multiple results (no file reads — efficient):
```
get_doc_outline(identifiers: ["path1.md", "path2.md", "path3.md"])
```

### `get_doc_outline` optional parameters

- `max_depth` (integer, optional) — cap the heading levels returned when inspecting a single document. Effective values are **1–5**: pass `max_depth: 2` to return only H1s and H2s, for example. Omit (or pass `6`) to include every level — the underlying filter is a no-op at 6, so "unlimited" is the default.
- `exclude_headings` (boolean, optional, default `false`) — when `true`, return frontmatter + outbound links only and skip the heading tree entirely. Useful when you just need the fqc_id, tags, or link graph.

**Mode note:** `exclude_headings` only applies when `identifiers` is a single string (full-file outline). When `identifiers` is an array, the tool runs in batch DB mode and **never** returns headings regardless of the flag — that mode is intentionally metadata-only.

### Token-efficient triage pattern

- **Batch metadata scan** — pass `identifiers` as an array to get fqc_ids, tags, titles, and link graph for many files in one call. Headings are never returned in this mode, so no need to set `exclude_headings`.
- **Single-document structure inspection** — pass a single string identifier and, if you only care about the top of the outline, set `max_depth: 2` or `max_depth: 3` to keep the response compact.

## When search returns unexpectedly empty

If the user just added or moved files outside the chat and search returns nothing you'd expect to see, the scanner may not have picked them up yet. Run `force_file_scan()` to reindex, then retry the search. Pass `background: true` for fire-and-forget if the user doesn't need to see the scan results inline. See the vault-maintenance workflow in fqc-organizer for the full scan behavior.
