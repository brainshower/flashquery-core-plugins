# on_document_deleted

FQC callback that fires when a vault document owned by the plugin is deleted or archived via FQC.

## Parameters

- `path` — vault-relative path of the deleted document
- `fqc_id` — UUID of the document
- `deleted_at` — optional timestamp of the deletion

## Execution logic

### 1. Confirm the record exists

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: matched on `fqc_id`

### 2. Archive the document record

Call `archive_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `id`: the record ID

This is a soft delete — the record remains in the database for historical context. The fact that a document existed and what it contained is still useful for understanding state history and diagnosing orphaned provenance rows.

### 3. Handle provenance

Rows in `prodbrain_provenance` that reference the deleted `fqc_id` (as either `source_fqc_id` or `derived_fqc_id`) are left in place. They represent historical lineage — the fact that a spec was derived from a now-deleted research note is still meaningful context.

Skills that traverse provenance (Brief, Draft) must handle `get_document` returning "not found" gracefully and treat such entries as historical references rather than errors.

### 4. Handle templates

If the path is under `_plugin/templates/`:

Call `search_records` on `prodbrain_templates` matched on `fqc_id`. Archive the matching record via `archive_record`. A template file that no longer exists should not be offered to skills at runtime.

### Return

`{ acknowledged: true }`

## Notes

- Nothing is hard-deleted. Archived records are still queryable for historical analysis.
- Provenance preservation is intentional — breaking lineage chains would make it impossible to understand why a feature spec exists or what signals originally drove a decision.
