---
name: close
description: >
  Use this skill when the user wants to wrap up their day, log what got done,
  capture end-of-day notes, or set up tomorrow's starting point. Trigger on
  "close out the day", "end of day", "wrap up", "log what I did today",
  "daily close", "what did I get done", "let me close out", or any request
  to record the day's work and set up for tomorrow. Also trigger when the
  user says "I'm done for the day" or "let's capture today before I forget".
  This is the counterpart to Orient — it feeds directly into tomorrow's
  morning brief.
---

# Close

The end-of-day counterpart to Orient. Has a brief conversation with the user to capture what happened today, then creates a daily log document that feeds into tomorrow's Orient brief.

## What it produces

A daily log with four sections:
- **What Got Done** — summary of work completed
- **How It Went** — process notes, blockers, anything worth flagging about execution
- **Discoveries and Notes** — observations from the day that belong in the product record (architectural insights, unexpected findings, things to investigate)
- **Tomorrow** — the user's priorities for the next session

The "Tomorrow" section is the most important output — it's what Orient reads to anchor tomorrow's brief. The "Discoveries and Notes" section is where execution learnings get preserved before they evaporate — insights like "got the Docker container working; the missing piece was the health check endpoint" that don't belong in a task tracker but do belong in the product record.

## The close-out conversation

This is a brief, conversational exchange — not a form. Ask the user a few natural questions to draw out what's worth capturing:

Start with something like: "What did you get done today?" or "How did the day go?"

Based on their response, you might follow up with:
- "Anything surprising or worth noting about how that went?"
- "Any discoveries or insights from the work that are worth capturing?"
- "What are you planning to pick up tomorrow?"

If the user gives a comprehensive response all at once, don't ask redundant follow-ups. If they're terse ("just worked on the scanner"), gently probe for anything beyond the bare facts — blockers, observations, tomorrow's plan.

If the user states a preference about how Orient or other skills should behave (e.g., "I want Orient to lead with open research notes" or "stop showing me archived items"), capture it as a memory in step 4.

## Steps

### 1. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

Identify the active project and vault root.

### 2. Have the close-out conversation

Engage the user in the conversational flow described above. Gather enough context to fill the four sections of the daily log. Don't rush — this is the point of the skill. But also don't turn it into an interrogation. A few exchanges is enough.

### 3. Create the daily log document

Look up the daily log template. Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"templates"`
- `filters`: `{ "document_type": "daily_log" }`

Read the template via `get_document` using the `fqc_id` from the template record.

Create the daily log document. Call `create_document` with:
- `title`: a date-based title (e.g., `Daily Log — 2026-04-17`)
- `path`: the project root (e.g., `product-brain/flashquery/`) — daily logs live at the project level, not in a subfolder
- `content`: the populated daily log template with the four sections filled in from the conversation

### 4. Register and tag the document

Extract the `fqc_id` from the response, then:

a. Call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"documents"`
   - `fields`:
     ```json
     {
       "fqc_id": "<fqc_id>",
       "project_id": "<active project id>",
       "document_type": "daily_log",
       "status": "active",
       "created_at": "<current ISO timestamp>",
       "updated_at": "<current ISO timestamp>"
     }
     ```

b. Read the tag vocabulary via `get_document` (path: `{vault_root}/_plugin/tags.md`). Apply any relevant tags via `apply_tags` — daily logs typically don't need many tags, but if the user mentioned blockers, tag with `#blocked`; if they flagged a priority, tag with `#priority`.

c. Set frontmatter tags and status via `update_doc_header`.

### 5. Save preferences (if stated)

If the user mentioned a preference during close-out, call `save_memory` with:
- `content`: the preference in clear language (e.g., `[product-brain-config] Orient preference: lead with open research notes instead of inbox count`)
- `plugin_scope`: `"product-brain"`
- `tags`: `["product-brain-config"]`

### 6. Confirm

Briefly confirm the daily log was saved. Mention that Orient will pick it up tomorrow.

Don't offer follow-up actions — the user is closing out. Keep it brief and let them go.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- Daily logs live at the project root level, not inside `inbox/`, `research/`, `specs/`, or `work/`. They're a cross-cutting record of the day, not a specific document type in the pipeline.
- If the user runs Close multiple times in a day, create a new log for each run — don't overwrite the previous one. The earlier log might have useful context.
- The Close skill is the natural endpoint of a day. Skill chaining suggests: Close → confirm Orient is ready for tomorrow. That's just the confirmation message, not a separate skill invocation.
