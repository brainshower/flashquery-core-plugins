---
name: add-business
description: >
  Use this skill when the user asks to add, create, or track a new company
  or organization in the CRM. Trigger on "add a company", "create a business",
  "add a business record for X", "I'm working with a new company", "track
  this company", "new client company", "add this organization", or when the
  user mentions a company they want the CRM to know about. This is for
  creating NEW businesses only — not for updating existing ones (use
  update-entity). Requires at least a business name.
---

# Add Business

Creates a new business in the CRM — a vault document for rich narrative content and an Obsidian-readable company profile, plus a linked database record for structured queries. Uses the same document-first pattern as contacts.

## When to use

Use this skill whenever someone says "add a company", "create a business record for X", "I'm working with a new company", or similar. You need at least a business name to proceed.

## Information to gather

Ask the user for:
- **Name** (required) — the business or organization name
- **Industry** (optional) — sector or market (e.g., energy, SaaS, healthcare)
- **Website** (optional) — company website URL
- **Location** (optional) — city, region, or country
- **Description** (optional) — what the company does, why it matters to the user

## Steps

### 0. Retrieve vault folder configuration

Before creating anything, call `search_memory` with `query: "crm_config vault folders"` and `tags: ["crm-config"]` to retrieve the folder configuration saved during plugin initialization. This tells you:
- Whether documents go in a single folder (e.g., `CRM/`) or separate folders (e.g., `CRM/Contacts/` and `CRM/Companies/`)
- The specific folder path for company documents

If no configuration is found, ask the user where company documents should be stored and save the preference using the `crm-memory` skill's pattern (with `[crm_config]` prefix and `crm-config` tag).

### 1. Create the vault document (document-first)

Call `create_document` with:
- `title`: the business name
- `path`: the vault folder path from step 0 (e.g., `CRM/` or `CRM/Companies/`)
- `content`: a populated version of the company profile template. Structure the body as follows:

  ```markdown
  # Company Information
  <!-- Key facts about the organization -->
  - **Website:** {website or leave blank}
  - **Industry:** {industry or leave blank}
  - **Location:** {location or leave blank}
  - **Size:** {size or leave blank}

  # What They Do
  <!-- A brief description of the company's business and why they matter to you -->
  {description the user provided, or a brief placeholder}

  # Key Contacts
  <!-- People at this organization — linked automatically when contacts are added -->

  # Opportunities
  <!-- Active deals, proposals, or potential collaborations with this company -->

  # Notes
  <!-- Market intelligence, relationship history, and other context -->
  ```

- Industry tag if applicable (e.g., `#industry/energy`, `#industry/saas`, `#industry/healthcare`).  Do not include status tags — those are managed by the system.

### 2. Parse the fqc_id from the response

The `create_document` response contains a line like:
```
fqc_id: 550e8400-e29b-41d4-a716-446655440000
```

Extract that UUID — you will need it in the next step.

### 3. Create the database record

Call `create_record` with:
- `plugin_id`: `"crm"`
- `table`: `"businesses"`
- `fields`:
  ```json
  {
    "name": "<business name>",
    "fqc_id": "<the UUID you parsed from step 2>",
    "tags": "<comma-separated tags, e.g. '#industry/energy'>"
  }
  ```
- `plugin_instance`: pass through if the user's CRM is using a non-default instance name

### 4. Report the result

Tell the user:
- The business was created
- The vault document path (e.g., `CRM/Acme Corp.md`)
- The database record ID
- That contacts can now be linked to this business using the `add_contact` skill

## Notes

- Industry is expressed as a tag (`#industry/energy`), not a database column. This makes it queryable via `search_records` tag filtering and visible in Obsidian's tag pane as something the user meaningfully chose.
- The Key Contacts section in the company document will be populated automatically when contacts are added and linked to this business via the `add_contact` skill.
- Domain, description, and other narrative details live in the vault document — not in the database record. The record exists purely for structured queries like "find all active companies in the energy sector."
