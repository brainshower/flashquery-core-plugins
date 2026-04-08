---
name: vault-scan
description: Trigger an immediate FlashQuery Core vault scan to discover new files, detect moved files, and track deletions. This is a slash command (/vault-scan) that the user runs explicitly after importing files into the vault outside the conversation, or when they suspect the index is stale. Trigger on "/vault-scan" or when the user says "scan my vault," "sync my vault," "I just added files," "resync FQC," or "my vault is out of date."
command: /vault-scan
---

# /vault-scan

Triggers an immediate vault scan via the `force_file_scan` MCP tool. Use this when the user has added, moved, or modified files outside of the conversation and needs FQC to catch up.

## When the user runs this

- They just imported files into the vault folder outside the conversation
- They added files manually (drag and drop, script, another app)
- Search results feel stale or they know a document exists but can't find it
- They want to confirm FQC is in sync before starting a working session

## Workflow

### Standard scan (synchronous — default)

```
force_file_scan(background: false)
```

This waits for the scan to complete and returns counts of what changed. Report the results to the user:

> "Vault scan complete:
> - New: 3 files indexed
> - Moved: 1 file (path updated)
> - Deleted: 0 files
> - Hash mismatches (external edits detected): 2"

If all counts are zero:
> "Vault scan complete — everything is already in sync. No changes detected."

### Background scan (if user passes `background` argument)

If the user runs `/vault-scan background` (or says something equivalent like "scan in the background"), call:

```
force_file_scan(background: true)
```

The tool returns immediately. Let the user know the scan is running in the background and they can continue working — FQC will index the new files as the scan completes.

## Result fields to report

The `force_file_scan` response includes counts for:
- **New** — files discovered in the vault that FQC wasn't tracking
- **Moved** — files that changed path (identified by their fqc_id frontmatter)
- **Deleted/missing** — files that FQC had tracked but can no longer find
- **Hash mismatches** — files that were externally edited since the last scan (re-embedding will be triggered)

Report all counts, even zeros — it confirms the scan covered each case.

## Differences from /reconcile

- `/vault-scan` walks the **filesystem → database**: discovers new files, updates moved file paths, marks missing files as `missing` (a soft, potentially temporary status).
- `/reconcile` walks the **database → filesystem**: verifies each database row, and promotes truly missing files from `missing` to `archived` (permanent removal from search).
- If you ran `/vault-scan` and still have lingering issues (documents missing from search that should exist), suggest the user run `/reconcile` next.

## Error handling

- If `force_file_scan` returns an error, report it to the user with the message. Common causes: database connectivity issues, vault path configuration problem.
- The scan is idempotent — running it multiple times is safe.
