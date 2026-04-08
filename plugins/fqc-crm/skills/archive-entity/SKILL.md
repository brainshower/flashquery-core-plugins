---
name: archive-entity
description: >
  Use this skill when the user wants to archive a CRM contact or company
  entirely — removing it from active use across all data layers. Trigger on
  "archive this contact", "archive Acme", "deactivate this record", "we're
  done with them", "they went out of business", "she left the company",
  "close this out", "no longer relevant". This is a full entity archival, not
  a pipeline stage change — if the user just wants to mark a deal as lost or
  paused while keeping the contact active, use update-entity instead. Nothing
  is deleted; archived entities are recoverable.
---

# Archive Entity

Archives a contact or company across all three CRM data layers — vault document, database record, and optionally related memories. Archiving is a soft operation: nothing is deleted. The entity's status changes to archived, it stops appearing in active pipeline and follow-up queries, but it remains fully searchable and recoverable.

## When to use

Use when someone says "archive this contact", "we're done with Acme", "she left the company", "deactivate this record", "remove from pipeline", or describes a situation where a CRM entity is no longer actively relevant.

Do not use for:
- Changing pipeline stage (e.g., lost deal but contact is still active) → `update-entity` with `#stage/lost`
- Temporary pauses → `update-entity` with `#stage/paused`
- Deleting data permanently → not supported; explain that FQC uses soft archival

## Information to gather

- **Entity name** (required) — which contact or company to archive
- **Reason** (optional but encouraged) — why they're being archived. Saved as a memory for future context.

## Steps

### 1. Find the entity

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"` or `"businesses"` (determine from context; if ambiguous, try contacts first, then businesses)
- `filters`: `{ "name": "<entity name>" }`

If multiple results match, ask the user to clarify. If no results, tell the user the entity wasn't found.

From the result, note the **record ID**, **fqc_id**, and current **tags**.

### 2. Confirm with the user

Before proceeding, confirm what will happen:

> "I'll archive **[Entity Name]**. This will:
> - Set the vault document status to archived
> - Archive the database record
> - Remove the entity from active pipeline and follow-up queries
>
> Nothing is deleted — the document stays in your vault and the record remains searchable with an archived filter.
>
> Should I also archive related memories (impressions, deal context, preferences) for this entity? Or keep them active in case they're useful for future reference?"

Wait for confirmation before proceeding. The memory question matters — sometimes a contact leaves a company but the intelligence about the company is still valuable.

### 3. Archive the vault document

Call `archive_document` with:
- `identifiers`: array containing the entity's document path or fqc_id (e.g., `["CRM/Acme Corp.md"]`)

This sets the document's frontmatter `status` to `archived` and updates the database row accordingly.

### 4. Archive the database record

Call `archive_record` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"` or `"businesses"`
- `id`: the record ID from step 1

### 5. Update tags on the document

Call `apply_tags` with:
- `identifiers`: array containing the entity's document path or fqc_id (e.g., `["CRM/Acme Corp.md"]`)
- `add_tags`: `["#status/archived"]`
- `remove_tags`: `["#status/active"]` plus any `#stage/` tags (archived entities are no longer in the pipeline)

### 6. Archive related opportunities (if applicable)

If archiving a company or contact, check for linked opportunity records:

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"opportunities"`
- `filters`: `{ "business_id": "<business record ID>" }` or `{ "contact_id": "<contact record ID>" }`

For any active opportunities found, ask the user:

> "There are [N] active opportunities linked to [Entity Name]: [list names]. Should I archive those too, or keep them active?"

Archive confirmed opportunities with `archive_record`.

### 7. Archive related memories (if user confirmed)

If the user opted to archive memories:

Call `list_memories` with:
- `tags`: relevant tags that scope to this entity (e.g., the entity name, or plugin-scoped tags)

For each relevant memory, call `archive_memory` with the memory's ID.

If the user opted to keep memories active, skip this step.

### 8. Save archival context as a memory

If the user provided a reason for archiving, save it:

Call `save_memory` with:
- `content`: "[Entity Name] was archived on [date]. Reason: [user's reason]. This is a [contact/company] that was previously [brief context — stage, relationship type, etc.]."
- `tags`: `["crm", "archive-context"]`
- `plugin_scope`: `"crm"`

This memory ensures that if the entity comes up in future conversations (e.g., someone mentions the company), the AI has context about why the relationship ended.

### 9. Report the result

Tell the user:
- The entity has been archived
- What was archived (document, record, and whether memories were included)
- How many opportunities were archived (if any)
- That everything is recoverable — the entity can be reactivated by changing status back to active
- The archival reason was saved as a memory (if one was provided)

## Notes

- Archiving is always soft. Nothing is deleted. The user can reactivate an entity by telling the AI to set it back to active, which would reverse the status and tag changes.
- The distinction between archiving and `#stage/lost` matters: a lost deal means the opportunity didn't work out, but the contact or company is still someone you might engage with. Archiving means the entity itself is no longer relevant to your active CRM.
- Always confirm before archiving. Archival touches multiple data layers and may cascade to opportunities. The user should know what's happening.
- The archival context memory is valuable — six months from now, "why did we stop working with Acme?" has an answer without the user needing to remember.
