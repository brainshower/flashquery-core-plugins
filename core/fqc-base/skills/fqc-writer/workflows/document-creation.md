# Document Creation Workflow

Use this workflow when the user wants to create a brand-new vault document.

## Decision tree

```
Does the user want to link this doc to an existing one?
  ├── Yes → Create-and-link pattern
  └── No → Does the user also want to record key takeaways as a memory?
              ├── Yes → Create-then-save-memory pattern
              └── No → Simple creation pattern
```

---

## Simple creation

**Tools:** `create_document` → (optionally) `apply_tags`

1. Call `create_document` with:
   - `title` — derive from user's request; ask if unclear
   - `content` — the markdown body; write it fully before calling
   - `path` — optional; infer from context (e.g., `"clients/acme/notes.md"`) or omit to place at vault root
   - `tags` — infer appropriate tags from context (see Tag conventions below)
   - `frontmatter` — optional object of additional frontmatter fields merged in at creation time. Use this to set custom fields (e.g., `client`, `project`, `priority`) without a follow-up `update_doc_header` call. Reserved keys `fqc_id`, `status`, `created`, and `fqc_instance` are managed by FlashQuery Core and cannot be overridden — any value supplied for them is ignored.

2. Parse the `fqc_id` from the response:
   ```
   Document created: clients/acme/notes.md
   fqc_id: a1b2c3d4-e5f6-7890-abcd-ef1234567890   ← parse this
   ```

3. If additional tags are needed beyond what was set in step 1, call `apply_tags` separately with the returned fqc_id (or the path).

4. Tell the user where the document was saved (the vault-relative path from the response).

---

## Create-and-link

**Tools:** `create_document` → `insert_doc_link`

Use when the user says something like "start a new doc about X and link it to Y."

1. Call `create_document` (as above). Parse the returned fqc_id.
2. Call `insert_doc_link`:
   - `identifier` — the new document (use the fqc_id or returned path)
   - `target` — the document to link to (use whatever identifier the user provided)
   - `property` — default `"links"`; override if the user specifies a relationship type like "parent" or "related"
3. Optionally call `save_memory` to record the relationship if it's likely to be useful across sessions.

---

## Create-then-save-memory

**Tools:** `create_document` → `save_memory`

Use when writing up notes, summaries, or anything that surfaces a key takeaway worth retaining.

1. Call `create_document` (as above).
2. Identify 1–3 high-value takeaways from the content — facts, decisions, preferences — that the user would benefit from recalling in a future conversation without re-reading the document.
3. Call `save_memory` for each:
   - `content` — a precise, self-contained sentence; include context (who, what, when)
   - `tags` — mirror the document's tags (e.g., `["#client/acme", "#type/meeting-notes"]`)
4. Tell the user what memories were saved and why.

---

## Tag conventions

Suggest tags based on the document's type and context. Common patterns:

| Document type | Suggested tags |
|---------------|----------------|
| Meeting notes | `#type/meeting-notes`, `#client/{name}` or `#project/{name}` |
| Research      | `#type/research`, `#status/active` or `#status/draft` |
| Proposals     | `#type/proposal`, `#client/{name}` |
| Deliverables  | `#type/deliverable`, `#project/{name}`, `#status/draft` |
| Reference     | `#type/reference` |

- Tag namespace is `#category/value` — lowercase, no spaces.
- Do not include `#status` in your tags list unless directed to by the user (we already have a status property in the frontmatter)
- Do not include tags concerning the directory, path or filename of the document.
- Avoid over-tagging: 2–4 tags is usually right.

---

## Example patterns

**"Write up notes from today's call with Acme"**
→ `create_document` (title: "Acme Call Notes - [date]", tags: `["#type/meeting-notes", "#client/acme"]`) → `save_memory` (key takeaways)

**"Start a new research doc on vault sync and connect it to the FQC roadmap"**
→ `create_document` (title: "Vault Sync Research", tags: `["#type/research", "#status/active"]`) → `insert_doc_link` (target: "FQC roadmap")

**"Create a proposal draft for Acme's AI integration project"**
→ `create_document` (title: "Acme AI Integration Proposal", path: "clients/acme/proposal.md", tags: `["#type/proposal", "#client/acme", "#status/draft"]`)

**"Start a proposal for Acme and mark it high priority with a due date"** — use `frontmatter` to set custom fields up front instead of a follow-up `update_doc_header`:
```
create_document(
  title: "Acme Proposal",
  path: "clients/acme/proposal.md",
  content: "...",
  tags: ["#type/proposal", "#client/acme"],
  frontmatter: { client: "Acme", priority: "high", "due-date": "2026-05-01" }
)
```
