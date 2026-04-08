---
name: log-interaction
description: >
  Use this skill when the user asks to log, record, or document an interaction
  with a CRM contact. Trigger on "log a call with X", "record an interaction",
  "I just met with X", "we had a meeting", "had coffee with X yesterday",
  "just got off a call with X", "log a meeting with X", "I emailed X about Y",
  "record a conversation", or when the user describes a meeting, call, email,
  or message exchange they had and wants it tracked. This creates an interaction
  record and appends to the contact's vault timeline — not for creating new
  contacts (use add-contact) or saving impressions from the interaction (use
  crm-memory).
---

# Log Interaction

Records an interaction you had with a contact. This does three things: creates a structured database record of the interaction (for date-range queries), appends a human-readable entry to the contact's Interaction Timeline in their vault document (so you can read the history in Obsidian), and updates the contact's `last_interaction` date (so you can query "who haven't I spoken to in 30 days?").

## When to use

Use this skill when someone says "log a call with X", "I just met with Y", "record an interaction", "we had a meeting", or similar.

## Information to gather

Ask the user for:
- **Contact name** (required) — who you interacted with
- **Interaction type** (required) — meeting, call, email, or message
- **Date** (optional) — defaults to today if not specified
- **Summary** (optional) — what happened, what was discussed
- **Action items** (optional) — any follow-ups or next steps
- **Company context** (optional) — if this interaction was in the context of a specific business

## Steps

### 1. Find the contact

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`
- `filters`: `{ "name": "<contact name>" }`

If multiple contacts match, ask the user to clarify which one. If no contacts match, tell the user and suggest they add the contact first using the `add_contact` skill.

From the result, note the contact's **record ID** and **fqc_id** (the UUID that links to their vault document).

### 2. Find the business (if mentioned)

If the user mentioned a business context for this interaction:

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"businesses"`
- `filters`: `{ "name": "<business name>" }`

Note the **business record ID** if found.

### 3. Create the interaction record

Call `create_record` with:
- `plugin_id`: `"crm"`
- `table`: `"interactions"`
- `fields`:
  ```json
  {
    "contact_id": "<contact record ID from step 1>",
    "business_id": "<business record ID from step 2, or omit if no business>",
    "date": "<ISO 8601 timestamp, e.g. 2026-03-27T14:00:00Z>",
    "tags": "#interaction/<type>"
  }
  ```
  Where `<type>` is one of: `meeting`, `call`, `email`, `message`

### 4. Append to the contact's vault document

Find the contact's vault document. Use `search_documents` with the contact's name as the query to find the document path, or derive it from the contact's project and name.

Call `append_to_doc` with:
- `identifier`: the contact's document path (or fqc_id)
- `content`: a formatted interaction entry:

  ```markdown
  ## YYYY-MM-DD
  **Type:** Meeting / Call / Email / Message
  **Summary:** {summary of what was discussed}
  **Action Items:** {follow-ups, or "None" if none}
  ```

  Use the actual date in the heading (YYYY-MM-DD format). Fill in the type, summary, and action items from what the user provided. If no summary was provided, use a brief placeholder and let the user know they can edit the document in Obsidian.

### 5. Update last_interaction on the contact record

Call `update_record` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`
- `id`: the contact's record ID
- `fields`: `{ "last_interaction": "<same ISO 8601 timestamp used in step 3>" }`

This enables queries like "who haven't I spoken to recently?" — the `last_interaction` field is what makes date-arithmetic queries possible.

### 6. Report the result

Tell the user:
- The interaction was logged for [Contact Name] on [Date]
- The interaction type and any action items noted
- That the contact's timeline has been updated in their vault document
- That `last_interaction` has been updated on the record

## Notes

- The Interaction Timeline in the vault document is the human-readable history — this is what appears when the user reads the contact's document in Obsidian.
- The interaction record in the database enables structured queries ("all meetings this month", "all interactions with Acme Corp") — it does not store the summary or narrative content.
- The `last_interaction` date on the contact record is specifically for follow-up queries. Always update it after logging any interaction.
- `append_to_doc` always adds to the end of the document, so the Interaction Timeline is chronological — oldest entries first, newest at the bottom. This is fine and expected. Do not attempt to insert entries out of order.
- If the user's interaction description contains an opportunity signal (e.g., "she mentioned they're budgeting for a rebrand", "they want us to pitch"), note this in the interaction summary and ask: "It sounds like there may be an opportunity here — would you like me to track it as a deal?" If they confirm, hand off to the `add-opportunity` skill.
