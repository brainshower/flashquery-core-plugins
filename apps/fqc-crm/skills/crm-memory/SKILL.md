---
name: crm-memory
description: >
  Use this skill when the user asks to save, recall, or update CRM-related
  memories — impressions, preferences, and ambient intelligence. Trigger on
  "remember that Sarah prefers email", "note that X is sensitive about Y",
  "what do I remember about X", "save this observation", "always lead
  briefings with opportunity status", "I heard at a conference that X",
  or any request to store or retrieve impressions, communication preferences,
  deal signals, relationship context, or company intelligence. These are
  things that don't belong in a vault document — hunches, preferences,
  ambient intel. Do NOT trigger on "remember to follow up with X" or
  "remind me to call X" — those are action items, not memories.
---

# CRM Memory

Handles all memory operations for the CRM: saving new impressions and observations, searching what's already known, and updating memories when information changes. Memory is distinct from the vault document — it holds the things that don't belong in a structured document but are too important to lose.

## When to use

Use this skill when:
- "Remember that Sarah is sensitive about her old vendor" -> save a memory
- "Note that John prefers email over calls" -> save a memory
- "What do I remember about Acme Corp's situation?" -> search memories
- "I heard at the conference that Acme is considering a rebrand" -> save ambient intelligence
- "Always lead my briefings with opportunity status" -> save a user preference
- "Update what I know about Sarah's deal timeline" -> update a memory

## What belongs in memory vs. a document

This is the most important distinction to make before saving anything.

**Use memory for:**
- **Impressions**: "Sarah seemed frustrated with her current vendor — good opening" — a gut feeling, not a fact
- **Communication preferences**: "James prefers a quick email rather than a call to confirm meetings" — how a person likes to be reached
- **Relationship context**: "Maria is close with the CEO — go through her for anything strategic" — relationship dynamics and sensitivities
- **Deal context**: "Their budget conversation suggested ~$50k range but they haven't confirmed" — pricing signals, negotiation nuance, timeline signals
- **Company intelligence**: "Heard at the conference that Acme is expanding into the European market" — ambient intelligence from outside your direct interactions
- **User CRM preferences**: "Always lead briefings with opportunity status before background" — how you want the AI to behave

**Use the vault document for:**
- Email addresses, phone numbers, job titles — factual contact details
- Interaction history — the full log of what was said and done (Interaction Timeline section)
- Company description, website, location — business facts
- Opportunities and deals that are active and documented — tracked status, not impressions

If you're unsure: ask yourself "would I trust this in a Dataview table?" If yes, it belongs in the document. If it's a hunch, a preference, or something you overheard, it belongs in memory.

## Memory categories

When saving a memory, choose the appropriate category:

| Category | Use for |
|----------|---------|
| `communication_preferences` | How a contact prefers to be reached — email vs. call, response times, best contact windows |
| `relationship_context` | Rapport notes, personal details shared, sensitivities, who they trust, what to avoid |
| `deal_context` | Pricing signals, budget hints, decision timelines, negotiation positions, urgency signals |
| `company_intelligence` | Market position, strategic moves, org changes, competitive signals, industry observations |

User CRM preferences (e.g., "always lead with opportunity status") can be saved under `relationship_context` or as a general note — they will be retrieved by `search_memory` when running `crm_intel`.

## Saving a memory

Call `save_memory` with:
- `content`: the memory content, prefixed with the category in brackets. Example:
  ```
  [relationship_context] Sarah Chen seems frustrated with her current data vendor — she mentioned slow support response times as her main pain point. Good opening for a conversation about switching.
  ```
- `plugin_scope`: `"crm"` — scopes this memory to the CRM plugin so it's retrievable in CRM context
- `tags`: relevant entity names or terms to improve retrieval, e.g., `["Sarah Chen", "data vendor"]` or `["Acme Corp", "expansion"]`

Confirm to the user: "Saved. I'll surface this when you ask about [entity] next time."

## Searching memories

When the user asks what's remembered about an entity, or when context is needed during intelligence synthesis:

Call `search_memory` with:
- `query`: the entity name plus relevant terms, e.g., `"Sarah Chen relationship context"` or `"Acme Corp strategy intelligence"`
- `plugin_scope`: `"crm"` — limits results to memories saved in CRM context
- `limit`: 5-10 results is usually sufficient

Present relevant memories with their content. Use judgment to filter out memories that aren't relevant to the current question.

## Updating a memory

When information changes or a memory needs correction:

1. Call `search_memory` to find the existing memory (use the entity name and category as the query).
2. From the results, identify the memory ID of the entry to update.
3. Call `update_memory` with:
   - `memory_id`: the memory ID from the search result
   - `content`: the updated content (prefix with category as before)
   - `plugin_scope`: `"crm"`
   - `tags`: updated tags if relevant

The update uses insert-only versioning — the old memory is preserved in the version chain and the new content becomes the current version. You do not need to delete the old memory.

## Notes

- Memory retrieval is semantic — `search_memory` uses vector similarity, so you don't need an exact match on the contact or company name. Searching "Sarah" or "data vendor frustration" will find the right memories.
- When running the `crm_intel` skill, always check memories as part of the synthesis — they often contain the most actionable intelligence (impressions, deal signals, user preferences) that isn't visible in the structured record or vault document.
- The four categories (`communication_preferences`, `relationship_context`, `deal_context`, `company_intelligence`) are guidance for the AI, not a strict classification system. Use your judgment when a memory could fit more than one category.
