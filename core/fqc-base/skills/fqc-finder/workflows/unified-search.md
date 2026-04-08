# Unified Search Workflow

Use this workflow when the user is looking for information without specifying whether it's in a document or a memory. It's the default starting point when intent is broad.

## When to use

- "What do we know about X?"
- "Anything on X?"
- "Find everything related to X"
- Any query where the user hasn't narrowed down to documents, memories, or records

## Tool: `search_all`

`search_all` searches documents and memories in one call using semantic similarity.

```
search_all(
  query: "the user's topic",
  tags: [...],      // optional — narrow by tag if context makes it clear
  limit: 10,        // per entity type; increase if you expect many results
  entity_types: ["documents", "memories"]   // default; both types
)
```

## Steps

1. **Formulate the query.** Extract the core topic from the user's message. Be specific:
   - User: "what do we know about Acme's timeline?" → query: `"Acme timeline"`
   - User: "anything on the website project?" → query: `"website project"`

2. **Add tag filters if appropriate.** If the user's context clearly scopes to a client, project, or topic, include matching tags. Otherwise leave `tags` unset.

3. **Call `search_all`.** Review the results — documents and memories are returned with similarity scores and IDs.

4. **Follow up on top document results.** For documents with high similarity scores (> 0.85), consider calling `get_document` to read the full content before synthesizing your answer.

5. **Synthesize and respond.** Answer the user's actual question using the retrieved content. Cite document titles and note when something came from a memory.

## Fallback: when embedding is unavailable

If `search_all` returns an embedding error:
1. For documents: call `search_documents` with `mode: "filesystem"` and a keyword `query`.
2. For memories: call `list_memories` with relevant `tags` if you can infer them.

## Example

**User:** "What do we know about Acme's budget?"

```
search_all(query: "Acme budget", tags: ["#client/acme"])
```

Results: proposal doc (score: 0.91) + memory "Acme's budget ~$50k" (score: 0.87)
→ Call `get_document` on the proposal for full pricing detail if needed.
→ Answer: "Based on your proposal and a saved memory, Acme has ~$50k budgeted for the integration. Full proposal is at `clients/acme/proposal.md`."
