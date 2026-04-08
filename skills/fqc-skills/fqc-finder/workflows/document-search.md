# Document Search Workflow

Use this workflow when the user specifically wants to find vault documents, or when the query is clearly about structured notes, files, or written content.

## When to use

- "Find my notes on X"
- "Show me the documents about X"
- "Do I have a proposal for Acme?"
- "Show me what's been worked on recently"
- "Find all meeting notes tagged #client/acme"

## Tool: `search_documents`

`search_documents` supports three modes — choose based on the query type:

| Mode | When to use | What it does |
|------|-------------|--------------|
| `"filesystem"` (default) | Tag filtering, browsing recent docs, when embeddings may be stale | Scans vault, filters by tags/query substring, sorts by last-modified |
| `"semantic"` | Natural-language topic query, finding conceptually related docs | Semantic similarity search via pgvector |
| `"mixed"` | Comprehensive search — want both relevance-ranked and exhaustive results | Semantic first, then filesystem to fill remaining slots |

## Steps

### 1. Choose the mode

- **Filter by tag or recency** → `filesystem`
- **"Find documents about X" (topic-based)** → `semantic` or `mixed`
- **"Show me what's recent"** → `filesystem` with no query, sorted by recency
- **Unsure / want completeness** → `mixed`

### 2. Call `search_documents`

```
search_documents(
  tags: [...],           // optional tag filters
  tag_match: "any",      // or "all" if multiple tags must all match
  query: "...",          // required for semantic/mixed; optional for filesystem
  mode: "mixed",
  limit: 10
)
```

### 3. Triage results efficiently

`search_documents` in filesystem mode doesn't return fqc_ids. If you need fqc_ids for a batch of results (e.g., to link or tag them), call `get_doc_outline` with an array of paths — this returns database metadata for all of them at once without reading file bodies.

For a smaller number of highly relevant results, call `get_document` to read the full content.

### 4. Synthesize and respond

Answer the user's question, citing document titles and paths. If the user asked "do I have X?", confirm clearly. If you found relevant content, summarize it.

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

To quickly check structure (headings, links, fqc_id) without loading the full body:
```
get_doc_outline(identifiers: "clients/acme/proposal.md")
```

To batch-check metadata on multiple results:
```
get_doc_outline(identifiers: ["path1.md", "path2.md", "path3.md"])
```
(Array mode returns only DB metadata — no file reads — very efficient for triage.)
