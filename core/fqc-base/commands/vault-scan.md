---
description: Scan the FQC vault to discover new, moved, and deleted files
argument-hint: [background]
---

Trigger an immediate FlashQuery Core vault scan by calling `force_file_scan`.

The user ran this because they added, moved, or modified files outside the conversation and need FQC to catch up.

## Instructions

**Default (synchronous scan):**
Call `force_file_scan(background: false)` and wait for results.

**If the user passed "background" as an argument ($ARGUMENTS contains "background"):**
Call `force_file_scan(background: true)` and let the user know the scan is running in the background.

## Reporting results

After a synchronous scan, report all four counts — even zeros confirm coverage:

- **New** — files discovered that FQC wasn't tracking
- **Moved** — files that changed path (identified by fqc_id frontmatter)
- **Deleted/missing** — files FQC tracked but can no longer find (marked as `missing` — a soft, recoverable status)
- **Hash mismatches** — files externally edited since the last scan (re-embedding triggered)

If all counts are zero: "Vault scan complete — everything is already in sync."

If there are lingering issues after the scan (documents still missing from search), suggest running `/fqc-base:reconcile` next — it promotes truly missing `missing` rows to `archived` status.

## Error handling

If `force_file_scan` returns an error, report the message. Common causes: database connectivity issues, vault path misconfiguration. The scan is idempotent — safe to run multiple times.
