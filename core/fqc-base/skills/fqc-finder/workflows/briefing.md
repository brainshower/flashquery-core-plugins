# Briefing Workflow

Use this workflow when the user wants a structured overview of a topic, project, or context — pulling together documents, memories, and optionally plugin records in one sweep.

## When to use

- "Give me a briefing on X"
- "What's the status of the website project?"
- "Orient me on the Acme account before my call"
- "Overview of [topic]"
- At the start of a work session on a known topic

## Tool: `get_briefing`

```
get_briefing(
  tags: ["#client/acme"],      // required — scope by tags
  tag_match: "any",            // or "all" if the topic requires all tags
  limit: 20,                   // per section; default is 20
  plugin_id: "crm"             // optional — include plugin records
)
```

## Steps

1. **Identify the scope tags** from the user's request:
   - "briefing on Acme" → `["#client/acme"]`
   - "website redesign status" → `["#project/website-redesign"]`

2. **Decide on `plugin_id`** — include if the user's context involves structured plugin data (contacts, opportunities, etc.).

3. **Call `get_briefing`.** The response has three sections:
   - `## Documents` — matching vault docs with titles, paths, fqc_ids
   - `## Memories` — matching memories with content previews
   - `## Plugin Records` — (only if `plugin_id` provided) recent records from all plugin tables

4. **Drill into specifics if needed.** Call `get_document` on the most relevant doc, or `get_memory` on a truncated memory.

5. **Present the briefing as a synthesized summary** — not a raw dump. Cover: what documents exist, what memories are relevant, notable status items.

## When `get_briefing` vs `search_all`

| Situation | Prefer |
|-----------|--------|
| Clear topic with known tags | `get_briefing` — scoped, structured |
| Natural-language query without clear tags | `search_all` — semantic, unscoped |
| Documents only | `search_documents` |
| Pre-meeting orientation | `get_briefing` |

## Example

**"Orient me on Acme before my call"**
```
get_briefing(tags: ["#client/acme"], plugin_id: "crm")
```
→ Synthesize: "Here's a quick Acme brief — proposal in draft, two meeting note docs, a memory noting async communication preference with ~$50k budget, CRM shows the opportunity at proposal stage. Want me to pull up the full proposal?"
