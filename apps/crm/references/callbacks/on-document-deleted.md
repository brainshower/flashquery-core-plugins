# on_document_deleted

FQC callback that fires when a vault document owned or watched by this plugin is deleted from the filesystem.

## Parameters

- `fqc_id` — UUID of the deleted document
- `path` — last known vault-relative path

## Current implementation: STUB

<!-- TODO: Implement full callback logic. See Future Work section in README.md. -->

This callback currently takes no action. It acknowledges the deletion notification and returns successfully.

## Future implementation

When fully implemented, this callback should:

1. **Archive the corresponding plugin record.** Look up the `fqc_id` in `crm_contacts` and `crm_businesses`. If found, call `archive_record` to soft-delete the record. Do not hard-delete — the record may still be referenced by interaction records or opportunity records.

2. **Handle interaction orphans gracefully.** If the deleted document was a contact, the `crm_interactions` records that reference that `contact_id` should remain — they represent historical data. Skills that query interactions should handle the case where the linked contact record is archived.

3. **Handle opportunity orphans.** Same logic — opportunity records referencing a deleted contact or business should be flagged for review but not automatically deleted.

4. **Clean up memories if appropriate.** Optionally archive memories scoped to the deleted entity. This is a judgment call — some memories (deal context, relationship dynamics) may still be valuable even after the entity document is gone. Consider flagging rather than archiving.

5. **Log the deletion.** Save a memory noting that the entity was deleted and when, so the AI can inform the user if they later ask about the entity.
