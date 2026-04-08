# Bulk Tagging Workflow

Use this workflow when the user wants to apply or remove tags across a set of documents matching some criteria.

## When to use

- "Tag all the Q1 deliverables as complete"
- "Mark everything in the website project as archived"
- "Add #type/research to all my research docs"
- "Remove the #status/draft tag from all client proposals"

## Tool sequence: `search_documents` → confirm → `apply_tags`

---

## Steps

### 1. Find the candidate set

Call `search_documents` with the criteria that defines the target set:

```
search_documents(
  tags: ["#project/q1", "#type/deliverable"],   // tag filters
  tag_match: "all",                              // "all" for intersection, "any" for union
  query: "...",                                  // optional keyword if needed
  mode: "filesystem",                            // filesystem for reliable tag-based filtering
  limit: 50                                      // increase if the user has a large vault
)
```

Filesystem mode is preferred for bulk operations because it reads directly from the vault — no stale embeddings, no missed results.

### 2. Show the candidates and confirm

Present the list of documents found:

> "I found 7 documents that match your criteria. Here's what I'd tag:
> - Q1 Kickoff Notes (clients/acme/q1-kickoff.md)
> - Q1 Design Deliverable (deliverables/q1-design.md)
> - ...
>
> I'll add `#status/complete` and remove `#status/draft` from all of them. OK to proceed?"

If the user approves, continue. If they want to exclude specific items, refine the list.

### 3. Execute: `apply_tags`

Pass all confirmed document paths (or fqc_ids) in a single `apply_tags` call — it's batch-capable:

```
apply_tags(
  identifiers: ["path1.md", "path2.md", "path3.md", ...],
  add_tags: ["#status/complete"],
  remove_tags: ["#status/draft"]
)
```

`apply_tags` returns a line per document showing the final tag set. Review the output for any errors.

### 4. Report results

Tell the user:
- How many documents were successfully updated
- Which (if any) failed, and why
- What their tags look like now (you can quote a few examples from the response)

---

## Status tag handling

You can only have one `#status/*` tag per document. To change status:
- Include the old status in `remove_tags` and the new status in `add_tags` in the same call.
- If you're not sure of the current status, call `get_doc_outline` on a sample document first to check.

---

## Example

**"Tag all the Q1 deliverables as complete"**

```
// Step 1
search_documents(
  tags: ["#project/q1", "#type/deliverable"],
  tag_match: "all",
  mode: "filesystem"
)

// Step 3 (after confirmation)
apply_tags(
  identifiers: ["deliverables/q1-design.md", "deliverables/q1-spec.md"],
  add_tags: ["#status/complete"],
  remove_tags: ["#status/draft", "#status/active"]
)
```
