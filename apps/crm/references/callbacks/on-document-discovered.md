# on_document_discovered

FQC callback that fires for every new vault document the scanner detects, whether created by a skill or added externally by the user on the filesystem.

## Parameters

- `path` — vault-relative path of the new document
- `fqc_id` — UUID assigned by FQC's core document system
- `asserted_ownership` — pre-populated by the discovery orchestrator's folder-matching logic. Contains the plugin ID if the document's folder matches a declared `documents.types` entry in the schema, or empty if no match was found.

## Return value

One of four claim values:
- `'owner'` — this plugin owns the document
- `'read-write'` — watcher with write intent
- `'read-only'` — watcher without write intent
- `'none'` — no interest

## Current implementation: STUB

<!-- TODO: Implement full callback logic. See Future Work section in README.md. -->

This callback currently returns a no-op response:

- If `asserted_ownership` identifies this plugin (`"crm"`), return `claim: 'owner'` — acknowledge ownership but take no further action.
- Otherwise, return `claim: 'none'`.

No database records are created. No template auto-registration occurs.

## Future implementation

When fully implemented, this callback should:

1. **Route new documents in CRM folders.** If the path is under a declared CRM folder (e.g., `CRM/`, `CRM/Contacts/`, `CRM/Companies/`), read the document's frontmatter to determine whether it's a contact note or company profile, then create the corresponding record in `crm_contacts` or `crm_businesses` with the `fqc_id`.

2. **Handle externally-created documents.** If a user creates a contact note manually in Obsidian (matching the template structure), the callback should detect it and register it in the database so it appears in `search_records` queries.

3. **Auto-register custom templates.** If the template system is migrated to `_plugin/templates/`, detect new template files dropped into that folder and register them in a template registry table.

4. **Handle ambiguous documents.** If a document lands in a CRM folder but doesn't match a known template structure, log it and skip — don't create a malformed record.
