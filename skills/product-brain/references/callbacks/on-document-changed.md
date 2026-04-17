# on_document_changed

FQC callback that fires when a vault document owned by the plugin is modified. This is the reactive counterpart to the Update skill — when the user edits a file directly in Obsidian or another editor, this callback keeps `prodbrain_documents` in sync.

## Parameters

- `path` — vault-relative path of the changed document
- `fqc_id` — UUID of the document
- `changes` — a `ChangePayload` containing:
  - `frontmatter` — parsed YAML of current frontmatter
  - `content` — full body text after frontmatter
  - `modified_at` — timestamp of the modification
  - `content_hash` — hash of the current content

There is no pre-computed diff. The payload is current state; the callback compares against the database record to determine what changed.

## Execution logic

### 1. Load current database state

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: matched on `fqc_id`

to get the stored record for comparison.

### 2. Frontmatter sync

Check two custom frontmatter fields:

**`type`** — if `changes.frontmatter` contains a `type` value that differs from `prodbrain_documents.document_type`, update the record via `update_record`.

**`status`** — if `changes.frontmatter` contains a `status` value that differs from `prodbrain_documents.status`, update the record via `update_record`.

This covers the case where a user manually edits these fields directly in the file via Obsidian's frontmatter editor.

Note: Tags are FQC-managed and are NOT synced here. `prodbrain_documents.tags` is written by `apply_tags` when skills tag a document — it's not read back from frontmatter.

### 3. Open questions sync

If the document type is `research_note`:

Scan `changes.content` directly for the presence of non-empty content under the "Open Questions" heading. No `get_document` call is needed — the content is already in the payload.

If the result differs from the stored `has_open_questions` boolean, update `prodbrain_documents` via `update_record`.

This is the most important sync operation. The Review Loop depends on the `has_open_questions` flag for efficient filtering — if a user resolves an open question by editing directly in Obsidian, this callback ensures the flag gets updated.

### 4. Template sync

If the path is under `_plugin/templates/`:

Read the updated frontmatter to check whether `name` or `document_type` have changed. Call `search_records` on `prodbrain_templates` and update via `update_record` if either value differs.

### 5. Update timestamp

Always update `prodbrain_documents.updated_at` via `update_record` to reflect the file's `modified_at` timestamp.

### Return

`{ acknowledged: true }`

## Notes

- Skills that write changes (Update, Capture, Close) update the database directly as part of their execution. This callback is for changes made outside the AI interface. The callback should be idempotent — re-applying the same values from a skill-triggered change is harmless.
