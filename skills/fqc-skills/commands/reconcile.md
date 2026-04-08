---
name: reconcile
description: Verify that every FlashQuery Core database row still has a corresponding vault file, fix stale paths, and archive records for permanently missing files. This is a slash command (/reconcile) for when the user suspects the database has drifted from the vault — files were moved, renamed, or deleted outside FQC, and search results feel wrong or incomplete. Trigger on "/reconcile" or when the user says "my database is out of sync," "reconcile FQC," "fix stale paths," "documents are missing from search," "clean up orphan records," or "I moved a bunch of files and search is broken."
command: /reconcile
---

# /reconcile

Verifies every FQC database row against the current vault filesystem state. Use this when the user suspects the database is out of sync with their vault — typically after bulk file moves, renames, or deletions done outside of FQC.

## When the user runs this

- They moved or renamed many files outside FQC and search results are now wrong
- Documents they know exist aren't appearing in search
- They ran `/vault-scan` and still have issues
- Periodic maintenance (recommend occasionally alongside `/vault-health`)

## Workflow

### Standard reconcile (default)

```
reconcile_documents(dry_run: false)
```

This scans all database rows, checks each against the vault filesystem, and:
- Updates paths for files that were **moved** (found by scanning for matching fqc_id in frontmatter)
- Marks as **archived** any rows for files that are truly gone (not found anywhere in the vault)

Report the results clearly:

> "Reconciliation complete — 142 documents checked:
> - Moved (paths updated): 2
>   - `clients/old/acme.md` → `clients/acme/notes.md`
>   - `research/draft.md` → `research/active/draft.md`
> - Archived (missing — no longer in vault): 1
>   - `projects/cancelled/brief.md`"

If nothing needed fixing:
> "Reconciliation complete — 142 documents checked. Everything is in sync. No changes needed."

### Dry-run mode

If the user runs `/reconcile dry-run` (or says "preview the reconciliation" or "show me what reconcile would do"), call:

```
reconcile_documents(dry_run: true)
```

Report the same results prefixed with `[DRY RUN]` and make clear that no changes were made. Offer to run the real reconcile if the preview looks right.

## Key distinction: /reconcile vs /vault-scan

| | /vault-scan | /reconcile |
|---|---|---|
| **Direction** | Filesystem → Database | Database → Filesystem |
| **Discovers** | New files not yet in DB | DB rows with missing/moved vault files |
| **Missing status** | Marks as `missing` (soft, potentially temporary) | Promotes to `archived` (permanent — file truly gone) |
| **Move detection** | Hash-based during filesystem walk | fqc_id frontmatter scan per missing row |
| **Use when** | You added files to the vault | You moved/deleted files from the vault |

If the user is unsure which to run, suggest `/vault-health` — it runs both in sequence with a full status report.

## Performance note

`reconcile_documents` is an expensive operation — it scans the entire vault to build an fqc_id → path index. Let the user know it may take a moment on large vaults.

## Error handling

- If `reconcile_documents` returns an error, report the message. Common causes: database connectivity, vault path misconfiguration.
- The operation is idempotent — safe to run multiple times.
- Files that couldn't be read during the vault index build are silently skipped — if a moved file is unreadable, it may be incorrectly marked as archived. Mention this caveat if the user reports unexpected archiving.
