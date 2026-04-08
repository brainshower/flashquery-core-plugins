---
description: Reconcile the FQC database against the vault filesystem
argument-hint: [dry-run]
---

Verify every FQC database row against the current vault filesystem by calling `reconcile_documents`.

The user ran this because they suspect the database has drifted from the vault — files were moved, renamed, or deleted outside FQC, and search results feel wrong or incomplete.

## Instructions

**Default:**
Call `reconcile_documents(dry_run: false)`.

**If the user passed "dry-run" as an argument ($ARGUMENTS contains "dry-run"):**
Call `reconcile_documents(dry_run: true)` to preview changes without applying them. Prefix your report with "[DRY RUN]" and offer to run the real reconcile if the preview looks correct.

## What reconcile does

- Scans all database rows for this instance
- For each row whose vault file is missing: scans the vault for a file with matching fqc_id in frontmatter
- **Moved** rows: updates the database path to the new location
- **Truly missing** rows: promotes status from `missing` to `archived` (permanent removal from search)

## Reporting results

Report clearly:
- Total documents checked
- Moved (with old path → new path for each)
- Archived as missing (with path for each)

If nothing needed fixing: "Reconciliation complete — {n} documents checked. Everything is in sync."

## Key distinction from /fqc-base:vault-scan

| | /fqc-base:vault-scan | /fqc-base:reconcile |
|---|---|---|
| Direction | Filesystem → Database | Database → Filesystem |
| Missing status | Marks as `missing` (soft) | Promotes to `archived` (permanent) |
| Use when | You added files to the vault | You moved/deleted files from the vault |

If the user is unsure which to run, suggest `/fqc-base:vault-health` — it runs both in sequence.

## Performance note

`reconcile_documents` scans the entire vault to build an fqc_id index. Let the user know it may take a moment on large vaults. The operation is idempotent — safe to run multiple times.
