---
name: crm-intel
description: >
  Use this skill when the user asks for CRM intelligence, meeting preparation,
  relationship insights, pipeline status, or opportunity overviews. Trigger on
  "brief me on X", "what do I know about X", "give me a dossier on X",
  "where do my deals stand", "show me my pipeline", "what's closing this
  quarter", "show me my opportunities", "pipeline overview", "who haven't I
  spoken to", "what should I follow up on", or any request to synthesize CRM
  knowledge across contacts, businesses, opportunities, interactions, and
  memories. This skill pulls from all three data layers and synthesizes —
  for simple entity lookups without synthesis, use find-entity instead.
---

# CRM Intelligence

General-purpose CRM knowledge retrieval. Synthesizes information from all three layers — vault documents (rich narrative), database records (structured queries), and memories (impressions and ambient intelligence) — into a comprehensive response tailored to what the user actually needs.

## When to use

Use this skill for any CRM knowledge query:
- "Brief me on Sarah Chen before my call"
- "What do I know about Acme Corp?"
- "Where do my deals stand?"
- "Who haven't I spoken to in the last month?"
- "Give me a pipeline overview"
- "What should I follow up on this week?"

## Understanding what the user needs

Before pulling data, interpret the request:

- **Meeting prep** — "brief me on X before my call/meeting": structured summary emphasizing recent interactions, open opportunities, and things to remember
- **Dossier** — "what do I know about X": full picture of everything stored about an entity
- **Pipeline status** — "where are my deals / pipeline overview": scan records by stage tags, surface active opportunities
- **Follow-up awareness** — "who haven't I spoken to": query `last_interaction` dates, surface overdue relationships
- **Broad intelligence** — any other CRM knowledge query that doesn't fit a single entity

## Entity-specific queries (meeting prep, dossier)

When the user asks about a specific person or company:

1. **Find the entity**: Call `search_records` on `"contacts"` or `"businesses"` table with `filters: { name: "<name>" }`. Get the record ID and fqc_id.

2. **Read the full vault document**: Call `get_document` with the entity's vault path. This contains the full narrative: contact information, relationship context, communication preferences, opportunities, next steps, and interaction history. Use `search_documents` with `mode: "semantic"` and the entity name as the `query` to find the path if you don't have it.

3. **Discover relationships**: Call `get_doc_outline` on the vault document. This returns all outbound links without reading the full body — use it to find connected entities (contacts linked to a company, companies a contact works with).

4. **Surface memories**: Two complementary calls here:
   - Call `search_memory` with the entity's name and relevant terms (e.g., "Sarah Chen relationship impression deal") and `plugin_scope: "crm"`. This uses semantic search to find contextually relevant memories — good for surfacing things that are thematically related even if they weren't explicitly tagged to this entity.
   - Call `list_memories` with `tags` scoped to the entity (e.g., the entity's name or CRM plugin tags) and `plugin_scope: "crm"`. This is an exhaustive listing — it catches every memory that was tagged to this entity, even ones that wouldn't rank highly in a semantic search. Together, the two calls ensure nothing is missed.

5. **Check the user's behavioral preferences**: Call `search_memory` with `query: "CRM preference briefing style"` and `plugin_scope: "crm"` to check if the user has saved preferences about how they want intelligence presented.

6. **Synthesize and respond**. For meeting prep, structure the response as:
   - **Background**: who they are, their role, their company
   - **Recent Interactions**: last 2-3 interactions from the timeline, most recent first
   - **Open Opportunities**: any active deals or collaborations
   - **Things to Remember**: impressions and context from memories
   - **Suggested Talking Points**: based on open opportunities and recent context

   For a dossier, present everything you found across all layers.

## Broad queries (pipeline, follow-ups)

When the user asks about their overall CRM rather than a specific entity:

1. **Get an orientation** — but only for open-ended queries. If the user says something like "what's going on in my CRM?" or "give me an overview of my pipeline", call `search_all` with a broad query (e.g., `"active contacts deals opportunities"`) and `plugin_scope: "crm"`. This crosses all three layers — documents, records, and memories — in a single call and surfaces the most relevant CRM data as a starting point.

   For specific structured queries ("what's closing this quarter?", "who haven't I spoken to in 30 days?"), skip this step and go directly to step 2 — `search_all` adds latency without benefit when you already know exactly what table and field to query.

2. **Query records directly**: Call `search_records` on the appropriate table(s):
   - Pipeline / deals: search the `"opportunities"` table using a natural language `query` (e.g., `"proposal stage active deals"`). Avoid `filters: { tags: "..." }` for stage tags — that does exact equality matching and fails when a record has multiple tags. Instead, use `query` for semantic matching, then inspect the `tags` field on each returned record to confirm the stage.
   - Follow-ups: search `"contacts"` with a `query` that includes date context (e.g., `"contacts not reached recently"`), then sort results by `last_interaction` to find overdue relationships.
   - Active entities: `filters: { status: "active" }` on contacts or businesses.
   - For full pipeline overviews, query both `"opportunities"` (structured deal records) and `"contacts"` / `"businesses"` (for stage tags on entities themselves).

3. **Surface ambient intelligence**: Call `search_memory` with `query` terms relevant to the query (e.g., `"pipeline deal opportunity"` or `"follow up overdue"`) and `plugin_scope: "crm"`. For broader sweeps, also call `list_memories` with `plugin_scope: "crm"` to see all stored memories by category — particularly useful for pipeline queries where deal context memories across multiple entities may be relevant. CRM memories often contain deal context and relationship signals that aren't queryable from records alone.

4. **Synthesize**: Present the results organized by what the user needs — deals by stage, contacts by last interaction date, or whatever grouping is most useful for the query.

## Respecting user preferences

Always check whether the user has stored preferences about how they want CRM intelligence presented. Call `search_memory` with terms like "CRM preference" or "always" or "briefing style" — if the user has saved preferences (e.g., "always lead with opportunity status", "group contacts by company"), honor them in your response.

## Notes

- This is the "intelligence synthesis" skill — it pulls from all three layers and makes judgment calls about what's most relevant. Don't just dump raw data; interpret and prioritize based on what the user asked for.
- For "what do I know about X?" queries, start with the vault document (read it fully), then enrich with memories. The vault document is the primary source of truth for facts; memories add impressions and context.
- `get_doc_outline` is efficient for relationship discovery — it returns links without reading the full body. Use it to discover connected entities, then fetch full documents only for the ones most relevant to the query.
- `get_briefing` gives a broad snapshot across tagged documents — useful for pipeline and follow-up queries. It requires a `tags` array (e.g., `tags: ["#stage/proposal", "#stage/negotiation"]`) and optionally accepts `plugin_id: "crm"` and `tag_match: "any"`. Use it when you need to survey documents across multiple pipeline stages rather than drilling into a specific entity.
