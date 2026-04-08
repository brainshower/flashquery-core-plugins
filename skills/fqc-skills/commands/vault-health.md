---
name: vault-health
description: Run a full FlashQuery Core vault health check — scan, reconcile, and surface hygiene issues in a single comprehensive report. This is a slash command (/vault-health) for periodic maintenance or when the user wants a complete status picture of their vault. Trigger on "/vault-health" or when the user says "check my vault health," "run a full vault check," "how healthy is my vault," "vault status," "do a full maintenance check," or "something feels off with FQC."
command: /vault-health
---

# /vault-health

Runs a complete vault health check in three stages: scan, reconcile, and hygiene audit. Use this for periodic maintenance or when the user wants a comprehensive picture of their vault's state without having to run multiple commands.

## When the user runs this

- Periodic maintenance (weekly/monthly check-in)
- Something feels off and they want a comprehensive diagnosis
- After a large vault reorganization to confirm everything settled correctly
- First-time setup verification

## Workflow

Run the three stages in sequence. Report after each stage completes.

---

### Stage 1: Vault Scan

```
force_file_scan(background: false)
```

This syncs the vault filesystem into the database: discovers new files, detects moved files, marks missing files.

Report the counts before proceeding to stage 2.

---

### Stage 2: Reconciliation

```
reconcile_documents(dry_run: false)
```

This walks database rows and verifies each file still exists in the vault — resolving any `missing` rows either by locating the file at a new path or archiving it as truly gone.

Report the counts: moved paths updated, files archived.

---

### Stage 3: Hygiene Audit

```
search_documents(mode: "filesystem")
```

Scan all active documents for hygiene issues. Look for:

1. **Untagged documents** — documents with no tags beyond `#status/active` (i.e., no categorization tags like `#type/*`, `#client/*`, or `#project/*`). These are hard to find later.

2. **Stale drafts** — documents tagged `#status/draft`. If there are many, surface them for the user's awareness (they may have forgotten about old drafts).

3. **Any other patterns** that look like they need attention based on the vault contents.

Note: The `search_documents` call with no filters returns the 20 most recently modified documents in filesystem mode. For a broader hygiene check on large vaults, consider running additional `search_documents` calls with specific tag filters (e.g., `tags: ["#status/draft"]`).

---

### Stage 4: Summary Report

Present a clean summary:

```
## Vault Health Report

**Scan results:**
- New files indexed: {n}
- Moved (paths updated): {n}
- Missing/deleted: {n}
- External edits detected: {n}

**Reconciliation:**
- Files reconciled: {total}
- Paths fixed: {n}
- Archived (permanently missing): {n}

**Hygiene:**
- Total active documents: {n}
- Untagged documents: {n} [list titles if ≤ 5, otherwise note "run /find untagged for full list"]
- Stale drafts: {n} [list titles if ≤ 5]

**Status:** [Clean ✓ / Issues found — see above]
```

If everything looks good, say so clearly. If issues were found, be specific about what needs attention and offer to help address it (e.g., "Want me to help tag those untagged documents?" or "I can archive those old drafts if you'd like.").

---

## Error handling

If any stage fails:
- Report the error with its message
- Continue to the next stage (partial results are still useful)
- Note in the summary which stages completed and which failed

## Performance note

`/vault-health` runs two expensive operations (`force_file_scan` + `reconcile_documents`) back to back. Let the user know it may take a moment on large vaults.
