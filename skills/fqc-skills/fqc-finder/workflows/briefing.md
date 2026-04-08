# Briefing Workflow

Use this workflow when the user wants a structured overview of a topic, project, or context — pulling together documents, memories, and optionally plugin records in one sweep.

## When to use

- "Give me a briefing on X"
- "What's the status of the website project?"
- "Orient me on the Acme account before my call"
- "Overview of [topic]"
- At the start of a work session on a known topic

## Tool: `get_briefing`

`get_briefing` retrieves matching memories, documents, and optionally plugin records in a single call, scoped by tags.

```
get_briefing(
  tags: ["#client/acme"],      // required — scope by tags
  tag_match: "any",            // or "all" if the user's topic requires all tags
  limit: 20,                   // per section; default is 20
  plugin_id: "crm"             // optional — include plugin records (e.g., CRM contacts)
)
```

## Steps

1. **Identify the scope tags.** Derive from the user's request:
   - "briefing on Acme" → `["#client/acme"]`
   - "website redesign project status" → `["#project/website-redesign"]`
   - "Q1 deliverables" → `["#project/q1"]` or `["#type/deliverable"]`

2. **Decide whether to include plugin records.** If the user's context involves structured data (contacts, opportunities, etc.) from a plugin, include `plugin_id`. Otherwise omit it.

3. **Call `get_briefing`.** The response has three sections:
   - `## Documents` — matching vault documents with titles, paths, fqc_ids, and tags
   - `## Memories` — matching memories with content previews and IDs
   - `## Plugin Records` — (only if `plugin_id` provided) recent records from all plugin tables

4. **Drill into specifics if needed.** After the overview, the user may want detail:
   - Call `get_document` on the most relevant document
   - Call `get_memory` on a memory whose preview is truncated
   - Offer to pull up any specific item

5. **Present the briefing clearly.** Don't just dump the raw output. Synthesize:
   - What documents exist and what they cover
   - What memories are relevant
   - Any notable status (e.g., drafts, blocked items, recent updates)

## Example

**"Orient me on Acme before my call"**

```
get_briefing(tags: ["#client/acme"], plugin_id: "crm")
```

→ Documents section: proposal, meeting notes, pricing brief
→ Memories: communication preferences, budget ($50k), key contact (Sarah, Head of Product)
→ CRM records: opportunity at proposal stage

→ Present: "Here's a quick Acme brief — you have a proposal in draft, two meeting note docs, and a memory noting they prefer async communication with a ~$50k budget. The CRM shows the opportunity is at proposal stage. Want me to pull up the full proposal?"

## When `get_briefing` is the right choice vs. `search_all`

| Situation | Prefer |
|-----------|--------|
| User has a clear topic and tags | `get_briefing` — scoped, structured output |
| User has a natural-language query without clear tags | `search_all` — semantic, unscoped |
| User wants documents only | `search_documents` |
| User wants overview before a meeting or task | `get_briefing` |
