---
name: update-entity
description: >
  Use this skill when the user asks to change, update, or modify something
  about an existing CRM contact, company, or opportunity — tags, pipeline
  stage, relationship type, name, status, or document section content.
  Trigger on "mark Sarah as VIP", "move Acme to proposal stage", "they're
  a client now", "move the deal to negotiation", "update the opportunity
  stage", "she changed her name", "they rebranded", "tag this as high
  priority", "remove the prospect tag", "update Sarah's Next Steps",
  "rewrite the notes for Acme", or any instruction to modify an existing
  CRM entity. This is for modifying existing entities — not for creating
  new ones (use add-contact, add-business, or add-opportunity) or for
  logging interactions (use log-interaction).
---

# Update Entity

Updates an existing contact or company in the CRM. This is the skill that handles all modifications to existing entities — tag changes (pipeline stage, relationship type, industry, custom tags), title changes (name corrections, company rebrands), and document section updates (rewriting Next Steps, Relationship Context, or any other named section).

This skill exists because `add-contact` and `add-business` are creation-only — they have no update path. Without this skill, there is no way to change tags or frontmatter on an existing entity.

## When to use

Use this when someone says "mark X as...", "move X to...", "tag X as...", "remove the ... tag from X", "X is now a client", "change X's name to...", "X rebranded to...", or any similar instruction to modify an existing CRM entity.

Do not use for:
- Creating new entities → `add-contact`, `add-business`, or `add-opportunity`
- Logging interactions → `log-interaction`
- Saving impressions or preferences → `crm-memory`
- Archiving entities → `archive-entity`

## Information to gather

At minimum:
- **Entity name** (required) — who or what is being updated
- **What to change** (required) — the user's instruction, which maps to one or more of the operations below

## Tag reference

Before applying tags, consult `references/tags.md` in this plugin for the native CRM tag vocabulary. That file defines which tags exist, when to apply them, and what user language maps to each tag. It also explains how to handle user-defined tags that fall outside the native taxonomy.

## Operations

This skill supports four types of updates. A single user request may involve more than one — for example, "they're a client now, and they rebranded to Nova Labs" involves both a tag change and a title change.

### Operation 1: Apply or remove tags

The most common update. Covers pipeline stage changes, relationship type changes, industry tags, and custom tags.

#### Steps

**1. Find the entity**

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`, `"businesses"`, or `"opportunities"` (determine from context — if the user mentions a deal or opportunity name, search opportunities; if ambiguous between contact and company, try contacts first, then businesses)
- `filters`: `{ "name": "<entity name>" }`

If multiple results match, ask the user to clarify. If no results, tell the user the entity wasn't found.

From the result, note the **record ID** and **fqc_id** (if present — opportunity records don't have fqc_id).

**2. Determine the tag changes**

Map the user's language to the appropriate tags using `references/tags.md`. Determine:
- **Tags to add** — new tags the user wants applied
- **Tags to remove** — tags that should be removed (e.g., when changing pipeline stage, remove the old `#stage/` tag before adding the new one)

For pipeline stages specifically: only one `#stage/` tag should be active at a time. When the user says "move to proposal stage", that means add `#stage/proposal` and remove whatever `#stage/` tag is currently present. To determine the current stage, check the entity's existing tags from the record returned in step 1.

For tags that don't match the native taxonomy: apply the tag as requested, then save a CRM preference memory noting the custom tag and its intended use (see the "User-defined tags" section in `references/tags.md`).

**3. Apply tags to the vault document (contacts and businesses only)**

If the entity has a vault document (contacts and businesses have fqc_id; opportunities do not):

Call `apply_tags` with:
- `identifiers`: array containing the entity's vault document path or fqc_id (e.g., `["CRM/Acme Corp.md"]`)
- `add_tags`: array of tags to add (e.g., `["#stage/proposal"]`)
- `remove_tags`: array of tags to remove (e.g., `["#stage/qualified"]`)

This updates both the document frontmatter and the Supabase `fqc_documents` row atomically.

For opportunity records (which have no vault document), skip this step — the record update in step 4 is sufficient.

**4. Update the record's tags field**

