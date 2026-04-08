---
description: Full vault health check — scan, reconcile, and surface hygiene issues
---

Run a comprehensive FlashQuery Core vault health check across three stages. The user wants a complete status picture of their vault.

## Stage 1: Vault Scan

Call `force_file_scan(background: false)` and report counts:
- New files indexed
- Moved (paths updated)
- Missing/deleted
- External edits detected (hash mismatches)

## Stage 2: Reconciliation

Call `reconcile_documents(dry_run: false)` and report:
- Total documents checked
- Paths fixed (moved files)
- Files archived (permanently missing)

## Stage 3: Hygiene Audit

Call `search_documents(mode: "filesystem")` to scan active documents. Look for:
1. **Untagged documents** — documents with no categorization tags beyond `#status/active` (no `#type/*`, `#client/*`, or `#project/*` tags). Hard to discover later.
2. **Stale drafts** — documents tagged `#status/draft`. Surface these for the user's awareness.

For a broader check, also run `search_documents(tags: ["#status/draft"], mode: "filesystem")`.

## Stage 4: Summary Report

Present a clean consolidated summary:

```
## Vault Health Report

**Scan:** {n} new | {n} moved | {n} missing | {n} external edits
**Reconcile:** {n} docs checked | {n} paths fixed | {n} archived
**Hygiene:** {n} total active docs | {n} untagged | {n} stale drafts

**Status:** Clean ✓   — or —   Issues found (see above)
```

If issues were found, be specific and offer to help address them (e.g., "Want me to help tag those untagged documents?" or "I can archive old drafts if you'd like.").

## Error handling

If any stage fails, report the error and continue to the next stage — partial results are still useful. Note which stages completed and which failed in the summary.

## Performance note

This command runs two expensive operations back to back. Let the user know it may take a moment on large vaults.
