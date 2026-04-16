# Vault Maintenance Workflow

Use this workflow for operational hygiene on the vault: reconciling the database after bulk file moves outside the chat, emptying folders, duplicating docs as starting points, moving or renaming with identity preserved, and re-indexing when the scanner falls behind.

These tools all preserve data in one way or another — moves keep the fqc_id, copies keep the source untouched, reconciliation marks missing files archived rather than deleting, and `remove_directory` refuses to clear anything non-empty. The skill's job is to choose the right tool for the user's intent and relay the critical warnings the tools emit.

## When to use

- "I moved a bunch of files in Finder — can you resync the database?"
- "Rename `inbox/acme-notes.md` to `clients/acme/notes.md`"
- "Make a copy of this proposal for the Beta client"
- "Delete the empty `archive/2024-old-projects` folder"
- "I just added files outside the chat — can the system see them?"

## When NOT to use

- Bulk tag changes → [Bulk Tagging](bulk-tagging.md)
- Archive sweeps based on search criteria → [Archive Sweep](archive-sweep.md)
- Single-document body edits → fqc-writer workflows
- Creating a brand-new document → fqc-writer's document-creation workflow

---

## Tool overview

| Tool | Purpose | Preserves fqc_id? |
|------|---------|-------------------|
| `move_document` | Rename/relocate a document | Yes — identity preserved |
| `copy_document` | Duplicate a document as a starting point | No — copy gets a new fqc_id |
| `remove_directory` | Safely remove an **empty** directory | n/a |
| `reconcile_documents` | Resync the DB against the vault after external file changes | Yes — detects moves via fqc_id |
| `force_file_scan` | Manually trigger the file scanner | n/a |

---

## `move_document` — rename or relocate while preserving identity

Use to rename a document, move it to a new directory, or both — without changing its `fqc_id`, history, or plugin associations. Intermediate directories are created automatically.

```
move_document(
  identifier: "inbox/note.md",              // required
  destination: "clients/acme/notes.md"      // required — vault-relative path, including filename
)
```

### Key behaviors to relay to the user

- **Identity is preserved.** fqc_id, creation date, tags, and all custom frontmatter carry over.
- **Wikilinks in other documents are NOT auto-updated.** If another file has `[[Old Title]]` pointing at the moved document, that link will still resolve by title in most setups but may break if you renamed the title. The tool's response includes a reminder — surface it to the user so they know whether to do a find-and-replace sweep.
- **Plugin-owned documents produce a warning.** If the moved document is owned by a plugin (e.g., a CRM contact doc), the plugin may be hard-wired to look at the old path. The response includes a warning — pass it along so the user can update the plugin's reference.
- **Missing extension is filled in.** If `destination` doesn't include a file extension, the source's extension is used (`"projects/q2/brief"` → `"projects/q2/brief.md"`).

### Examples

**Rename in the same folder:**
```
move_document(
  identifier: "inbox/note.md",
  destination: "inbox/meeting-notes.md"
)
```

**Move from inbox into a client folder:**
```
move_document(
  identifier: "inbox/acme-notes.md",
  destination: "clients/acme/notes.md"
)
```

**Move into a folder that doesn't exist yet (auto-created):**
```
move_document(
  identifier: "inbox/q2-kickoff.md",
  destination: "projects/q2/kickoff.md"
)
```

**Extension inferred from source:**
```
move_document(
  identifier: "inbox/rough-draft",
  destination: "projects/q2/brief"     // → "projects/q2/brief.md"
)
```

---

## `copy_document` — duplicate as a starting point

Use when the user wants to treat an existing document as a template — e.g., "copy the proposal template for the Acme deal." The source is not modified. The copy gets a **new fqc_id**, fresh `created` timestamp, and its own status lifecycle.

```
copy_document(
  identifier: "templates/proposal.md",          // required
  destination: "clients/acme/proposal.md"       // optional — defaults to vault root
)
```

### Key behaviors to relay to the user

- **Metadata is copied immutably.** Title, tags, and all custom frontmatter fields (e.g., `client`, `priority`) are copied as-is from the source. There is no way to customize the copy's metadata at creation time.
- **To change title, tags, or custom fields on the copy,** call `update_doc_header` (for frontmatter) or `update_document` (for body + title) **after** copying. Set that expectation with the user up front — they usually want a modified copy, not a carbon copy.
- **Destination defaults to vault root.** Omitting `destination` lands the copy at the vault root, with the filename derived from the source title.

