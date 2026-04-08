---
name: initialize-plugin
description: >
  Use this skill when the user asks to "initialize CRM", "set up CRM",
  "register the CRM plugin", or "create CRM tables". Also trigger when
  the user says "initialize plugin" in a context where the CRM plugin
  is being set up for the first time. This is a one-time setup skill
  that registers the CRM schema with FlashQuery Core.
---

# Initialize CRM Plugin

This skill registers the CRM plugin with your FlashQuery Core instance. Run this once before using any other CRM skills.

## When to use

Use this skill when setting up the CRM plugin for the first time, or when setting up the plugin under a new instance name. You only need to run this once — it creates the database tables that all other CRM skills depend on.

## Steps

### 1. Register the schema

Read the schema file from the plugin's shared references directory. The schema is located at `references/schema.yaml` at the plugin root (two levels up from this SKILL.md file — e.g., `fqc-crm/references/schema.yaml`). Read the full file content as a string.

Call `register_plugin` with:
- `schema_yaml`: the full content of the `schema.yaml` file you just read
- `plugin_instance`: if the user specified an instance name (e.g., "work", "personal"), pass it here. Otherwise omit this parameter and it will default to "default".

The plugin system will parse the schema and create four database tables:
- `fqcp_crm_default_contacts` — stores contact records with name, last_interaction, tags, and fqc_id
- `fqcp_crm_default_businesses` — stores business records with name, tags, and fqc_id
- `fqcp_crm_default_interactions` — stores interaction records linking contacts to businesses by date and type
- `fqcp_crm_default_opportunities` — stores opportunity records with name, contact_id, business_id, close_date, and tags for pipeline queries
- (Table names use the instance name in place of "default" if one was specified)

### 2. Configure vault folder structure

Ask the user where CRM documents should be stored in their vault. Present two options:

**Option A: Single folder** — all contacts and companies in one folder (e.g., `CRM/` or `Work/CRM/`). Simpler, everything in one place.

**Option B: Separate folders** — one folder for contacts and another for companies (e.g., `CRM/Contacts/` and `CRM/Companies/`). Useful if the user prefers to browse contacts and companies separately in their file system.

Once the user chooses, save the configuration as a memory so all CRM skills know where to create documents. Call `save_memory` with:
- `content`: a structured configuration note. Examples:

  For Option A (single folder):
  ```
  [crm_config] Vault folder structure: single folder. All CRM documents (contacts and companies) are stored in: CRM/
  ```

  For Option B (separate folders):
  ```
  [crm_config] Vault folder structure: separate folders. Contact documents are stored in: CRM/Contacts/ — Company documents are stored in: CRM/Companies/
  ```

  Use the actual folder paths the user specifies — the examples above are defaults.

- `plugin_scope`: `"crm"`
- `tags`: `["crm-config", "vault-folders"]`

### 3. Configure plugin instance (optional)

If the user wants CRM tables to live under a specific instance name (e.g., "work" or "personal"), ask them now. Save the instance name in a memory so all CRM skills can pass it consistently:

```
[crm_config] Plugin instance name: work
```

If no instance name was specified, use "default" — skills omit `plugin_instance` in that case and the system defaults automatically.

### 4. Confirm setup

Tell the user:
- Which database tables were created
- Where CRM documents will be stored in their vault (the folder structure they chose)
- The project scope, if configured
- That they can now use the CRM skills to add contacts, log interactions, and query their network

## Notes

- If `register_plugin` returns an error saying the schema version has changed, notify the user — schema migration is not automatic. They will need to manually migrate or drop and recreate the tables.
- If the plugin was already registered (tables already exist), the registration is idempotent — it will succeed without duplicating anything.
- The plugin_id for this plugin is `"crm"` — you will pass this as the `plugin_id` parameter in all subsequent MCP tool calls.
