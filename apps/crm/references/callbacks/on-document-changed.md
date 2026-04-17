# on_document_changed

FQC callback that fires when a vault document owned or watched by this plugin is modified. Receives the full current state of the document, not a diff.

## Parameters

- `fqc_id` — UUID of the changed document
- `path` — current vault-relative path
- `changes` — object containing:
  - `frontmatter` — full current frontmatter of the document
  - `content` — full current body content of the document

## Current implementation: STUB

<!-- TODO: Implement full callback logic. See Future Work section in README.md. -->

This callback currently takes no action. It acknowledges the change notification and returns successfully.

## Future implementation

When fully implemented, this callback should:

1. **Sync tags between vault document and database record.** If the user edits tags in Obsidian's frontmatter, detect the change and call `update_record` to sync the `tags` field on the corresponding `crm_contacts` or `crm_businesses` record.

2. **Sync title changes.** If the user renames a document's title in frontmatter, update the `name` field on the database record.

3. **Detect status changes.** If the user changes the `status` field in frontmatter (e.g., from `active` to `archived`), propagate that to the database record.

4. **Be idempotent.** Skills that modify files (update-entity, log-interaction, etc.) update plugin tables directly as part of their execution. When the scanner later picks up those file changes and fires this callback, it should re-read the same values and apply the same updates harmlessly. No duplicate records, no conflicting state.
