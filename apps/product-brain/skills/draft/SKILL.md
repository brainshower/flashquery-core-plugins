---
name: draft
description: >
  Use this skill when the user wants to turn accumulated research and
  fragments into a feature spec. Trigger on "draft a spec for X", "write
  a feature spec", "turn this research into a spec", "spec out X", "I'm
  ready to define this feature", "create a spec from the research on X",
  "shape this into a spec", or any request to produce a coherent feature
  definition from existing Product Brain content. Also trigger when a
  research note is tagged #needs-spec and the user says "let's write
  that spec" or similar. Even casual requests like "I think we know enough
  about X to write it up" should trigger this skill. This is where messy
  research becomes a structured handoff artifact.
---

# Draft

Shape accumulated research and fragments into a feature spec — a coherent document that describes what to build, why, and what the dependencies are. The output is the primary handoff artifact to a development team or AI execution agent.

## What Draft produces

A feature spec document following the Feature Spec template:
- **Overview** — one paragraph on the feature and why it's being built
- **User Need** — the problem, the audience, what success looks like
- **Proposed Solution** — what we're building and how it addresses the need
- **Product Capability** — how this fits alongside existing features
- **Dependencies and Constraints** — what must be true before this can be built
- **Open Questions** — unresolved decisions (it's OK for a spec to have open questions)
- **Notes** — background context, related decisions, implementation notes
- **Sources** — wikilinks to every research note and spark that contributed

Draft doesn't invent content — it synthesizes what's already been captured. The research notes, sparks, and related documents are the raw material; Draft organizes them into a structure someone can build from.

## Steps

### 1. Identify the scope

The user might say "draft a spec for document versioning" or "turn the scanner research into a spec." Identify:

**The feature or topic** — what the spec is about.

**The source material** — which research notes, sparks, and other documents should feed into the spec. The user might name them explicitly, or you may need to search.

### 2. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

### 3. Gather source documents

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: scoped to the relevant project and topic
- `query`: the feature topic (semantic search)
- `limit`: 20

Also call `search_records` on the `provenance` table to find any existing lineage chains related to the topic — sparks that fed research notes, earlier specs that were superseded, etc.

Run `search_all` with the topic as the query for a broader sweep across documents and memories.

### 4. Read the source material

Use the outline-first pattern:

a. Call `get_doc_outline` for each candidate source document.

b. Identify which sections contain relevant material for the spec.

c. Call `get_document` with `sections` to read targeted content from each source.

For research notes, the key sections are typically Summary, Findings, and Open Questions. For sparks, read the full body (they're short). For related specs, read Overview and Proposed Solution to avoid contradiction.

### 5. Have a brief conversation (if needed)

If the source material has gaps or ambiguities that affect the spec, ask the user before writing. Keep it to the essentials:

- "The research notes cover X and Y but there's nothing about Z — should the spec include that, or is it out of scope?"
- "There are conflicting notes about whether to use approach A or B — which direction should the spec take?"

If the source material is sufficient, go straight to writing. Don't ask for permission to start.

### 6. Create the feature spec

Look up the feature spec template. Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"templates"`
- `filters`: `{ "document_type": "feature_spec" }`

Read the template via `get_document`.

Compose the feature spec, filling in each section from the source material. The Sources section must include a `[[wikilink]]` to every research note and spark that contributed — this is the navigation layer of provenance, and it's not optional.

Call `create_document` with:
- `title`: a clear feature name (e.g., `Document Versioning`, `Scanner Hidden File Support`)
- `path`: `{vault_root}/{project_path}/specs/`
- `content`: the complete feature spec

### 7. Register the document

Extract the `fqc_id` from the response, then:

a. Call `create_record` with:
   - `plugin_id`: `"product-brain"`
   - `table`: `"documents"`
   - `fields`:
     ```json
     {
       "fqc_id": "<fqc_id>",
       "project_id": "<project id>",
       "document_type": "feature_spec",
       "status": "active",
       "has_open_questions": <true if the Open Questions section is non-empty>,
       "created_at": "<current ISO timestamp>",
       "updated_at": "<current ISO timestamp>"
     }
     ```

b. Read the tag vocabulary via `get_document` (path: `{vault_root}/_plugin/tags.md`). Apply appropriate tags via `apply_tags` — at minimum `#needs-review` for a fresh spec, and `#dev-ready` only if the user confirms it's ready for handoff.

c. Set frontmatter via `update_doc_header`.

### 8. Write provenance records (dual-write)

For each contributing source document (research note or spark), write both layers:

**Query layer** — call `create_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"provenance"`
- `fields`:
  ```json
  {
    "source_fqc_id": "<contributing document fqc_id>",
    "derived_fqc_id": "<new feature spec fqc_id>",
    "created_at": "<current ISO timestamp>"
  }
  ```

**Navigation layer** — the `[[wikilinks]]` in the Sources section (already written in step 6). Optionally also call `insert_doc_link` on the source documents to add a backlink in their Related section pointing to the new spec — this makes the connection bidirectional in Obsidian's graph view.

Both layers must be written together. The database is for querying lineage; the wikilinks are for navigating it in Obsidian. Neither is a substitute for the other.

### 9. Present the result

Tell the user the spec was created — title, path, and a brief summary of what it covers. Mention the source documents that contributed (by name, briefly).

Offer the natural next step: "Want me to prepare a Brief for the development handoff?" (→ Brief skill).

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- Draft doesn't replace human judgment. If the research is thin or contradictory, say so in the spec's Open Questions and Notes sections rather than papering over uncertainty with confident-sounding prose.
- For UI-facing features, the spec might be the index document inside a feature subfolder that also contains design assets. In that case, create the spec inside `specs/{feature-name}/` rather than directly in `specs/`.
- If the user asks to revise an existing spec rather than create a new one, this is an edit operation — read the existing spec, make the changes, and update it via `replace_doc_section` or `update_document`. Don't create a duplicate.
