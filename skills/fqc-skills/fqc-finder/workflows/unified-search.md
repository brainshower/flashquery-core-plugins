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

2. **Add tag filters if appropriate.** If the user's context clearly scopes to a client, project, or topic, include matching tags. Otherwise leave `tags` unset and let semantic search do the work.

3. **Call `search_all`.** Review the results:
   - Documents are returned with similarity scores and fqc_ids
   - Memories are returned with similarity scores and memory IDs

4. **Follow up on top document results.** For documents with high similarity scores (e.g., > 0.85), consider calling `get_document` to read the full content before synthesizing your answer. Use `get_doc_outline` for a lighter-weight structure check first if you're unsure whether you need the full body.

5. **Synthesize and respond.** Answer the user's actual question using the retrieved content. Cite document titles and note when something came from a memory.

## Fallback: when embedding is unavailable

If `search_all` returns an embedding error:
1. For documents: call `search_documents` with `mode: "filesystem"` and `query` set to the keyword.
2. For memories: call `list_memories` with relevant `tags` if you can infer them, or with no filters to show recent memories.

## Example

**User:** "What do we know about Acme's budget?"

```
search_all(query: "Acme budget", tags: ["#client/acme"])
```

Results might include:
- A document: "Acme Proposal" (score: 0.91)
- A memory: "Acme's budget for the integration is ~$50k" (score: 0.87)

→ Call `get_document` on the proposal to read pricing details if needed.
→ Synthesize: "Based on your proposal doc and a saved memory, Acme has approximately $50k budgeted for the integration project. The full proposal is in `clients/acme/proposal.md`."
