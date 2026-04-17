---
name: brief
description: >
  Use this skill when the user wants a synthesized summary of Product Brain
  content for a specific context — before starting work on a feature, preparing
  for a milestone, reviewing a topic area, or doing a development handoff.
  Trigger on "brief me on X", "summarize what we know about X", "prepare a
  brief for X", "what's the full picture on X", "give me the background on X",
  "development handoff for X", "milestone brief for X", or any request to
  pull together multiple documents into a coherent summary. Also trigger when
  the user asks to "trace the lineage" of a feature spec or wants to understand
  how a decision evolved from its original signals. Even casual requests like
  "what's the story behind X" or "fill me in on X" should trigger this skill.
  This is read-only — it synthesizes existing content but doesn't create or
  modify anything.
---

# Brief

Synthesize relevant Product Brain content into a coherent summary for a specific context. This is a read-only skill — it pulls together existing documents, traverses provenance chains, and produces a narrative that's useful for the task at hand.

## When it's valuable

Brief shines when the user needs to understand the full picture of a topic that's spread across multiple documents — the feature spec, the research that informed it, the original sparks that started the thread, the decisions made along the way, and any outstanding questions. Instead of reading six documents individually, Brief produces a single coherent summary.

Common contexts:
- **Before starting work on a feature** — what's been decided, what's still open, what the constraints are
- **Development handoff** — everything a developer or AI agent needs to pick up a feature spec and build from it
- **Milestone planning** — what's in scope, what's ready, what's blocked
- **Topic review** — what we know about a topic across all document types
- **Decision archaeology** — tracing how a decision evolved from initial signals through research to final spec

## Steps

### 1. Understand the context

The user's request tells you what to synthesize. Parse:

**Topic or focus** — what they want briefed (a feature, a milestone, a topic area, a specific document's lineage)

**Depth** — do they want a quick overview or a thorough briefing? "Quick summary of X" is different from "give me the full background on X for a dev handoff." Default to a medium depth that covers the essentials without overwhelming.

**Audience** — who is this for? If it's a development handoff, include technical constraints and dependencies. If it's for the user's own orientation, emphasize decisions and open questions.

### 2. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

### 3. Find relevant documents

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"documents"`
- `filters`: scoped to the relevant project, document types, and statuses
- `limit`: 20

For a topic-based brief, also call `search_all` with the topic as the query to catch documents that are semantically related but might not match structured filters.

### 4. Traverse provenance

This is what makes Brief more than a search result list. Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"provenance"`
- `filters`: to find lineage chains connected to the key documents

For a feature spec brief, walk backward: spec → contributing research notes → originating sparks. This reveals not just what was decided, but the signal path that led to the decision.

For a topic brief, walk in both directions: find what contributed to each document and what each document contributed to.

The provenance chain is what lets Brief answer "why does this feature spec exist?" — not just "what does it say?"

### 5. Read targeted content

Use the outline-first pattern to keep token usage manageable:

a. Call `get_doc_outline` for each relevant document — this gives you the section structure and linked documents without reading the body.

b. Based on the outline, decide which sections actually need reading for this brief.

c. Call `get_document` with `sections` for targeted extraction — e.g., just the "Overview" and "Open Questions" from a feature spec, or just the "Summary" and "Findings" from a research note.

Don't read every document in full. Read the parts that matter for the brief's context.

### 6. Optionally get a tagged summary

If the brief benefits from a broader view — especially for milestone briefs — call `get_briefing` with relevant tags (e.g., `["#milestone", "#dev-ready"]`).

### 7. Compose the brief

Synthesize everything into a coherent narrative. The structure depends on the context:

**Feature brief:** Overview → User need → What's been decided → What's still open → Dependencies → Source lineage (where this came from)

**Milestone brief:** What the milestone means → What's in scope → What's ready vs. in progress vs. blocked → Key decisions made → Open questions

**Topic brief:** What we know → Key findings → Decisions related to this topic → Open questions → Related threads worth exploring

**Lineage brief:** The original signals (sparks) → How research developed → What decisions were made → Where things stand now

In all cases, cite the source documents — mention them by title so the user can dig deeper if they want.

### 8. Offer follow-ups

Based on what the brief surfaced:
- If open questions exist → offer to start research
- If a spec is ready for development → note that it's `#dev-ready`
- If the brief was for a feature → offer to run Draft if no spec exists yet

One offer, not a menu.

## Notes

- Brief is read-only — it never creates, modifies, or deletes documents.
- The `plugin_id` for all tool calls is `"product-brain"`.
- When traversing provenance, handle "not found" gracefully. A source document may have been archived or deleted — that's historical lineage, not an error. Mention it as "based on a research note that has since been archived" rather than treating it as a broken reference.
- Brief output is ephemeral — it lives in the conversation, not in the vault. If the user wants the brief preserved, they can ask Capture to save it.
