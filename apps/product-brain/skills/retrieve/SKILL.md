---
name: retrieve
description: >
  Use this skill when the user asks to find, search, look up, or recall
  something from the Product Brain. Trigger on "what do we know about X",
  "find notes on X", "search the brain for X", "what have we captured about X",
  "what's the rationale behind X", "what have users said about Y", "show me
  research on X", "look up X", or any natural question that implies searching
  across product knowledge. Also trigger on "what sparks are there about X",
  "find feature specs related to Y", or requests filtered by document type
  or project. Even casual asks like "do we have anything on X" or "what did
  we decide about Y" should trigger this skill. This is the primary way to
  get content back out of the Product Brain.
---

# Retrieve

Semantic search across all Product Brain content. This is a read-only skill — it finds and presents information but doesn't modify anything.

## How it works

Retrieve translates a natural question into a scoped search. The user asks something like "what do we know about scanner performance?" and gets back relevant documents with their metadata — type, project, status, tags, and enough content to understand what each one contains.

The skill combines two search mechanisms:
1. **Structured filtering** via `search_records` — narrows by project, document type, status, or tags
2. **Semantic search** via `search_all` — finds conceptually relevant content across documents and memories

Filtering happens first (when applicable), then semantic search within that scope. This keeps results focused rather than returning everything tangentially related.

## Steps

### 1. Parse the user's intent

Identify three things from the user's question:

**Search query** — the core topic or question. "What do we know about scanner performance?" → query is "scanner performance."

**Scope filters** (optional) — any constraints the user specified:
- Project: "in the FlashQuery project" or "for Client Portal"
- Document type: "research notes about X", "feature specs for Y", "sparks about Z"
- Status: "active items", "resolved decisions", "shipped features"
- Tags: "anything tagged #priority", "user feedback items"

**Result intent** — what kind of answer the user expects:
- **List** — "show me everything about X" → return multiple results with summaries
- **Answer** — "what's the rationale behind X?" → synthesize an answer from relevant documents
- **Specific document** — "find the feature spec for document versioning" → locate one document

### 2. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

to get the active project (used as default scope if the user didn't specify one).

### 3. Apply structured filters

If the user specified scope filters, call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: constructed from the scope constraints, e.g.:
  ```json
  {
    "project_id": "<project uuid if specified>",
    "document_type": "research_note",
    "status": "active"
  }
  ```
- `limit`: 20 (reasonable default; increase if the user seems to want comprehensive results)

This gives you a set of `fqc_id` values to focus the semantic search on. If no filters were specified, skip this step — let `search_all` search everything.

### 4. Semantic search

Call `search_all` with:
- `query`: the core search query extracted in step 1
- `type`: `"all"` (searches both documents and memories)

If step 3 produced a filtered set, compare the `search_all` results against the filtered `fqc_id` list and prioritize matches that appear in both. Include high-relevance results from outside the filter set as supplementary findings — they might be unexpectedly useful.

### 5. Present results

How you present depends on the result intent:

**For a list:** Show each relevant document with:
- Title and document type
- Project name
- Status and key tags
- A brief summary (1-2 sentences) of what it contains — use `get_document` with `sections` to read just enough to summarize if the search result snippets aren't sufficient

Order by relevance. Keep the presentation scannable — the user should be able to quickly identify which document they want to dig into.

**For an answer:** Read the most relevant documents via `get_document` (use `get_doc_outline` first if the document is large, then `get_document` with `sections` for targeted reading). Synthesize an answer from the content, citing which documents contributed to the answer.

**For a specific document:** Present the document's metadata and offer to show its full content or a specific section.

### 6. Offer follow-ups

After presenting results, offer natural next actions if appropriate:
- "Want me to show the full content of any of these?"
- "Should I update the status on any of these?" (→ hand off to Update)
- "Want me to brief you on this topic in more depth?" (→ hand off to Brief)

Keep it to one offer, not a menu of options.

## Notes

- This skill is read-only — it never creates, modifies, or deletes documents.
- The `plugin_id` for all tool calls is `"product-brain"`.
- When no results are found, say so plainly and suggest related queries if you can think of any. Don't pad a "no results" response with generic suggestions.
- Memories (saved via `save_memory`) are included in `search_all` results. If a memory is relevant, include it in the results — it might contain context that didn't make it into a formal document.
