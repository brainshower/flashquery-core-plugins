---
name: capture
description: >
  Use this skill when the user wants to save something to the Product Brain —
  a thought, observation, idea, link, bug report, task, research finding,
  or anything else worth keeping for later product decisions. Trigger on
  "capture this", "save this", "note this", "add this to the brain",
  "log this thought", "I just realized", "here's an idea", "something came
  up", or any time the user shares a fragment of product thinking they want
  preserved. Also trigger when the user shares a URL with commentary like
  "this is relevant to X" or dictates a stream-of-consciousness observation.
  Even quick, casual inputs like "oh, we should think about Y" or "bug: the
  scanner misses hidden files" should trigger this skill. This is the primary
  way content enters the Product Brain — if someone is handing you something
  to remember for later, this is the skill.
---

# Capture

Save a fragment of product thinking to the vault — immediately, without friction. This is the primary input mechanism for the Product Brain.

## The interaction model

Capture is designed around three beats. The first beat is the only one that matters for reliability — the thought gets saved before anything else happens. The second and third beats add value while the context is still warm, but they should feel like a natural extension of the conversation, not a form to fill out.

### Beat 1 — Save immediately

Whatever the user said gets saved to the vault right now. No questions first, no formatting decisions, no "what type is this?" gatekeeping. The thought is safe. This is the non-negotiable first step.

The AI's job here is to take whatever arrived — dictated speech, a sentence fragment, a URL with a comment, a run-on paragraph — and produce a clean document from it. Extract the core idea, give it a clear title, clean up the phrasing if it was messy, and file it. The messiness of the input is the AI's problem to handle, not the user's problem to fix before saving.

### Beat 2 — Pull the thread

After the document is saved, ask one or two targeted follow-up questions to extract context that would make the fragment more useful later. This is time-sensitive — the user still has the thought in their head right now, and once they move on, that context is gone.

Good follow-up questions are specific to what was captured:
- For an observation: "What made you notice this? Is this a pattern or a one-off?"
- For a link: "What specifically caught your eye about this?"
- For a bug: "How critical is this? Is there a workaround?"
- For an idea: "Is this connected to anything you're working on right now?"

Keep it to one or two questions. This is not an interview — it's a brief moment of enrichment while the thought is warm. If the user gives short answers or seems ready to move on, respect that. Update the document with whatever they share via `append_to_doc` or `replace_doc_section`.

### Beat 3 — Surface connections

Scan the vault for related content and flag anything that looks connected. "This looks related to your research note on scanner performance — want me to link them?" The user doesn't have to go looking; the vault looks for them.

