---
name: fqc-finder
description: Find, recall, and surface existing content from the FlashQuery Core vault — documents, memories, and plugin records. Use this skill whenever the user wants to search for something, look something up, recall previously saved information, get an overview of a topic, or browse what they have stored. Trigger on phrases like "find documents about," "what do we know about," "show me the notes from," "remember when we discussed," "give me an overview of," "search for anything related to," "what did I save about," "pull up that memory about," "show me what I remembered about," "do I have any notes on," "look up," "find me," "what's stored about," "give me a briefing on," or "show me everything on." Even casual phrasing like "what do I know about X?" or "anything saved on Y?" should trigger fqc-finder.
---

# fqc-finder

This skill orchestrates FlashQuery Core's search and retrieval tools. Its job is to understand what the user is looking for, choose the right search strategy, and synthesize the results into a clear, actionable answer.

## What this skill owns

- Searching and browsing vault documents
- Recalling memories (semantic search, tag-filtered browsing)
- Cross-entity search (documents + memories in one call)
- Getting briefings and overviews on a topic
- Querying plugin records
- Following up on search results with full content retrieval

## Routing heuristic

Read the user's intent and route to the appropriate workflow:

| User intent | Workflow |
|-------------|----------|
| "What do we know about X?" — don't know if docs or memories | → [Unified Search](workflows/unified-search.md) |
| "Find documents about X" or "show me my notes on X" | → [Document Search](workflows/document-search.md) |
| "What did I save/remember about X?" | → [Memory Recall](workflows/memory-recall.md) |
| "Give me a briefing on X" / "overview of project X" | → [Briefing](workflows/briefing.md) |
| "Find contacts/records that match X" (plugin records) | → [Record Search](workflows/record-search.md) |
| "Show me everything from last week" / "what's recent?" | → [Document Search](workflows/document-search.md) (filesystem mode, no filters) |

When uncertain, default to [Unified Search](workflows/unified-search.md) — it covers both documents and memories in one call.

## Synthesis guidance

Don't just dump search results. After retrieving content:

1. **Synthesize, don't list.** Answer the user's actual question using the retrieved content as your source — don't just echo back raw results.
2. **Follow up on promising results.** If a search result looks highly relevant, call `get_document` to read the full content before answering.
3. **Surface the source.** Mention where information came from (document title/path, or "from a saved memory") so the user can find it again.
4. **Acknowledge gaps.** If search returns nothing or very little, say so clearly. Don't invent content.

## Error handling

- **Semantic search unavailable** — if `search_memory` or `search_all` returns an embedding error, fall back to `list_memories` with tag filters for memories and `search_documents` in filesystem mode for documents.
- **Ambiguous filename** — if a document tool returns an ambiguity error, use the full path or fqc_id instead.
- **No results** — let the user know nothing was found and offer to broaden the search or try different terms.
