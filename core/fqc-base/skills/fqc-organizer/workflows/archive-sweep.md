# Archive Sweep Workflow

Use when the user wants to retire a set of documents — archiving them so they're excluded from search results without deleting them from the vault.

## When to use
- "Archive everything tagged #project/old-site"
- "Archive all documents older than 6 months"
- "Clean up old drafts"
- "Retire all the cancelled project docs"

## Tool sequence: `search_documents` → confirm → `archive_document`

### 1. Find the candidate set

```
// By tag
search_documents(tags: ["#project/old-site"], mode: "filesystem", limit: 50)

// By topic
search_documents(query: "old pricing model", mode: "mixed", limit: 20)
```

For "archive anything older than X months," filesystem mode sorts by last-modified date — present documents with dates so the user can make informed decisions.

### 2. Show candidates and confirm

This step is especially important for archive operations — archiving is not easily reversed from the AI's side.

> "I found 5 documents that match:
> - Old Pricing Brief (clients/acme/pricing-old.md) — last modified 8 months ago
> - 2025 Site Architecture (research/old-site-arch.md) — last modified 11 months ago
> - ...
>
> Archiving will hide these from search results. Files stay on disk. Proceed?"

### 3. Execute: `archive_document` (batch- or single-capable)

`identifiers` accepts either an array (batch) or a single string (one document). Bulk sweeps use the array form:

```
archive_document(
  identifiers: ["clients/acme/pricing-old.md", "research/old-site-arch.md", ...]
)
```

The single-identifier form is also valid — useful for a confirmed one-off inside a larger organizing session:

```
archive_document(identifiers: "clients/acme/pricing-old.md")
```

Response: one line per document (`{path}: archived`) or error lines for failures.

### 4. Report results

Tell the user how many were archived, which failed, and remind them files remain on disk.

---

## Reversibility note

`archive_document` is a soft archive — files remain on disk with `status: archived` in frontmatter. There is no `unarchive_document` tool; reverting requires manual frontmatter edit + vault scan. Always mention this in your confirmation prompt.