Call `update_record` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`, `"businesses"`, or `"opportunities"`
- `id`: the record ID from step 1
- `fields`: `{ "tags": "<updated comma-separated tag string>" }`

Build the new tag string by taking the existing tags, removing the ones being removed, and adding the ones being added.

**5. Report the result**

Tell the user what changed:
- Which entity was updated
- Tags added and/or removed
- If a pipeline stage changed, state the transition (e.g., "Moved Acme Corp from qualified → proposal")

### Operation 2: Change entity name (title)

Used when a contact changes their name or a company rebrands. This is less common but important when it happens.

#### Steps

**1. Find the entity** (same as Operation 1, step 1)

**2. Update the vault document title**

Call `update_doc_header` with:
- `identifier`: the entity's document path (or fqc_id)
- `updates`: `{ "title": "<new name>" }`

**3. Update the record name**

Call `update_record` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"` or `"businesses"`
- `id`: the record ID
- `fields`: `{ "name": "<new name>" }`

**4. Update links in related documents**

This is the tricky part. Other documents may reference this entity via `[[Old Name]]` links. Search for documents containing the old name:

Call `search_documents` with the old name as the `query` and `mode: "semantic"`.

For each document that contains a `[[Old Name]]` link, call `get_document` to read it, then call `update_document` to replace `[[Old Name]]` with `[[New Name]]` in the body.

**5. Report the result**

Tell the user:
- The entity was renamed from [Old Name] to [New Name]
- Which related documents had their links updated
- Remind the user that if they have the document open in Obsidian, they should refresh to see the title change

### Operation 3: Update a document section

Used when the user wants to rewrite or replace the content of a specific section in a contact or company document — for example, "update Sarah's Next Steps" or "rewrite the notes for Acme Corp."

#### Steps

**1. Find the entity** (same as Operation 1, step 1)

From the result, note the **fqc_id**. This operation only applies to contacts and businesses (which have vault documents), not opportunities.

**2. Confirm the section and new content**

Identify which section the user wants to update. The standard sections are:

- **Contact documents**: Contact Information, Relationship Context, Communication, Opportunities, Next Steps, Interaction Timeline
- **Company documents**: Company Information, What They Do, Key Contacts, Opportunities, Notes

If the user provided the new content, use it. If they described what they want changed but didn't provide exact text, draft the section content and confirm with them before writing.

**3. Replace the section**

Call `replace_doc_section` with:
- `identifier`: the entity's fqc_id
- `heading`: the section heading (e.g., `"Next Steps"`)
- `content`: the new section content (everything below the heading, not including the heading itself)

This surgically replaces only the target section, leaving the rest of the document untouched.

**4. Report the result**

Tell the user which section was updated and on which entity's document.

#### When NOT to use this operation

- Do not use `replace_doc_section` for the **Interaction Timeline** section — that section is append-only via `insert_in_doc` (log-interaction skill). Replacing it would destroy history.
- Do not use it for tag or title changes — those have their own operations above with proper cross-layer sync.

### Operation 4: Bulk tag update

When a deal closes or a relationship shifts, the user may want to update multiple related entities at once. For example, "Acme is now a client" could mean updating the company AND all contacts associated with it.

#### Steps

**1. Find the primary entity and apply its changes** (Operations 1 or 2 above)

**2. Identify related entities**

If the update logically applies to related entities (e.g., a company stage change that should propagate to linked contacts), call `get_doc_outline` on the primary entity's document to find linked entities.

**3. Confirm with the user before propagating**

Ask: "Acme Corp has been moved to client stage. Should I also update the linked contacts ([names]) to #stage/client?"

Only propagate if the user confirms. Pipeline stages on contacts may differ from the company — one contact might be a client relationship while another is still a prospect at the same company.

## Notes

- Tag changes are the primary use case for this skill. The `apply_tags` tool is the right mechanism because it syncs document frontmatter and Supabase atomically.
- `update_doc_header` is used only for the rarer title/name change case. Do not use it for tag changes — `apply_tags` handles those.
- `replace_doc_section` is the right tool when the user wants to rewrite a specific named section. It's surgical — only the target section is replaced, so there's no risk of accidentally modifying other sections. Never use it on the Interaction Timeline (append-only).
- Always check the current tags before applying changes, especially for pipeline stages where only one `#stage/` tag should be active.
- When a tag doesn't match the native taxonomy in `references/tags.md`, apply it anyway (tags belong to the user — P-02) and save a preference memory so future skills recognize it.
