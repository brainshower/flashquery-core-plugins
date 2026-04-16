# Section Editing Workflow

Use this workflow when the user wants a **precise, section-scoped edit** to an existing document — adding an entry under a specific heading, rewriting a particular section, prepending a note to the top, or inserting content between two existing sections — without touching the rest of the body.

This workflow covers the middle ground between `append_to_doc` (dumb append to the end) and `update_document` (full-body rewrite). Prefer these section-scoped tools whenever the edit has a clear anchor in the existing document — they preserve surrounding content, survive formatting that `update_document` would clobber, and avoid unnecessary re-embedding of text the user didn't want changed.

## When to use

- "Log today's call under Interactions" — appending a new entry under a known heading
- "Rewrite the Pricing section with these new numbers" — swapping out one section's body
- "Add a status banner at the top of the proposal" — prepending at the top
- "Insert a new section between Background and Proposed Approach"
- Any edit that names or implies a specific heading

## Decision tree (in priority order)

```
Does the user want to replace the content of a specific section?
  └── Yes → replace_doc_section

Does the user want to add content at a specific position
(after a heading, before a heading, at the end of a section, or at the top/bottom)?
  └── Yes → insert_in_doc

Does the user just want content tacked on at the very end
with no section awareness?
  └── Yes → append_to_doc (see document-modification.md)

Does the user want to rewrite the whole body?
  └── Yes → update_document (see document-modification.md)
```

## Recommended pre-check

When the user's request doesn't explicitly name the heading (e.g., "add it to the client call section" — but there are three client-related headings), call `get_doc_outline` first to see the heading tree. This also tells you whether a heading appears multiple times, so you can pick the right `occurrence`.

```
get_doc_outline(identifiers: "clients/acme/notes.md")
```

---

## `insert_in_doc` — insert at a specific position

Adds content at a precise anchor in the document without disturbing what's already there.

```
insert_in_doc(
  identifier: "clients/acme/notes.md",   // required
  position: "end_of_section",            // required — see enum below
  heading: "Interactions",               // required for after_heading, before_heading, end_of_section
  content: "### 2026-04-15 — Kickoff\n\nDiscussed Q2 scope...",   // required
  occurrence: 1                          // optional, 1-indexed, default 1
)
```

### Parameters

- **`identifier`** (required) — path, filename, or fqc_id of the target document.
- **`position`** (required, enum) — one of: `"top"`, `"bottom"`, `"after_heading"`, `"before_heading"`, `"end_of_section"`. These values are validated at runtime; passing anything else returns an error listing the valid options.
- **`heading`** (string) — the anchor heading. **Required when `position` is `"after_heading"`, `"before_heading"`, or `"end_of_section"`; omit for `"top"` and `"bottom"`**. Case-sensitive — match the heading as it appears in the document (`"Pricing"` ≠ `"pricing"`).
- **`content`** (required) — markdown to insert. Don't include the heading line itself when inserting into an existing section; that's already there.
- **`occurrence`** (integer, optional, default `1`, 1-indexed) — which occurrence of `heading` to anchor on when the same heading name appears more than once.

### Position cheat sheet

| `position` | Where content lands | `heading` required? |
|------------|---------------------|---------------------|
| `top` | Immediately after frontmatter, before the first heading | No |
| `bottom` | At the very end of the document | No |
| `after_heading` | Directly below the named heading line | Yes |
| `before_heading` | Directly above the named heading line | Yes |
| `end_of_section` | After the section's existing content but before the next sibling/parent heading | Yes |

`end_of_section` is the right choice for "log a new entry under X" — new content slots in at the bottom of X's section, before the next heading starts. `after_heading` is for inserting a lede or intro paragraph right below the heading line.

### Examples

**Logging a new interaction under `## Interactions`:**
```
insert_in_doc(
  identifier: "clients/acme/notes.md",
  position: "end_of_section",
  heading: "Interactions",
  content: "### 2026-04-15 — Kickoff call\n\nDiscussed Q2 scope and timeline."
)
```