If the user confirms a connection, write it as a dual link:
1. A `[[wikilink]]` in the appropriate Sources or Related section (navigation layer — visible in Obsidian's graph view)
2. A provenance record in the database (query layer — traversable by Brief and Draft)

If nothing related is found, or if the user doesn't want to link anything, that's fine. This beat is optional value, not required overhead.

After capture is complete, offer the natural next step if appropriate: "There are now 4 items in the inbox — want to run the Review Loop?" Only offer if the inbox has accumulated enough to be worth processing.

## Steps

### 1. Retrieve configuration and determine project

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

This gives you the vault root, active project, and folder paths.

If the user mentioned a specific project ("capture this for Client Portal"), use that project. Otherwise default to the active project from the configuration memory.

If multiple projects exist and the content is ambiguous, ask the user which project this belongs to — but only if genuinely ambiguous. Most of the time, the active project is correct.

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `filters`: `{ "name": "<project name>" }` (or `{ "status": "active" }` if using the default)

to get the `project_id` and `project_path`.

### 2. Infer document type

Based on what the user said, determine the most appropriate document type:

| Content signal | Type | Folder | Template |
|----------------|------|--------|----------|
| A thought, observation, link, idea, something vague or exploratory | `spark` | `inbox/` | Spark |
| A topic being investigated, accumulated understanding, something with open questions | `research_note` | `research/` | Research Note |
| A bug, task, thing to do, something with inherent doneness | `work_item` | `work/` | Work Item |
| A clear feature description with user need and solution shape | `feature_spec` | `specs/` | Feature Spec |

**Default to spark.** When in doubt, make it a spark. Sparks are the inbox catch-all — the lightest possible structure. The Review Loop will route it to the right destination later. It's much better to capture something as a spark that gets promoted later than to make the user think about categorization before they can save their thought.

The exception is when the user's intent is unambiguous: "bug: the scanner misses hidden files" is clearly a work item. "I've been looking into how other tools handle document versioning and here's what I found..." is clearly a research note. Use judgment, but lean toward spark for anything that's not obvious.

### 3. Create the vault document (Beat 1)

Look up the template for the inferred document type. Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"templates"`
- `filters`: `{ "document_type": "<inferred type>" }`

Read the template content via `get_document` using the `fqc_id` from the template record. Use the template structure, but populate it with the user's content — don't leave `{{placeholder}}` markers in the output. Generate a clear, descriptive title from the content.

Call `create_document` with:
- `title`: a clean, descriptive title generated from the content (e.g., "Scanner misses hidden files" not "Bug report about scanner")
- `path`: `{vault_root}/{project_path}/{folder}/` based on the document type
- `content`: the populated template content

This is the moment the thought is safe. Everything after this is enrichment.

### 4. Register in the documents table

Extract the `fqc_id` from the `create_document` response, then call `create_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `fields`:
  ```json
  {
    "fqc_id": "<fqc_id from create_document>",
    "project_id": "<project_id from step 1>",
    "document_type": "<inferred type>",
    "status": "active",
    "has_open_questions": <true if research_note with open questions, false otherwise>,
    "created_at": "<current ISO timestamp>",
    "updated_at": "<current ISO timestamp>"
  }
  ```

### 5. Apply tags

Read the tag vocabulary via `get_document` with the identifier for the tags file (path: `{vault_root}/_plugin/tags.md`).

Select appropriate tags from the vocabulary based on the content. Choose tags that will help the user find this document later — typically one or two from the Classification group and optionally one from Workflow or Source.

Call `apply_tags` with:
- `identifier`: the `fqc_id` of the new document
- `add_tags`: the selected tags

If the content clearly calls for a tag that doesn't exist in the vocabulary, create it — but note this explicitly: "I've tagged this with `#api-design` — want me to add it to the tag vocabulary?" If the user confirms, append the new tag to `_plugin/tags.md` via `append_to_doc`.

### 6. Pull the thread (Beat 2)

Confirm to the user that the document was saved (briefly — title, type, path). Then ask one or two follow-up questions specific to the content. Keep it conversational and quick.

If the user provides additional context, update the document:
- For sparks: `append_to_doc` to add context to the body
- For research notes: `replace_doc_section` to update the Summary or add to Open Questions
- For work items: `replace_doc_section` to flesh out Description or Context

Update `prodbrain_documents.updated_at` via `update_record` if the document was modified.

### 7. Surface connections (Beat 3)

Call `search_all` with:
- `query`: a semantic search based on the core idea of what was captured
- `type`: `"all"` (searches both documents and memories)

Review the results for genuinely relevant connections — not just keyword overlap, but conceptual relevance. Present the strongest 1-3 connections to the user with a brief explanation of why each seems related.

If the user confirms a connection, write the dual link:

**Navigation layer** — call `insert_doc_link` with:
- `identifier`: the `fqc_id` of whichever document should contain the link
- `target_doc`: the title or fqc_id of the linked document
- `anchor_section`: `"Sources"` or `"Related"` depending on the relationship

Convention for Sources vs. Related:
- **Sources** — directional, meaning "this document was informed by that one." Use when the new capture was derived from or inspired by existing content.
- **Related** — associative, meaning "these are about the same topic." Use when both documents are peers rather than one feeding the other.

**Query layer** — call `create_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"provenance"`
- `fields`:
  ```json
  {
    "source_fqc_id": "<the origin document>",
    "derived_fqc_id": "<the document that was informed>",
    "created_at": "<current ISO timestamp>"
  }
  ```

Convention for direction: the new document is `source_fqc_id` if it contributed to something existing (e.g., a new spark that adds to an existing research note). It is `derived_fqc_id` if it was informed by something existing (e.g., a spark captured after reading an existing research note).

If no relevant connections are found, skip this beat silently — don't tell the user "I didn't find anything related."

## Handling special input types

**URLs and links** — when the user shares a link with commentary, capture the commentary as the body and include the URL in the Sources section. Tag with `#web-research`. The Review Loop will do cursory research on the link later.

**Dictated / speech-to-text input** — expect run-on sentences, missing punctuation, filler words, and incomplete thoughts. Extract the core idea, clean up the phrasing, and produce a coherent document. Don't ask the user to clarify messy input — just do your best interpretation and let them correct if needed.

**Quick tasks / bugs** — when the user's input is clearly a work item ("bug: X doesn't work", "todo: update the docs"), create it as a work item directly in the `work/` folder rather than routing through the inbox. The intent is clear enough to skip the inbox stage.

**Requests to update existing content** — if the user says something like "add this to the research note about X" or "update the scanner performance note with this," this is an Update operation, not a new Capture. Look up the existing document, append to or update it, and update the `prodbrain_documents` record. Don't create a duplicate.

## Notes

- Speed matters here more than anywhere else in the plugin. The window for pulling a thread — getting a bit more out of someone while the thought is still live — is short. Get the document saved first, ask questions second.
- The `plugin_id` for all tool calls is `"product-brain"`.
- If the user seems to be in the middle of something and just wants to drop a thought quickly, abbreviate beats 2 and 3. Confirm the save, skip the follow-ups. The Review Loop will handle enrichment later.
