---
name: fqc-organizer
description: Run bulk organization and vault maintenance operations — tagging sets of documents, archiving old content, cleaning up memories at scale, and operational hygiene like moving/copying documents, removing empty folders, reconciling the database against the filesystem, and forcing file scans. Use this skill whenever the user wants to organize, clean up, bulk tag, or do sweeping operations across multiple documents or memories. Also trigger when the user wants to move or rename a document, copy a doc as a template/starting point, delete an empty folder, resync the database after external file changes, or force the vault scanner to catch up. Trigger on phrases like "clean up," "organize," "archive old documents," "what's out of date," "bulk tag," "tag everything in this project as," "archive anything older than," "tag all the X as Y," "mark all my Y docs as," "clean up old memories about," "organize my research docs," "move this file to," "rename this document," "copy this proposal for," "delete this empty folder," "resync the database," or "the system can't see the files I just added." Even phrasing like "get things in order" or "tidy up my vault" should trigger fqc-organizer.
---

# fqc-organizer

This skill handles bulk organization operations that require the AI to interpret intent, find the right set of documents or memories, and confirm actions with the user before executing at scale.

## What this skill owns

- Bulk tagging of documents matching search criteria
- Archive sweeps (find candidates → confirm → archive)
- Bulk memory cleanup (find old/outdated memories → confirm → archive)
- Vault maintenance: moving/renaming documents, copying docs as starting points, removing empty directories, reconciling the database against the filesystem, and forcing file scans

Tool surface in addition to `search_documents`, `apply_tags`, `archive_document`, `list_memories`, and `archive_memory`: `move_document`, `copy_document`, `remove_directory`, `reconcile_documents`, `force_file_scan`.

## What this skill does NOT own

- The `/fqc-base:vault-scan`, `/fqc-base:reconcile`, and `/fqc-base:vault-health` slash commands — those are scripted, non-interactive runs of the same underlying tools. The skill covers the interactive, conversational flows (e.g., "I moved some files around — can you resync?").
- Single-document tag changes → handled by fqc-writer.
- Search and retrieval → handled by fqc-finder.
- Section-scoped document edits → handled by fqc-writer's section-editing workflow.

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
| Move, rename, copy, or delete-folder operations; resync DB; force scan | → [Vault Maintenance](workflows/vault-maintenance.md) |

---

## Error handling

- **Write lock timeout** — retry once after 3 seconds; if persistent, pause and tell the user.
- **Individual item errors** — `apply_tags` and `archive_document` process arrays and report errors per item without aborting the batch. Report any failures alongside successes after execution.
- **No results from search** — tell the user and ask if they'd like to broaden the criteria.
