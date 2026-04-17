---
name: find-entity
description: >
  Use this skill when the user asks to find, look up, or search for a
  contact, business, or opportunity in the CRM. Trigger on "find X",
  "look up X", "search for X", "show me X", "who works at X", "show me
  my contacts tagged Y", "do I have a record for X", "list my contacts",
  or any request to locate and retrieve a CRM entity by name, status,
  tags, or relationship. This skill finds and displays entities — for
  intelligence synthesis, meeting prep, or pipeline overviews ("brief me",
  "what do I know about X", "where do my deals stand"), use crm-intel
  instead.
---

# Find Entity

Searches the CRM for contacts and businesses. Supports three search modes: structured database queries, relationship traversal via links, and full document retrieval.

## When to use

Use this skill when someone asks:
- "Find [person or company]"
- "Who works at [company]?"
- "Show me my contacts in the energy sector"
- "What do I know about [person or company]?" (for full details, use `crm_intel` instead)
- "Do I have a record for X?"

## Search modes

### Mode 1: Structured search

For finding entities by name, status, tags, or other record fields:

Call `search_records` with:
- `plugin_id`: `"crm"`
- `table`: `"contacts"` or `"businesses"` (choose based on what the user is looking for, or search both)
- `filters`: a JSON object for exact-match filtering (e.g., `{ "name": "Sarah Chen" }` or `{ "status": "active" }`)
- `query`: a text string for semantic search (use when the user is searching by concept or partial description rather than an exact field value)
- `limit`: how many results to return (default 10; increase if the user wants a broader list)
- `plugin_instance`: pass through if using a non-default instance

Always report for each result: name, record ID, status, and any tags.

### Mode 2: Relationship traversal

For answering "who works at [company]?" or "what companies is [person] connected to?":

1. Call `search_records` to find the entity record (e.g., search businesses by name to find "Acme Corp").
2. Use `search_documents` with the entity name as the `query` and `mode: "semantic"` to find the entity's vault document path.
3. Call `get_doc_outline` on the vault document path. The outline returns all outbound links — for a company document, the Key Contacts section links are the authoritative list of associated contacts.
4. Report the linked entities from the links. If the user wants full details on a linked contact, proceed to Mode 3.

Example: "Who works at Acme Corp?"
- `search_records` -> find Acme Corp record -> get its vault document path
- `get_doc_outline` on the company document -> extract Key Contacts links
- Report: "Acme Corp has 3 contacts: [[Sarah Chen]], [[James Okafor]], [[Maria Reyes]]"

### Mode 3: Full detail retrieval

When the user wants to read everything about a contact or business — "show me everything about Sarah", "full details on Acme":

1. Use `search_records` to find the entity if you don't already have a document path.
2. Use `search_documents` with the entity name as the `query` and `mode: "semantic"` to find the vault document path if needed.
3. Call `get_document` with the vault path to retrieve the full document content.
4. Call `list_memories` with `tags` scoped to the entity (e.g., the entity's name or relevant CRM tags) and `plugin_scope: "crm"` to retrieve all stored CRM memories for this entity — impressions, communication preferences, deal context, and company intelligence. This catches everything the AI knows about the entity beyond what's in the vault document.
5. Present a unified view: the full document (frontmatter metadata, all sections, interaction timeline, and relationship links) followed by any memories found. Group memories by category (communication preferences, relationship context, deal context, company intelligence) for readability.

## When nothing is found

If `search_records` returns no results:
- Try `search_documents` with `mode: "semantic"` and a broader query (the record may exist but you might have the name slightly wrong)
- Suggest alternative spellings or name variations
- Ask the user if the entity might be filed under a different name
- Let them know they can add it using `add_contact` or `add_business` if it doesn't exist

## Notes

- For finding all contacts at a company, Mode 2 (relationship traversal via `get_doc_outline`) is more reliable than searching contact records by company name — company associations are stored as links in vault documents, not as a column in the contacts table.
- Use Mode 1 for bulk queries (all contacts with `#stage/qualified`, everyone with `last_interaction` before a date), Mode 2 for relationship questions, and Mode 3 when the user wants to read a full profile.
