---
name: add-contact
description: >
  Use this skill when the user asks to add, create, or track a new person
  in the CRM. Trigger on "add a contact", "create a contact for X",
  "add X to my CRM", "I met someone new", "save this contact", "track
  this person", "new contact for X", or when the user describes meeting
  someone and wants them in the CRM. This is for creating NEW contacts
  only — not for updating existing ones (use update-entity) or logging
  interactions (use log-interaction). Requires at least a name.
---

# Add Contact

Creates a new contact in the CRM — a vault document the user can read in Obsidian, plus a linked database record for structured queries. This is the document-first pattern: the vault document is always created before the database record.

## When to use

Use this skill whenever someone says "add a contact", "I met someone new", "create a contact for X", or similar. You need at least a name to proceed.

## Information to gather

Ask the user for:
- **Name** (required) — full name of the contact
- **Company** (optional) — which business they work at
- **Role** (optional) — their title or role
- **Email / phone** (optional) — contact details
- **Context** (optional) — how you know them, why they matter, any relevant background

## Steps

### 0. Retrieve vault folder configuration

Before creating anything, call `search_memory` with `query: "crm_config vault folders"` and `tags: ["crm-config"]` to retrieve the folder configuration saved during plugin initialization. This tells you:
- Whether documents go in a single folder (e.g., `CRM/`) or separate folders (e.g., `CRM/Contacts/` and `CRM/Companies/`)
- The specific folder path for contact documents

If no configuration is found, ask the user where contact documents should be stored and save the preference using the `crm-memory` skill's pattern (with `[crm_config]` prefix and `crm-config` tag).

### 1. Create the vault document (document-first)

Call `create_document` with:
- `title`: the contact's full name
- `path`: the vault folder path from step 0 (e.g., `CRM/` or `CRM/Contacts/`)
- `content`: a populated version of the contact note template. Structure the body as follows:

  ```markdown
  # Contact Information
  <!-- Key details for reaching this person -->
  - **Email:** {email or leave blank}
  - **Phone:** {phone or leave blank}
  - **Role:** {role or leave blank}
  - **Company:** {company or leave blank}

  # Relationship Context
  <!-- How you know them, why they matter, and any sensitivities to be aware of -->
  {any context the user provided, or leave a brief placeholder}

  # Communication
  <!-- Communication style, preferences, and patterns learned over time -->

  # Opportunities
  <!-- Active opportunities, proposals, or potential collaborations -->

  # Next Steps
  <!-- Current follow-ups and action items -->

  # Interaction Timeline
  <!-- Each interaction is logged here as a new entry, appended chronologically -->
  ```

- `tags`: any relevant tags for categorization (e.g., `#stage/qualified`, `#relationship/warm`). Do not include status tags — those are managed by the system.

### 2. Parse the fqc_id from the response

The `create_document` response contains a line like:
```
fqc_id: 550e8400-e29b-41d4-a716-446655440000
```

Extract that UUID — you will need it in the next step. This is the stable identifier that links the vault document to the database record.

### 3. Create the database record

Call `create_record` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"`
- `fields`:
  ```json
  {
    "name": "<contact's full name>",
    "fqc_id": "<the UUID you parsed from step 2>",
    "tags": "<comma-separated tags if any, e.g. '#stage/qualified,#relationship/warm'>"
  }
  ```
- `plugin_instance`: pass through if the user's CRM is using a non-default instance name

### 4. Link to a business (if a company was mentioned)

If the user mentioned a company the contact works at:

a. Call `search_records` with `plugin_id: "crm"`, `table: "businesses"`, and `filters: { name: "<business name>" }` to find the business record.

b. If the business is found, add a bidirectional link between the two documents:
   - Call `insert_doc_link` on the **contact's vault document** (the path returned in step 1) to add `[[Business Name]]` in the Relationship Context section.
   - Call `insert_doc_link` on the **business's vault document** (use `search_documents` with the business name to find its path) to add `[[Contact Name]]` in the Key Contacts section.

c. If the business is not found, note this in your response — the user may want to add the business first using the `add_business` skill, then re-link.

### 5. Report the result

Tell the user:
- The contact was created
- The vault document path (e.g., `CRM/Sarah Chen.md`)
- The database record ID
- Any business links that were established (or any that could not be completed)

## Notes

- The link pattern (`[[Name]]`) is how contacts and businesses are associated. Do not use tags or a "company" column for this — wikilinks in the vault document are the authoritative relationship.
- The vault document is the primary source of truth. The database record exists for structured queries ("find everyone in the energy industry") — not for storing contact details.
- If you need to find the business vault document path for `insert_doc_link`, call `search_documents` with the business name as the query.
