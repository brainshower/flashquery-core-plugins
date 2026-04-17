---
name: add-project
description: >
  Use this skill when the user asks to add, create, or set up a new project
  in the Product Brain. Trigger on "add a project", "create a new project",
  "new product", "start tracking a new initiative", "add project for X",
  or when the user mentions a new product or initiative they want to start
  capturing knowledge for. Also trigger when the user asks to list projects,
  switch their active project, archive a project, or manage project lifecycle
  in any way. Even casual mentions like "I'm starting a new thing" or
  "let's set up a space for X" should trigger this skill.
---

# Add Project

Creates a new project in the Product Brain and makes it visible to all skills. Also handles project lifecycle: listing active projects, switching active context, and archiving.

## When to use

Use this skill when the user wants to:
- **Create a new project** — a new product, initiative, or area of work they want to capture knowledge for
- **List projects** — see what projects exist and their status
- **Switch active project** — change which project Orient and Review Loop focus on
- **Archive a project** — mark a project as no longer active

The rest of this skill focuses on project creation. Lifecycle operations are described at the end.

## Why projects must be created through this skill

FQC tracks files, not folders. An empty folder created directly on the filesystem is invisible to the scanner. More importantly, the `on_document_discovered` callback routes incoming documents by matching their path against `prodbrain_projects` entries. A folder with no corresponding database record means documents placed there won't be attributed to any project — they become orphans. This skill is the only path that creates both the folder and the database record as a single intentional operation.

## Creating a new project

### Gather information

Have a brief conversation with the user to establish:

**1. Project name** (required) — the display name for this project (e.g., "FlashQuery Core", "Client Portal", "Marketing Site"). This is how the project appears in Orient briefs and skill output.

**2. Project path** (required) — the folder name within the vault root (e.g., `flashquery/`, `client-portal/`). Suggest a kebab-case version of the project name as the default. The user should confirm or override.

**3. Description** (optional) — a sentence or two about what this project is. Useful for context in briefs and when skills need to understand the project's scope.

If the user's message already contains this information (e.g., "add a project called Client Portal"), extract it rather than asking again.

### Steps

#### 1. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config vault root"`
- `tags`: `["product-brain-config"]`

This returns the vault root path and plugin configuration saved during Init. You need the vault root to construct the full project path.

If no configuration is found, the Product Brain hasn't been initialized yet. Tell the user to run Init first.

#### 2. Create the project record

Call `create_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `fields`:
  ```json
  {
    "name": "<project display name>",
    "project_path": "<vault_root>/<project_path>/",
    "status": "active",
    "description": "<optional description>",
    "created_at": "<current ISO timestamp>"
  }
  ```

Save the returned record ID — this is the `project_id` for all documents in this project.

#### 3. Create the folder hierarchy

Create all four project subfolders via `create_directory`:

- `{vault_root}/{project_path}/inbox/`
- `{vault_root}/{project_path}/research/`
- `{vault_root}/{project_path}/specs/`
- `{vault_root}/{project_path}/work/`

These empty folders are immediately visible in Obsidian and ready for documents. No placeholder files are needed — the `prodbrain_projects` record from step 2 is what makes routing work.

**No schema re-registration is needed.** Project folders created after Init are intentionally not declared in the schema. When a document lands in a new project folder, the `on_document_discovered` callback's `asserted_ownership` will be empty (folder unknown to the schema), and the callback falls through to its DB-lookup path: it reads `prodbrain_projects` via `search_records`, matches the document path against registered `project_path` values, and routes correctly. The database record is what makes routing work — not a schema entry.

#### 4. Update configuration memory

Call `search_memory` with `query: "product-brain-config"` and `tags: ["product-brain-config"]` to find the existing configuration memory. Then call `update_memory` with the existing `memory_id` and updated content that includes the new project in the active projects list.

If `update_memory` is not available, call `save_memory` with updated content and archive the old memory.

#### 7. Confirm and offer next step

Tell the user:
- The project was created with its name and folder path
- That they can start capturing content with Capture
- That Orient and Review Loop will include this project

Offer the natural next step: **Capture** to add the first item to the new project.

## Project lifecycle operations

### List projects

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `filters`: `{ "status": "active" }` (or omit filter for all projects including archived)

Present the results showing each project's name, path, status, and description.

### Switch active project

The "active project" controls which project Orient and Review Loop focus on by default. It doesn't prevent other skills from working with any project — it's a session preference, not a structural change. No database record changes.

Call `save_memory` with:
- `content`: `[product-brain-config] Active project: {project_name} (id: {project_id}, path: {project_path})`
- `plugin_scope`: `"product-brain"`
- `tags`: `["product-brain-config", "active-project"]`

Orient and Review Loop read this via `search_memory` at the start of each run to scope their queries to the right project. Archive any previous active-project memory to avoid conflicts.

### Archive a project

Confirm the user's intent, then call `update_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `id`: the project's record ID
- `fields`: `{ "status": "archived" }`

This removes the project from Orient and Review Loop processing. The project folder and all documents remain in the vault and in `prodbrain_documents` with their existing statuses — archiving is a status change, not a deletion. A project can be reactivated by updating its status back to `"active"`.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- Project paths should be unique — check existing projects before creating a new one to avoid overlapping folder claims.
- A project with status `"archived"` can be reactivated by updating its status back to `"active"`.
