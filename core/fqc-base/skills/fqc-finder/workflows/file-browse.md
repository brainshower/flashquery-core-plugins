# File Browse Workflow

Use this workflow when the user wants to browse vault files and folders by path — the "what's in this folder" or "what changed recently" type of question. It's the natural complement to `search_documents`: filesystem-shaped navigation rather than content-shaped discovery.

## When to use

- "What's in the clients folder?"
- "Show me what's in `clients/acme`"
- "What's changed in the last week?"
- "What did I add to `inbox` yesterday?"
- Inventorying a subtree by date window rather than by topic
- Sanity-checking that a newly saved file is actually present

## When NOT to use

- Content-based discovery ("find notes about X") → [Document Search](document-search.md)
- Reading the structure of a specific file (headings, links) → `get_doc_outline`
- Cross-type search spanning documents + memories → [Unified Search](unified-search.md)
- Browsing plugin records → out of scope for fqc-base; use the plugin's own skill

## Tool: `list_files`

```
list_files(
  path: "clients/acme",   // required — vault-relative directory
  recursive: true,         // optional; default false — walk the entire subtree
  extension: ".md",        // optional — case-insensitive; see caveat below
  date_from: "7d",         // optional — modified ≥ this; relative ("7d", "24h", "1w") or ISO
  date_to: "2026-04-15"    // optional — modified ≤ this; relative or ISO
)
```

### Parameters in detail

- **`path`** (string, required) — vault-relative directory. Examples: `"clients/acme"`, `"inbox"`, `"projects/q2"`.
- **`recursive`** (boolean, optional, default `false`) — when `true`, walks the entire subtree under `path`. Leave off for a flat listing of just the immediate children.
- **`extension`** (string, optional) — case-insensitive filter applied to the result set (e.g., `".md"`). **Caveat worth knowing:** the underlying file enumeration only scans markdown files, so the `extension` filter runs against a `.md`-only result set. Passing `".png"`, `".pdf"`, or any non-`.md` extension returns empty. Only `".md"` is useful here in the current implementation — don't suggest otherwise to users.
- **`date_from`** (string, optional) — include files modified on or after this moment. Accepts relative formats (`"7d"`, `"24h"`, `"1w"`) or ISO (`"2026-04-01"`, `"2026-04-01T15:30:00Z"`).
- **`date_to`** (string, optional) — include files modified on or before this moment. Both relative and ISO formats work for `date_to` as well, even though the schema description mentions only ISO — both parameters share the same parser.

### Response note

Each file entry currently reports `Size: 0 bytes` — that field isn't wired up yet in the implementation. Don't cite sizes to the user; use `date_from` / `date_to` for any recency-based reasoning instead.

## Examples

**"What's in the Acme folder?"**
```
list_files(path: "clients/acme")
```

**"Show me everything under clients/acme, all subfolders included"**
```
list_files(path: "clients/acme", recursive: true)
```

**"What did I add to the inbox in the last week?"**
```
list_files(path: "inbox", date_from: "7d")
```

**"What changed in projects/q2 between April 1 and April 15?"**
```
list_files(path: "projects/q2", date_from: "2026-04-01", date_to: "2026-04-15")
```

## When results look suspiciously empty

If the folder should contain files the user just added outside the chat, the scanner may not have picked them up yet. Run `force_file_scan()` to reindex, then retry `list_files`. Pass `background: true` if the user doesn't need to see the scan summary inline — results appear in server logs.

```
force_file_scan()          // synchronous; returns { status: "complete", new_files, updated_files, moved_files, deleted_files, status_mismatches }
force_file_scan(background: true)   // fire-and-forget; returns immediately
```

See [vault-maintenance](../../fqc-organizer/workflows/vault-maintenance.md) in fqc-organizer for the fuller picture of when scanning fits into a session.

## Synthesis guidance

`list_files` returns a filesystem view. When presenting results:

1. **Group by subfolder** if `recursive: true` returned a wide tree — readable summaries beat flat lists once there are more than ~15 files.
2. **Lead with dates** if the user asked a recency question — put the `last_modified` up front.
3. **Offer a drill-in.** After showing what's in a folder, a natural next step is "want me to read any of these?" — answer via `get_document` or `get_doc_outline`.
