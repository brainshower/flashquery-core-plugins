---
name: organize
description: >
  Use this skill when the user wants to clean up, reorganize, or do a
  thorough pass over their Product Brain vault. Trigger on "organize the
  vault", "clean up the brain", "things are getting messy", "sort through
  what's accumulated", "review everything", "do a cleanup pass", "triage
  the backlog", "reorganize", or any request for a deliberate, thorough
  review of vault contents beyond what the daily Review Loop handles. Also
  trigger when the user wants to migrate existing notes into the Product
  Brain from another system, onboard a collection of documents, or do a
  "spring cleaning" pass. Even casual mentions like "it's getting cluttered"
  or "I should organize this" in a Product Brain context should trigger
  this skill. This is the large-scale counterpart to the Review Loop —
  for backlogs, messy imports, and periodic housekeeping.
---

# Organize

A periodic, guided pass over vault contents to route misplaced items, consolidate related material, archive stale content, and restore structure when things have gotten messy. This is the larger-scale counterpart to the Review Loop — where the loop handles routine daily intake, Organize handles the backlog.

## When to use

- The inbox has grown faster than the Review Loop has processed it
- Files were dragged into the vault haphazardly from Finder or another tool
- It's time for a deliberate periodic review of the whole vault
- The user is migrating documents from an external system (old notes, another tool, scattered folders)
- Something just feels disorganized and needs attention

## Multi-session design

A thorough Organize pass is not a single-sitting exercise. The skill is designed to work across multiple sessions with a "pick up where we left off" capability. At the end of each session, summarize what was done and what remains. At the start of a resumed session, present that summary so the user can continue without re-scanning everything.

## Three-phase workflow

### Phase 1 — Discovery

Scan before asking anything. Build a full inventory and do initial rough classification so you have the complete picture before making any routing decisions.

#### Steps

1. Read the tag vocabulary via `get_document` (`{vault_root}/_plugin/tags.md`). You'll need this for re-tagging during Phase 3.

2. Call `list_files` recursively to inventory all documents across the vault — all project folders, the inbox, and any unexpected locations.

3. Call `get_doc_outline` in array mode to batch-inspect structure. For each document, note:
   - Apparent document type (from frontmatter or section structure)
   - Which project folder it's in (and whether that matches its apparent type)
   - Rough age (from file metadata)
   - Any obvious duplicates or near-duplicates

4. Call `search_records` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"documents"`
   - to get the full database picture (type, status, project assignment)

5. Call `search_records` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"projects"`
   - to get all active and archived projects

6. Call `reconcile_documents` to identify orphaned database records where vault files no longer exist.

7. Call `search_records` on `templates` to confirm which templates are available for reclassification.

At the end of Discovery, you should have a complete picture: every document, where it is, what type it appears to be, whether the database agrees, and any anomalies.

### Phase 2 — Draft classification

Rather than asking "what is this?" for each document, present your best guess and let the user react. Corrections are faster than answers from scratch.

#### Principles

- **Obvious cases get handled silently.** A spark in the inbox that clearly belongs there doesn't need a question.
- **Ambiguous cases get surfaced.** A document in `research/` that looks like a work item, or a spark that's been in the inbox for weeks.
- **Cryptic notes get context.** Things written quickly when the context was obvious and now unclear — surface with whatever context you can infer: "This looks like it was written around the time you were working on X — does that ring a bell?"

Present draft classifications in groups:

```
These 4 sparks in the inbox look ready to route:
- "Scanner hidden files" → promote to work item in work/
- "Competitor pricing research" → promote to research note in research/
- "Docker health check trick" → merge into research note "Container Setup"
- "API versioning question" → promote to research note in research/

These look fine where they are (no action needed):
- [list of correctly placed documents]

These need your input:
- "old-notes-v2.md" in the vault root — I can't tell what this is. Written around March, maybe related to the scanner work?
```

### Phase 3 — Batched decisions

Group similar decisions to avoid death by a thousand questions.

#### Grouping patterns

- **"These N items all look like scratch notes that predate any clear project structure — archive them all, or review individually?"** One decision instead of many.
- **"These 3 sparks are all about the same topic — merge them into a single research note?"** Consolidation.
- **"These work items were all shipped in the last milestone — archive them together?"** Bulk status change.

#### Execution for each decision

**Reclassify to a different folder:**
1. Move via `move_document` to the correct location
2. Update `prodbrain_documents` via `update_record` with corrected `document_type` and `status`
3. Correct frontmatter via `update_doc_header`
4. Re-tag via `apply_tags` if the new type calls for different tags

**Archive stale content:**
1. Archive the vault document via `archive_document`
2. Archive the database record via `archive_record`

**Consolidate related material:**
1. Identify the target document (usually the most developed one)
2. Append content from source documents via `append_to_doc`
3. Write provenance records for each source via `create_record` on `provenance`
4. Add wikilinks via `insert_doc_link`
5. Archive the consolidated source documents

**Surface an implicit decision:**
Going through old notes often reveals decisions that were made implicitly and never recorded. When you notice one: "This document implies a decision was made about X — want to capture that?" If yes, create a new document (typically a research note with status `resolved` or a spark tagged `#decision`) via Capture's flow.

**Identify new connections:**
When documents that were captured separately clearly relate to the same thread, present the connection to the user. If confirmed, write provenance via `create_record` on `provenance`.

The default resolution for anything unclear is **archive, not delete**. Nothing gets lost.

After a pass completes, offer the natural next step: "Want me to Brief you on the newly organized material?" The Brief skill can synthesize what was just reorganized into a coherent summary — useful for confirming that the cleanup achieved what was intended.

## Migration mode

At the extreme end, Organize handles onboarding a large collection of existing documents from scattered folders, old note apps, or a previous tool. This is the same workflow at larger scale with more hand-holding:

1. Have the user place (or point to) the documents in the vault
2. Run `force_file_scan` to discover them
3. Proceed through the three phases, expecting a higher proportion of ambiguous items
4. Be patient with cryptic notes — the user may need to think about context that's been dormant for months

Migration is expected to take multiple sessions. Progress tracking is essential.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- Organize does not write to `prodbrain_projects` or `prodbrain_review_state` — it works within the existing project structure.
- The outline-first scanning pattern (`list_files` → `get_doc_outline` → targeted `get_document`) is essential for keeping token usage manageable when processing many documents.
- When in doubt about a document, surface it to the user rather than making an assumption. The cost of asking is low; the cost of misrouting is time spent un-doing it later.
