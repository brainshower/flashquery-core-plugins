---
name: orient
description: >
  Use this skill when the user wants to start their day, get oriented,
  see what's going on in the Product Brain, or get a quick status overview.
  Trigger on "orient me", "what's going on", "morning brief", "where did
  I leave off", "start my day", "give me a rundown", "what should I focus
  on", "what's in the inbox", "what's the state of things", or any request
  for a starting-point overview of product work. Also trigger when the user
  starts a new session and seems to need context on where things stand.
  Even casual openers like "what's up" or "catch me up" in a Product Brain
  context should trigger this skill. This is a read-only skill — it
  synthesizes existing content into a brief, it doesn't create or modify
  anything.
---

# Orient

The daily starting point. Surfaces a brief covering where things left off, what's sitting in the inbox, and what open items deserve attention — enough to get oriented in under two minutes without reading through notes manually.

## What it produces

An Orient brief is a few short sections, each a sentence or two. Not a status report — a starting point. The goal is to replace the experience of opening a notes file and trying to reconstruct context from scratch.

The brief should cover:

**Where you left off** — what the last daily log said about today's plan (the "Tomorrow" section from yesterday's Close). If no daily log exists, summarize the most recently modified documents to approximate continuity.

**Inbox status** — how many items are sitting in the inbox, and a one-line description of any that stand out (e.g., "3 sparks in the inbox, including one about competitor pricing that's been there 4 days").

**Open threads** — active research notes with open questions, feature specs in progress, work items that are unblocked. Focus on what's actionable, not everything that exists.

**Flagged items** — anything tagged `#priority` or `#blocked`, and anything that's been sitting untouched long enough to warrant a nudge.

Keep the whole brief scannable. If the user wants to dig into any section, they'll ask — don't front-load detail they haven't requested.

## Steps

### 1. Retrieve configuration and projects

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

This returns the vault root and plugin configuration.

Also call `search_memory` with:
- `query`: `"orient preferences"`
- `tags`: `["product-brain-config"]`

to check if the user has stated any Orient preferences (e.g., "lead with open research notes" or "skip the inbox count").

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `filters`: `{ "status": "active" }`

This returns all active projects with their names and paths. Use this to scope the rest of the brief. If the user specified a project ("orient me on Client Portal"), focus on that one. If memory contains an active-project preference, default to that project. Otherwise, brief across all active projects.

### 2. Read the most recent daily log

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: `{ "document_type": "daily_log", "status": "active" }`
- `limit`: 1

If a recent daily log is found, read its "Tomorrow" section via `get_document` with:
- `identifier`: the `fqc_id`
- `sections`: `["Tomorrow"]`

This is the "where you left off" anchor for the brief.

### 3. Check the inbox

Call `list_files` with:
- the inbox path for the active project (e.g., `product-brain/flashquery/inbox/`)

Count the items and note any that have been sitting longer than a day or two.

### 4. Find open threads

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: `{ "status": "active", "has_open_questions": true }`
- `limit`: 10

This finds research notes with unresolved open questions — the most actionable items.

Also query for recently updated active documents:
- `filters`: `{ "status": "active" }`
- sorted by `updated_at` descending, `limit`: 5

### 5. Check for flagged items

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `query`: `"priority blocked"`
- `limit`: 10

Look for documents tagged `#priority` or `#blocked`.

### 6. Read the last Review Loop brief

Call `get_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"review_state"`
- `id`: the review state record for the active project (or the global record)

If a recent Review Loop has run, note when it last ran and whether it surfaced anything the user hasn't seen yet.

### 7. Optionally get a tagged summary

If the brief benefits from a broader view, call `get_briefing` with:
- `tags`: relevant tags like `["#priority", "#needs-review"]`

This provides a summary view across tagged documents and memories.

### 8. Compose and present the brief

Synthesize all the above into a concise brief. Structure it naturally — not as a rigid template, but as a few short paragraphs or groups that answer "where am I and what should I focus on?"

If the inbox has accumulated items, offer the natural next step: "There are 6 items in the inbox — want to run the Review Loop?"

## Notes

- Orient is read-only — it never creates, modifies, or deletes anything.
- The `plugin_id` for all tool calls is `"product-brain"`.
- If this is the first time Orient has run and there's no daily log, no inbox items, and no active documents, acknowledge that the vault is fresh and suggest Capture as the natural starting point.
- Orient can be run any time, not just in the morning. "Where was I?" mid-afternoon is the same skill, same purpose.
