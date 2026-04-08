---
name: fqc-organizer
description: Run bulk organization operations on vault documents and memories — tagging sets of documents, archiving old content, or cleaning up memories at scale. Use this skill whenever the user wants to organize, clean up, bulk tag, or do sweeping operations across multiple documents or memories. Trigger on phrases like "clean up," "organize," "archive old documents," "what's out of date," "bulk tag," "tag everything in this project as," "archive anything older than," "tag all the X as Y," "mark all my Y docs as," "clean up old memories about," or "organize my research docs." Even phrasing like "get things in order" or "tidy up my vault" should trigger fqc-organizer. Does NOT own vault scanning or reconciliation — those are handled by the /vault-scan and /reconcile commands.
---

# fqc-organizer

This skill handles bulk organization operations that require the AI to interpret intent, find the right set of documents or memories, and confirm actions with the user before executing them at scale.

## What this skill owns

- Bulk tagging of documents matching search criteria
- Archive sweeps (find candidates → confirm → archive)
- Bulk memory cleanup (find old/outdated memories → confirm → archive)

## What this skill does NOT own

- Vault scanning or reconciliation → handled by `/vault-scan` and `/reconcile` commands
- Single-document tag changes → handled by fqc-writer
- Search and retrieval → handled by fqc-finder

## Core principle: confirm before bulk-mutating

Bulk operations can affect many documents at once and are not easily undone. Always show the user the candidate set before executing. The workflow is:

**Search → Show candidates → Confirm → Execute**

Never skip the confirmation step for operations affecting more than one item, unless the user explicitly says "just do it without asking."

---

## Routing heuristic

| User intent | Workflow |
|-------------|----------|
| Tag a set of documents matching criteria | → [Bulk Tagging](workflows/bulk-tagging.md) |
| Archive documents matching criteria | → [Archive Sweep](workflows/archive-sweep.md) |
| Clean up / archive old memories | → [Memory Cleanup](workflows/memory-cleanup.md) |

---

## Error handling

- **Write lock timeout** — retry once after 3 seconds; if persistent, pause the bulk operation and tell the user.
- **Individual item errors** — `apply_tags` and `archive_document` process arrays and report errors per item without aborting the batch. After execution, report any items that failed alongside the successes.
- **No results from search** — if the candidate search returns nothing, tell the user and ask if they'd like to broaden the criteria.
