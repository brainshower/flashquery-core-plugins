---
name: add-opportunity
description: >
  Use this skill when the user asks to create, log, or track a new opportunity,
  deal, or potential project in the CRM pipeline. Trigger on "add an opportunity",
  "new deal with Acme", "log this opportunity", "track this as a deal",
  "potential project with X", "there's work coming from X", "they want us to
  pitch", "add to my pipeline", "create a deal record", or when the user
  describes a business opportunity and wants it tracked. This creates an
  opportunity record for pipeline queries — not for updating an existing
  opportunity's stage (use update-entity for that).
---

# Add Opportunity

Creates a new opportunity record in the CRM. Opportunities are pure query-layer entities — the record enables pipeline queries ("show me all active deals", "what's closing this quarter?") while the opportunity narrative lives in the associated contact and/or company vault documents in their Opportunities sections.

This follows the three-layer routing test (P-05): the opportunity record exists so the AI can find and filter opportunities across the full pipeline. The narrative detail that a human would want to read or edit lives in the vault documents where it already has a natural home.

## When to use

Use when someone says "add an opportunity", "log a deal", "new potential project with X", "track this as an opportunity", "there's a deal brewing", or describes a business opportunity they want the CRM to track.

Do not use for:
- Updating an existing opportunity's tags or stage → `update-entity`
- Adding narrative detail to a contact or company → `log-interaction` or edit the vault document directly
- Recording impressions about a deal → `crm-memory` with `deal_context` category

## Information to gather

Ask the user for:
- **Opportunity name** (required) — a short descriptive name for the deal (e.g., "Acme Corp Rebrand"). If the user doesn't provide one, derive it from the company and context.
- **Company** (optional but typical) — the business associated with this opportunity
- **Contact** (optional) — the primary contact for this deal
- **Expected close date** (optional) — when the deal might close. Accept any precision: specific date, month, quarter, or year.
- **Context** (optional) — what the opportunity is about, deal stage, value, any relevant background

## Steps

### 1. Find linked entities

If the user mentioned a company:

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"businesses"`
- `filters`: `{ "name": "<business name>" }`

Note the **business record ID**. If not found, let the user know and suggest creating the business first with `add-business`.

If the user mentioned a contact:

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`
- `filters`: `{ "name": "<contact name>" }`

Note the **contact record ID**. If not found, suggest creating the contact with `add-contact`.

### 2. Determine tags

Consult `references/tags.md` for the native tag vocabulary. Apply tags based on the user's description:

- **Pipeline stage** — if the user described the stage (e.g., "we're pitching them" → `#stage/proposal`), apply it. If no stage was mentioned, default to `#stage/prospect`.
- **Additional tags** — any other relevant tags from the user's description (e.g., value tier, deal type)

### 3. Convert close_date

If the user provided a close date, convert it to a `timestamptz` value following the imprecise date convention documented in the schema:

| User says | Store as |
|-----------|----------|
| "April 12, 2026" | `2026-04-12T00:00:00Z` |
| "April 2026" | `2026-04-01T00:00:00Z` |
| "Q3 2026" | `2026-07-01T00:00:00Z` |
| "2027" | `2027-01-01T00:00:00Z` |
| "next quarter" | First day of the next calendar quarter |
| "end of year" | First day of December of the current year |

If no close date was mentioned, leave it null.

### 4. Create the opportunity record

Call `create_record` with:
- `plugin_id`: `"crm"`
- `table`: `"opportunities"`
- `fields`:
  ```json
  {
    "name": "<opportunity name>",
    "contact_id": "<contact record ID, or omit if none>",
    "business_id": "<business record ID, or omit if none>",
    "close_date": "<timestamptz value, or omit if none>",
    "tags": "<comma-separated tags>"
  }
  ```

### 5. Update the vault document(s)

The opportunity narrative should be added to the relevant vault document(s) — the Opportunities section of the company doc, the contact doc, or both.

**If a company was linked:**

Find the company's vault document. Call `search_documents` with the company name as the query to find the document path.

Call `append_to_doc` with:
- `identifier`: the company document path (or fqc_id)
- `content`: a brief narrative entry formatted to slot into the Opportunities section:
  ```markdown
  **{Opportunity Name}** — {brief description of the opportunity, stage, timeline, any context the user provided}
  ```

Note: `append_to_doc` always appends to the end of the document. If the Opportunities section isn't the last section, the user can move the entry in Obsidian. Alternatively, read the document with `get_document`, insert the entry at the right place, and use `update_document` to write the full updated content.

**If a contact was linked (and the contact is the primary relationship):**

Find the contact's vault document similarly. Add a brief note to their Opportunities section referencing the deal and company.

### 6. Report the result

Tell the user:
- The opportunity was created with its name
- Linked company and/or contact
- Pipeline stage assigned
- Close date (and note if it was approximated from imprecise input)
- That the narrative was added to the relevant vault document(s)

## Notes

- Opportunity records have no `fqc_id` — they don't get their own vault documents. The narrative lives in the associated contact and company documents. This keeps information consolidated where the user already reads it.
- The record's purpose is enabling pipeline queries: "show me all active opportunities", "what's closing in Q2?", "all deals with Acme". Without the record, this data would be trapped in document prose with no way to query across entities.
- When a user describes an opportunity in passing during another flow (e.g., while logging an interaction), the AI should recognize the opportunity signal and ask if they'd like to track it: "It sounds like there's an opportunity here — want me to log it?"
- Close dates are approximate by nature. The imprecise date convention (store at start of period) is a pragmatic trade-off — the column enables range queries, and the full-precision context lives in the vault document narrative.
