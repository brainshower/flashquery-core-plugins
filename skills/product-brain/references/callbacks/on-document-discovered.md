# on_document_discovered

FQC callback that fires for every new vault document the scanner detects, whether created by a skill or added externally by the user on the filesystem.

## Parameters

- `path` — vault-relative path of the new document
- `fqc_id` — UUID assigned by FQC's core document system
- `asserted_ownership` — pre-populated by the discovery orchestrator's folder-matching logic. Contains the plugin ID if the document's folder matches a declared `documents.types` entry in the schema, or empty if no match was found.

## Return value

One of four claim values:
- `'owner'` — this plugin owns the document
- `'read-write'` — watcher with write intent
- `'read-only'` — watcher without write intent
- `'none'` — no interest

The Product Brain uses `'owner'` and `'none'` only.

## Execution logic

### Path 1 — Template detection

If `asserted_ownership` identifies this plugin AND the path is under `_plugin/templates/`:

1. Read the file's frontmatter to infer `document_type` from the `type` field
2. Call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"templates"`
   - `fields`:
     ```json
     {
       "fqc_id": "<fqc_id>",
       "name": "<inferred from filename or frontmatter>",
       "document_type": "<from frontmatter type field>",
       "is_base": false,
       "created_at": "<current ISO timestamp>"
     }
     ```
3. Return `claim: 'owner'`

This is the auto-registration path for user-defined templates. The user drops a custom template into `_plugin/templates/`, the next scan cycle picks it up, and it becomes available to all skills.

### Path 2 — Project document routing

If `asserted_ownership` is empty (no folder match from schema declarations):

1. Call `search_records` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"projects"`
   to get all registered projects and their `project_path` values

2. Check whether the document path starts with any registered `project_path`

3. If a match is found:
   a. Infer `document_type` from the subfolder:
      - `inbox/` → `spark`
      - `research/` → `research_note`
      - `specs/` → `feature_spec`
      - `work/` → `work_item`
      - Project root → infer from content or default to `spark`

   b. Call `create_record` with:
      - `plugin_id`: `"product-brain"`
      - `table`: `"documents"`
      - `fields`:
        ```json
        {
          "fqc_id": "<fqc_id>",
          "project_id": "<matched project id>",
          "document_type": "<inferred type>",
          "status": "active",
          "created_at": "<current ISO timestamp>"
        }
        ```

   c. Return `claim: 'owner'`

4. If no match is found: return `claim: 'none'`

## Notes

- Path 2 is the primary routing path for project documents. Only the first project's folders (created during Init) are declared in the schema. Projects created later via Add Project are intentionally NOT added to the schema — Add Project does not re-register. This means `asserted_ownership` will always be empty for documents in those project folders, and routing always goes through the DB-lookup path. This is by design: the `prodbrain_projects` record written by Add Project is what makes routing work, not a schema entry.
- The callback does NOT check for the `_plugin/feedback/` path separately — feedback documents are owned by folder claim from the schema, so `asserted_ownership` handles them automatically.
- Skills that create documents (Capture, Close, Draft) write to `prodbrain_documents` directly as part of their execution. They don't rely on this callback. The callback handles files that arrive *outside* a skill invocation.