### Examples

**Copy a proposal template into a client folder:**
```
copy_document(
  identifier: "templates/proposal.md",
  destination: "clients/acme/proposal.md"
)
```

**Copy without a destination — lands at vault root:**
```
copy_document(identifier: "templates/contact.md")
```

**Copy then customize the copy's title/tags:**
```
copy_document(identifier: "templates/proposal.md", destination: "clients/beta/proposal.md")
// then:
update_doc_header(identifier: "clients/beta/proposal.md", updates: { client: "Beta", title: "Beta Proposal" })
```

---

## `remove_directory` — delete an empty directory

Safely removes an empty directory. No recursion, no force. If the directory contains any files or subfolders, the tool errors and lists the contents.

```
remove_directory(path: "archive/2024-old-projects")
```

### Behavior to relay

- **Empty-only.** If the directory isn't empty, the error response shows what's in it — present that to the user and ask whether they want to move/archive the contents first. Don't loop in attempts to force-delete; that isn't supported.
- **Path is vault-relative**, same convention as every other vault path.

---

## `reconcile_documents` — resync DB after external vault changes

Scans the database for documents whose vault file is missing on disk. When a document's `fqc_id` turns up at a different path (because the user moved files in Finder, git, etc.), the DB is updated to the new path. Files that remain permanently missing are marked as archived.

```
reconcile_documents(dry_run: true)    // preview first — always recommended
reconcile_documents()                 // then apply
```

### When to run

- The user moved/renamed files outside the chat and wants the system to catch up.
- Semantic search starts returning stale paths or "file not found" errors on docs that clearly still exist.
- After a git pull that rearranged the vault.

### Recommended pattern

Always recommend `dry_run: true` first. Present the proposed changes (moves detected, files about to be marked archived) and confirm before running without `dry_run`.

### Pair with `force_file_scan`

Reconciliation focuses on DB-side cleanup. If new files were added outside the chat (not just moved), run `force_file_scan` first so the scanner picks them up, then run `reconcile_documents` to resolve any moves the scanner flagged.

```
force_file_scan()
reconcile_documents(dry_run: true)
// review, then:
reconcile_documents()
```

---

## `force_file_scan` — manually trigger the scanner

Re-indexes the vault. Useful when the user added files outside the chat and wants them visible immediately, or as a recovery step before reconciliation.

```
force_file_scan()                      // synchronous; waits for the scan to complete
force_file_scan(background: true)      // fire-and-forget; returns immediately
```

### Response format

- **`background: false`** (default, synchronous): returns JSON
  ```json
  {
    "status": "complete",
    "new_files": N,
    "updated_files": N,
    "moved_files": N,
    "deleted_files": N,
    "status_mismatches": N
  }
  ```
  Note: `updated_files` corresponds to hash mismatches — files whose content changed since the last scan.

- **`background: true`**: returns immediately with
  ```json
  { "status": "started", "message": "..." }
  ```
  Results are only visible in server logs after that. Use when the user doesn't need the summary inline (e.g., they just want the scanner to catch up while they keep working).

Pick synchronous when the user is about to do a search or browse that depends on the scan; background when the user is mid-conversation and the scan is a behind-the-scenes nicety.

---

## Confirm-before-executing

Most of these operations are reversible in principle but annoying in practice. Before running anything that moves, copies, removes, or reconciles in bulk, show the user what's about to happen:

- For `move_document` / `copy_document` — name the source and destination, and mention any warnings the tool will emit (wikilinks, plugin ownership).
- For `reconcile_documents` — run `dry_run: true` first and show the proposed changes.
- For `remove_directory` — confirm the directory is empty and name the path.

## Error handling

- **Write lock timeout** — retry once after 3 seconds; if persistent, pause and tell the user something else is writing to the vault.
- **Destination already exists** (move/copy) — the tool errors rather than clobbering. Ask the user whether to pick a new name, archive the existing file first, or abort.
- **`remove_directory` on a non-empty directory** — surface the listed contents and ask the user whether to move/archive them first.
- **`reconcile_documents` reports permanently missing files** — explain that those will be marked archived on the next non-dry-run pass, and give the user the option to restore files from backup first if any of them were deleted accidentally.
