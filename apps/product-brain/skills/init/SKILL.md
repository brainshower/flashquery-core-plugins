---
name: init
description: >
  Use this skill when the user asks to "initialize Product Brain", "set up
  Product Brain", "set up the product brain plugin", "register the product
  brain", or "create product brain tables". Also trigger when the user says
  "initialize plugin" in a context where the Product Brain plugin is being
  set up for the first time, or when the user mentions wanting to start
  capturing product knowledge, setting up a product vault, or organizing
  product thinking. This is a one-time setup skill that creates the full
  Product Brain infrastructure in FlashQuery Core.
---

# Initialize Product Brain

This skill sets up the Product Brain plugin from scratch: registers the database schema, writes base document templates to the vault, creates the default tag vocabulary, and sets up the first project. Run this once — subsequent projects are handled by the Add Project skill.

## Overview

The Product Brain is a structured knowledge management system for product thinking. It gives the user a dedicated vault section organized for capturing fragments, research, feature specs, and work items — with an AI assistant that handles filing, tagging, connection-surfacing, and periodic review.

Initialization creates three layers of infrastructure:

1. **Database tables** — five tables for querying documents by project, type, status, and lineage without reading vault files
2. **Vault structure** — template files, a tag vocabulary, feedback folder, and the first project's folder hierarchy
3. **Configuration memory** — saved preferences so all skills know where things live

## Setup conversation

Before doing anything, have a brief setup conversation with the user. You need three things:

**1. Vault location** — where in the vault the Product Brain should live. This becomes the root path. A reasonable default is `product-brain/` at the vault root, but the user may prefer something like `Products/` or a nested path. The `_plugin/` folder (templates, feedback) will live directly under this root.

**2. First project name** — the name of their first product or initiative (e.g., "FlashQuery Core", "My App", "Client Project"). Every document in the Product Brain belongs to a project, so at least one must exist before anything can be captured.

**3. First project path** — the folder name for this project within the vault root (e.g., `flashquery/`, `my-app/`). Suggest a kebab-case version of the project name as the default. The project folder will contain `inbox/`, `research/`, `specs/`, and `work/` subfolders.

**4. Any additional projects?** — ask whether they have other products or initiatives to register right now. If yes, gather a name and path for each. All projects declared during Init get their folder entries included in the schema and their folders created in one pass. Projects added later via the Add Project skill will work through the database-lookup routing path instead.

Keep this conversational and quick. If the user has already stated preferences (e.g., "set up Product Brain for FlashQuery in the products/ folder"), extract answers from what they said rather than asking again.

## Steps

### 1. Read and prepare the schema

Read the schema file at `references/schema.yaml` (relative to the product-brain skill root — two levels up from this SKILL.md, at `skills/product-brain/references/schema.yaml`). Read the full file content as a string.

Before registering, append folder entries for every project declared during setup to the `documents.types` section. For each project (e.g., one with path `flashquery/` under vault root `product-brain/`), append:

```yaml
    - name: flashquery-inbox
      folder: product-brain/flashquery/inbox
      description: "Inbox for FlashQuery project — sparks land here"
    - name: flashquery-research
      folder: product-brain/flashquery/research
      description: "Research notes for FlashQuery project"
    - name: flashquery-specs
      folder: product-brain/flashquery/specs
      description: "Feature specs for FlashQuery project"
    - name: flashquery-work
      folder: product-brain/flashquery/work
      description: "Work items for FlashQuery project"
```

Also update the `_plugin` folder entries to include the vault root:

```yaml
    - name: templates
      folder: product-brain/_plugin/templates
      description: "Base and user-defined document templates"
    - name: feedback
      folder: product-brain/_plugin/feedback
      description: "Plugin self-improvement notes"
```

### 2. Register the plugin

Call `register_plugin` with:
- `schema_yaml`: the full modified schema content from step 1
- `plugin_instance`: if the user specified an instance name, pass it here. Otherwise omit (defaults to "default").

This creates five database tables:
- `prodbrain_projects` — project registry
- `prodbrain_documents` — document index by project, type, and status
- `prodbrain_templates` — template registry
- `prodbrain_provenance` — directed lineage relationships between documents
- `prodbrain_review_state` — Review Loop execution state

The `plugin_id` for all subsequent tool calls is `"product-brain"`.

### 3. Write base templates to the vault

Read each template file from `references/templates/` in the skill directory. There are five base templates:

| Template | File | Document type |
|----------|------|---------------|
| Spark | `references/templates/spark.md` | `spark` |
| Research Note | `references/templates/research-note.md` | `research_note` |
| Feature Spec | `references/templates/feature-spec.md` | `feature_spec` |
| Work Item | `references/templates/work-item.md` | `work_item` |
| Daily Log | `references/templates/daily-log.md` | `daily_log` |

