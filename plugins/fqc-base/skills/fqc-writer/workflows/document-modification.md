# Document Modification Workflow

Use this workflow when the user wants to change an existing document — adding content, updating the body, changing tags, modifying metadata, inserting links, or archiving.

## Decision tree

```
What kind of change does the user want?
  ├── Add a new section / append content → append_to_doc
  ├── Replace or rewrite the body → update_document
  ├── Change tags only → apply_tags
  ├── Change other frontmatter (custom fields, title) → update_doc_header
  ├── Add a link between documents → insert_doc_link
  └── Archive / retire the document → archive_document
```

---

## Appending content

**Tool:** `append_to_doc`

Use when the user wants to add a section, log entry, or block of content to an existing document **without replacing what's already there**.

1. Identify the document (use fqc_id, path, or filename — prefer fqc_id or full path to avoid ambiguity).
2. If you're not sure of the document's structure, call `get_doc_outline` first to understand headings before appending.
3. Call `append_to_doc`:
   - `identifier` — the document
   - `content` — the full markdown to append, including any headings (e.g., `"## New Section\n\nBody text here."`)
4. The tool inserts two blank lines before the appended content automatically.

**When to use `get_doc_outline` first:** If the user says "add a section after X" or "continue the existing notes," read the structure first to understand where things sit before writing the appended content.

---

## Replacing/rewriting the body

**Tool:** `update_document`

Use when the user wants to replace the document's body entirely, or change both body and metadata together.

1. If you need to see the current content first (to preserve parts of it), call `get_document` to read it.
2. Call `update_document`:
   - `identifier` — the document
   - `content` — the new body (omit to leave body unchanged)
   - `title` — new title (omit to preserve existing)
   - `tags` — **replaces the entire tag list**; use `apply_tags` instead for incremental changes
   - `frontmatter` — additional fields to merge in (cannot override `fqc_id`, `fqc_instance`, `created`, `status`)

**Important:** `update_document` always triggers re-embedding. For metadata-only changes (tags, frontmatter), prefer `apply_tags` or `update_doc_header` to avoid unnecessary re-embedding.

**Untracked file recovery:** If the tool returns `"Document at {path} has no fqc_id in frontmatter"`, call `get_document` first (which auto-provisions the fqc_id), then retry.

---

## Changing tags

**Tool:** `apply_tags`

Use for any incremental tag add/remove. This is the preferred tool for tag mutations — it handles validation, normalization, and conflict detection.

1. Call `apply_tags`:
   - `identifiers` — the document(s); can be a single identifier or an array for batch operations
   - `add_tags` — tags to add (idempotent — adding an existing tag is safe)
   - `remove_tags` — tags to remove (silent no-op if not present)

**Status tag conflicts:** You can only have one `#status/*` tag at a time. To change status, pass the old status in `remove_tags` and the new one in `add_tags` in the same call.

**Batch tagging:** To tag many documents at once, pass an array of identifiers to `identifiers`. All documents get the same add/remove applied. (For large batch operations based on a search, use fqc-organizer instead.)

---

## Changing frontmatter metadata

**Tool:** `update_doc_header`

Use when the user wants to change non-tag frontmatter fields (custom fields like `client`, `project`, `due-date`, etc.) without touching the body. This does NOT trigger re-embedding, making it more efficient than `update_document` for metadata-only changes.

1. Call `update_doc_header`:
   - `identifier` — the document
   - `updates` — a map of fields to set; pass `null` as a value to delete a field

**Note:** If the `updates` map includes a `tags` key and there are existing conflicting status tags in the frontmatter, the tool will error and direct you to use `apply_tags` first to resolve conflicts.

---

## Linking documents

**Tool:** `insert_doc_link`

Use when the user wants to create a relationship between two existing documents.

1. Call `insert_doc_link`:
   - `identifier` — the source document (the one that gets the link added)
   - `target` — the document to link to
   - `property` — optional; defaults to `"links"`; use `"related"`, `"parent"`, `"child"`, etc. for specific relationship types

The tool resolves both identifiers and adds a `[[Target Title]]` wikilink to the source's frontmatter. Duplicate links are silently ignored.

---

## Archiving documents

**Tool:** `archive_document`

Use when the user wants to retire one or more documents. Archived documents are excluded from search results but remain on disk.

1. Call `archive_document`:
   - `identifiers` — a single identifier or an array for batch archiving

The tool updates both the vault frontmatter and the database. It's idempotent — archiving an already-archived document is safe. For large-scale archive sweeps based on search criteria, use fqc-organizer.

---

## Example patterns

**"Add the pricing section to the proposal doc"**
→ `get_doc_outline` (understand structure) → `append_to_doc` (content: `"## Pricing\n\n..."`)

**"Update the Acme meeting notes with what we just discussed"**
→ `get_document` (read current content) → `update_document` (with revised/extended body) OR `append_to_doc` (if it's an additive update)

**"Tag all the Q1 deliverables as complete"**
→ For a single doc: `apply_tags` (add: `#status/complete`, remove: `#status/draft`)
→ For bulk: use fqc-organizer

**"Archive the old pricing brief"**
→ `archive_document` (identifiers: "clients/acme/pricing-brief.md")

**"Set the client field on the proposal to 'Acme'"**
→ `update_doc_header` (updates: `{ client: "Acme" }`)