**Prepending a status banner at the top:**
```
insert_in_doc(
  identifier: "readme.md",
  position: "top",
  content: "> **Status:** Draft — do not circulate\n\n"
)
```

**Inserting a new section before "Proposed Approach":**
```
insert_in_doc(
  identifier: "clients/acme/proposal.md",
  position: "before_heading",
  heading: "Proposed Approach",
  content: "## Current State\n\nAcme is on..."
)
```

**Disambiguating repeated headings with `occurrence`:**
If `## Notes` appears under both `## Meeting 1` and `## Meeting 2`, and the user wants to add to Meeting 2's Notes:
```
insert_in_doc(
  identifier: "journal/2026-04.md",
  position: "end_of_section",
  heading: "Notes",
  occurrence: 2,
  content: "- Follow up with legal re: NDA."
)
```

---

## `replace_doc_section` — swap the content of a specific section

Replaces the body of one section while leaving the rest of the document intact. The heading line itself is preserved automatically — supply only the new body content.

```
replace_doc_section(
  identifier: "clients/acme/proposal.md",   // required
  heading: "Pricing",                        // required, case-sensitive
  content: "Revised pricing as of 2026-04-15...",   // required; body only
  include_subheadings: true,                 // optional, default true
  occurrence: 1                              // optional, 1-indexed, default 1
)
```

### Parameters

- **`identifier`** (required) — path, filename, or fqc_id.
- **`heading`** (required, case-sensitive) — the section to replace. If the heading appears multiple times in the document, the tool returns an error listing each occurrence with its line number; disambiguate with `occurrence`.
- **`content`** (required) — the new body for the section. **Don't include the heading line itself** — it's preserved for you.
- **`include_subheadings`** (boolean, optional, default `true`) — when `true`, replaces the section **including any nested child headings** (so the whole subtree is swapped). When `false`, preserves child headings in place and replaces only the prose directly under the heading, above the first nested heading.
- **`occurrence`** (integer, optional, default `1`, 1-indexed) — which occurrence of `heading` to target when it repeats.

### Undo hint

The response includes the **old section content** under an "Old section content (for undo if needed):" label. Mention this to the user after the operation so they know they can paste it back if the change was wrong — the revert is trivial as long as they act before further edits layer on.

### Examples

**Swap the Pricing section wholesale:**
```
replace_doc_section(
  identifier: "clients/acme/proposal.md",
  heading: "Pricing",
  content: "Revised pricing as of 2026-04-15:\n\n- Tier 1: $25k...\n- Tier 2: $60k..."
)
```

**Replace only the immediate prose under a heading, keep child sections intact:**
```
replace_doc_section(
  identifier: "projects/q2/brief.md",
  heading: "Overview",
  include_subheadings: false,
  content: "Short intro paragraph — child headings like Goals and Timeline are preserved."
)
```

**Replace the second occurrence of a repeated heading:**
```
replace_doc_section(
  identifier: "journal/2026-04.md",
  heading: "Notes",
  occurrence: 2,
  content: "Cleaned up meeting 2 notes."
)
```

---

## Error handling

- **Heading not found** — the tool surfaces the available headings in its error message. Call `get_doc_outline` first if you're uncertain which headings exist, and case-match carefully.
- **Ambiguous heading (multiple occurrences)** — `replace_doc_section` returns an error with each occurrence's line number. Use `occurrence` to disambiguate.
- **Wrong `position` enum value** — the tool validates `position` and returns an error listing the valid set (`top`, `bottom`, `after_heading`, `before_heading`, `end_of_section`). Re-check the spelling.
- **Missing `heading` when required** — `after_heading`, `before_heading`, and `end_of_section` all need `heading`; without it the tool errors.
- **Untracked file (no fqc_id)** — call `get_document` first to auto-provision the fqc_id, then retry the section edit.

## Handoff to document-modification

- For tag-only changes, frontmatter tweaks, link insertion, or full-body rewrites, hand off to [Document Modification](document-modification.md) — those tools are better shaped for those intents.
- For a brand-new document, use [Document Creation](document-creation.md).