For each template:

a. Read the template file content from the references directory.

b. Call `create_document` with:
   - `title`: the template's display name (e.g., "Spark", "Research Note")
   - `path`: `{vault_root}/_plugin/templates/` (e.g., `product-brain/_plugin/templates/`)
   - `content`: the full template file content (including frontmatter)

c. Extract the `fqc_id` from the response (appears as `fqc_id: {uuid}` in the response).

d. Call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"templates"`
   - `fields`:
     ```json
     {
       "fqc_id": "<uuid from step c>",
       "name": "<template display name>",
       "document_type": "<spark|research_note|feature_spec|work_item|daily_log>",
       "is_base": true,
       "plugin_version": "0.1.0",
       "created_at": "<current ISO timestamp>"
     }
     ```

### 4. Write the tag vocabulary

Read the default tag vocabulary from `references/tags-default.md` in the skill directory.

Call `create_document` with:
- `title`: `tags`
- `path`: `{vault_root}/_plugin/` (e.g., `product-brain/_plugin/`)
- `content`: the full tag vocabulary file content

This creates `_plugin/tags.md` — the single source of truth for available tags. Every skill that applies tags (`Capture`, `Close`, `Review Loop`, `Draft`, `Organize`) reads this file via `get_document` at runtime. The user can edit it directly in Obsidian or any text editor — changes take effect on the next skill invocation.

### 5. Create projects

For **each project** declared during the setup conversation, perform the following steps in order:

a. Create the project record — all documents reference their owning project. Call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"projects"`
   - `fields`:
     ```json
     {
       "name": "<project display name>",
       "project_path": "<vault_root>/<project_path>/",
       "status": "active",
       "created_at": "<current ISO timestamp>"
     }
     ```

   Save the returned record ID — this is the `project_id` used by all documents in this project.

b. Create the folder hierarchy. Call `create_directory` for each subfolder:
   - `{vault_root}/{project_path}/inbox/`
   - `{vault_root}/{project_path}/research/`
   - `{vault_root}/{project_path}/specs/`
   - `{vault_root}/{project_path}/work/`

c. Create a welcome spark in the inbox to give the user something to see immediately. Call `create_document` with:
   - `title`: `Welcome to {project_name}`
   - `path`: `{vault_root}/{project_path}/inbox/` (e.g., `product-brain/flashquery/inbox/`)
   - `content`: a spark-format welcome note explaining that this is the project's inbox and how to start capturing. Use the spark template structure (frontmatter `type: spark`, body with the welcome message, empty Related and Sources sections).

d. Register the welcome spark in the documents table. Extract the `fqc_id` from the response in step c, then call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"documents"`
   - `fields`:
     ```json
     {
       "fqc_id": "<welcome doc fqc_id>",
       "project_id": "<project record id from step a>",
       "document_type": "spark",
       "status": "active",
       "created_at": "<current ISO timestamp>"
     }
     ```

Repeat steps a–d for every project. The first project declared is treated as the active project in the configuration memory saved in the next step.

### 6. Save configuration memory

Call `save_memory` with:
- `content`: a structured configuration note. Include the vault root and all projects. Example for two projects:

  ```
  [product-brain-config] Vault root: product-brain/. Active projects: FlashQuery Core (path: product-brain/flashquery/), Client Portal (path: product-brain/client-portal/). Plugin ID: product-brain. Templates in: product-brain/_plugin/templates/. Tags file: product-brain/_plugin/tags.md.
  ```

- `plugin_scope`: `"product-brain"`
- `tags`: `["product-brain-config"]`

### 7. Confirm setup

Tell the user what was created:
- The five database tables and what they're for (keep it brief)
- Where template files live (they can customize them)
- Where the tag vocabulary lives (they can extend it)
- Each project that was set up and its folder structure
- That they can now use Capture to start adding content, or Add Project to create additional projects later

Offer the natural next step: **Menu** to see what's available, or **Capture** to add the first item to the vault.

## Notes

- If `register_plugin` returns an error saying the schema version has changed, notify the user — schema migration is not automatic.
- If the plugin was already registered (tables already exist), registration is idempotent — it succeeds without duplicating anything. But template files would be re-created as duplicates, so check first with `search_records` on the `templates` table before writing templates.
- The `plugin_id` for this plugin is `"product-brain"` — pass this as the `plugin_id` parameter in all subsequent MCP tool calls.
- The `_plugin/feedback/` folder is for capturing observations about the plugin's own behavior during use. Skills don't write here automatically — it's a place for the user (or a future self-improvement skill) to note friction points.
- The schema's `documents.types` section declares folder ownership for the discovery system. When `on_document_discovered` fires, the folder-matching logic uses these entries to determine which plugin owns a new document. This is why project folders must be declared in the schema — not just created in the filesystem.
