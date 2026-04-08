# Archive Sweep Workflow

Use this workflow when the user wants to retire a set of documents — archiving them so they're excluded from search results without deleting them from the vault.

## When to use

- "Archive everything tagged #project/old-site"
- "Archive all documents older than 6 months"
- "Clean up old drafts"
- "Retire all the cancelled project docs"

## Tool sequence: `search_documents` → confirm → `archive_document`

---

## Steps

### 1. Find the candidate set

Call `search_documents` with the criteria that defines what should be archived:

```
// By tag
search_documents(
  tags: ["#project/old-site"],
  mode: "filesystem",
  limit: 50
)

// By keyword or topic
search_documents(
  query: "old pricing model",
  mode: "mixed",        // mixed covers both semantic matches and filesystem results
  limit: 20
)
```

For "archive anything older than X months," use filesystem mode. Note that `search_documents` in filesystem mode sorts by last-modified date — you can use this to identify old documents and filter them manually after retrieval.

### 2. Show candidates and confirm

This step is especially important for archive operations — archiving is not easily reversed from the AI's side (files remain on disk but are excluded from search).

Present the list clearly:

> "I found 5 documents that match your criteria. Here's what I'd archive:
> - Old Pricing Brief (clients/acme/pricing-old.md) — last modified 8 months ago
> - 2025 Site Architecture (research/old-site-arch.md) — last modified 11 months ago
> - ...
>
> Archiving will hide these from search results. The files stay on disk. Proceed?"

If the user wants to exclude any, refine accordingly.

### 3. Execute: `archive_document`

Pass all confirmed identifiers in a single call — `archive_document` is batch-capable:

```
archive_document(
  identifiers: [
    "clients/acme/pricing-old.md",
    "research/old-site-arch.md",
    ...
  ]
)
```

The response has one line per document: `{path}: archived` or an error line for any that couldn't be archived.

### 4. Report results

Tell the user:
- How many documents were archived successfully
- Which (if any) couldn't be archived, and why
- A reminder that files remain on disk and can be found manually if needed

---

## Notes on reversibility

- `archive_document` is a soft archive — the vault file is updated to `status: archived` and the database is flagged. Files remain on disk.
- To unarchive, the user would need to manually update the document's frontmatter status back to `active` and run a vault scan. There is no `unarchive_document` tool.
- Always confirm before archiving, and mention this in your confirmation prompt.

---

## Example

**"Archive everything tagged #project/old-site"**

```
// Step 1
search_documents(tags: ["#project/old-site"], mode: "filesystem")

// Step 3 (after confirmation with user)
archive_document(identifiers: ["research/old-site-arch.md", "clients/acme/old-scope.md"])
```

**"Clean up anything in my vault that looks like an old draft from 2025"**

```
// Step 1 — search broadly, then filter by date/relevance
search_documents(
  tags: ["#status/draft"],
  mode: "filesystem",
  limit: 50
)
// Present results with dates; let user confirm which ones to archive
```
