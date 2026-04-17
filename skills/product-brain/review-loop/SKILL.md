---
name: review-loop
description: >
  Use this skill when the user wants to process what's accumulated in the
  Product Brain inbox, review recent captures, or run a periodic review
  cycle. Trigger on "review the inbox", "run the review loop", "process
  what's accumulated", "what's new in the brain", "review recent captures",
  "route the inbox", "let's review", or any request to process, triage, or
  review recently captured Product Brain content. Also trigger when Orient
  or Capture suggests running the Review Loop, or when the user asks
  "what should I look at" in a Product Brain context. Even casual mentions
  like "anything need attention?" or "what's piled up?" should trigger this
  skill. This is the metabolic process that turns raw capture into organized
  knowledge over time.
---

# Review Loop

The background processing skill that keeps the vault from becoming a dumping ground. It does several things in one pass: routes inbox items to the right destination, performs cursory research on inbound links and sparks, scans research notes for open questions, and surfaces connections between recently captured documents.

The output is a brief — what was routed, what was found, what questions need a decision. The brief is intentionally short: highlights and directional cues, not articles to read. The user should be able to scan it and decide where to steer.

## What it does in one pass

1. **Routes inbox sparks** — decides whether each spark should merge into an existing document or become a new standalone document (research note, work item, or feature spec)
2. **Performs cursory research** — for sparks that include URLs or topics worth exploring, does a lightweight research pass and appends findings to the relevant document
3. **Checks open questions** — scans research notes with `has_open_questions=true` and looks for possible answers or new directions
4. **Surfaces connections** — finds links between recently captured documents and flags them for the user

## Steps

### 1. Initialize the run

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

Retrieve the vault root, active project, and folder paths.

Check for external file additions by calling `force_file_scan`. This triggers `on_document_discovered` for any files added to the vault outside a skill invocation, ensuring `prodbrain_documents` is up to date before processing.

### 2. Determine what to process

Call `get_record` or `search_records` on the `review_state` table:
- `plugin_id`: `"product-brain"`
- `table`: `"review_state"`

to find the `last_run_at` and `last_processed_at` timestamps. If no record exists (first run), process everything.

Call `list_files` with the inbox path and a date filter (default: past 12 hours, or since `last_processed_at` if it's more recent) to find candidate documents.

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: `{ "status": "active" }`

filtered to documents updated since `last_processed_at`. Look for:
- Inbox sparks to route (`document_type: "spark"` in the inbox path)
- Research notes with open questions (`has_open_questions: true`)
- Recently created items that might connect to each other

### 3. Batch-inspect structure

Use the outline-first pattern to understand the documents without reading their full content:

Call `get_doc_outline` for each candidate document (use array mode if available to batch-inspect). This gives you the section structure, frontmatter, and linked documents — enough to decide what each document is about and whether it needs full reading.

### 4. Route inbox items

For each spark in the inbox, make a routing decision. Read the spark's content via `get_document` if the outline alone isn't enough to decide.

**Route to an existing research note** — when the spark's content clearly contributes to an existing research topic:

a. Identify the target research note via `search_records` or `search_all`.

b. Append the spark's content to the research note via `append_to_doc` — add it to the Findings section with a note about when and where it came from.

c. If the spark answers an open question, update the Open Questions section via `replace_doc_section` — move the answered question to Findings with the answer.

d. Write provenance (dual-write):
   - Call `create_record` on `provenance` with `source_fqc_id` = spark, `derived_fqc_id` = research note
   - Call `insert_doc_link` to add `[[spark title]]` to the research note's Sources section

e. Update the spark's status: call `update_record` on `documents` to set `status: "archived"`, then call `archive_record` to archive the spark record.

**Promote to a new document** — when the spark deserves its own document:

a. Determine the appropriate type (research note for exploratory topics, work item for tasks/bugs, feature spec only if the user's intent was that clear).

b. Look up the relevant template from `prodbrain_templates`.

c. Create the new document via `create_document` in the appropriate folder (`research/`, `work/`, or `specs/`).

d. Register in `prodbrain_documents` via `create_record`.

e. Write provenance if the new document was seeded from the spark: `create_record` on `provenance`.

f. Read the tag vocabulary via `get_document` (`_plugin/tags.md`). Apply appropriate tags via `apply_tags`.

g. Archive the original spark (same as step e above for routing).

**Leave in inbox** — when you're genuinely uncertain about where the spark belongs. Don't force a routing decision — leave it and surface it in the brief for the user to decide. These should be rare.

### 5. Cursory research

For sparks or research notes that contain URLs or reference topics worth exploring, do a lightweight research pass. The goal is a few findings and a direction, not a comprehensive report.

Append research findings to the relevant document via `append_to_doc`. If the findings suggest new open questions, add them to the Open Questions section via `replace_doc_section` (for research notes) or note them in the document body (for other types).

### 6. Check open questions

Process research notes where `has_open_questions` is true:

a. Read the Open Questions section via `get_document` with `sections: ["Open Questions"]`.

b. For each open question, check whether recent captures, vault content, or cursory web research provides a useful direction. Don't try to fully answer every question — a useful direction or a relevant finding is sufficient.

c. If progress is found, append findings to the Findings section and update Open Questions accordingly.

d. If all open questions are resolved, update `prodbrain_documents` via `update_record` to set `has_open_questions: false`.

### 7. Surface connections

Look for relationships between recently captured documents:

Call `search_all` with queries derived from the key topics of recent captures. Check for semantic overlap between documents that were captured separately but relate to the same thread.

Note connections in the brief output — don't write links automatically. Present them to the user: "The spark about X seems related to the research note on Y — want me to link them?"

### 8. Write the output brief

The Review Loop produces a pinned vault document (created once, updated each run):

If no brief document exists yet, create it via `create_document` with:
- `title`: `Review Loop Brief`
- `path`: the project root (e.g., `product-brain/flashquery/`)

If it already exists, update it via `replace_doc_section`.

The brief should contain:
- **What was routed** — which sparks were merged into existing docs or promoted to new docs, and where
- **What was found** — research findings, answered questions, new directions
- **What needs a decision** — items left in the inbox that need the user's input, connections that could be linked, ambiguous routing decisions
- **Open threads** — research notes with active open questions, flagged items

Keep it scannable. This is a summary the user can react to, not a document to study.

### 9. Update review state

Call `update_record` (or `create_record` on first run) with:
- `plugin_id`: `"product-brain"`
- `table`: `"review_state"`
- `fields`:
  ```json
  {
    "project_id": "<active project id or null for all-project>",
    "last_run_at": "<current ISO timestamp>",
    "last_processed_at": "<timestamp of the most recently processed document>"
  }
  ```

### 10. Present and offer next steps

Show the user the brief — either inline in the conversation or by referencing the vault document.

Natural follow-ups:
- If connections were flagged → "Want me to link any of these?"
- If research notes have rich findings → "Want me to draft a spec from the research on X?" (→ Draft)
- If a research note's open questions suggest web research → offer to research a specific question

One offer at a time.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- The Review Loop can be run at any frequency. A reasonable default is to review everything captured in the past 12 hours, but the user can ask for a different window ("review everything from this week").
- The brief is intentionally short. If the user wants more detail on any item, they can ask — or use Retrieve / Brief.
- When routing sparks, lean toward merging into existing documents when there's a clear connection. Proliferating standalone documents when they should be part of an existing thread makes the vault harder to navigate.
- Cursory research is a best-effort pass, not a thorough investigation. The goal is "here's what I found in 30 seconds" — enough to inform direction, not to produce a complete answer.
