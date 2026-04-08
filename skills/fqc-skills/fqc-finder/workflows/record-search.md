# Record Search Workflow

Use this workflow when the user wants to find structured data from a plugin — contacts, opportunities, or other plugin-defined records.

## When to use

- "Find the contact who mentioned competitor pricing"
- "Do I have a record for Acme?"
- "Find contacts at Acme Corp"
- "Who did I talk to about the integration project?"
- Any query that sounds like it's about structured data (contacts, deals, records) rather than free-form documents

## Important note on plugin ownership

Core FQC skills (fqc-finder included) can call `search_records` for general queries, but plugin-specific skills own the schema context needed to interpret record fields correctly. If a dedicated plugin skill is available (e.g., fqc-crm's `crm-intel` or `find-entity`), prefer using it. Use this workflow when no plugin skill is available or when the user just wants a quick search.

## Tool: `search_records`

Plugin records are stored in plugin-defined tables. You'll need to know the plugin ID and, optionally, the table name.

```
search_records(
  plugin_id: "crm",            // required — the plugin ID
  table: "contacts",           // optional — narrow to a specific table; omit to search all tables
  query: "competitor pricing", // natural-language semantic query
  filters: { company: "Acme" }, // optional field filters
  mode: "semantic",            // "semantic" or "filter" or "mixed"
  limit: 10
)
```

### Search modes

| Mode | When to use |
|------|-------------|
| `"semantic"` | Natural-language query ("who talked about X?") |
| `"filter"` | Exact field matching ("find contacts at Acme Corp") |
| `"mixed"` | Both — semantic ranked first, filter results fill remaining slots |

## Steps

1. **Identify the plugin ID.** The user's context usually makes this clear (contacts → "crm", etc.). If unsure, ask.

2. **Formulate the search.** Decide between semantic query, field filters, or both.

3. **Call `search_records`.** Review the returned records.

4. **Follow up with linked documents.** If a record has an `fqc_id` field, call `get_document` with that ID to retrieve the linked vault document (e.g., the meeting notes for that contact).

5. **Synthesize and respond.** Present the relevant records clearly, linking to related documents where available.

## Example

**"Find the contact who mentioned competitor pricing"**

```
search_records(
  plugin_id: "crm",
  query: "competitor pricing",
  mode: "semantic"
)
```

If the result includes a contact record with `fqc_id: "a1b2c3..."`:
```
get_document(identifier: "a1b2c3-...")
```
→ "Found Sarah Chen at Acme Corp — she mentioned competitor pricing in your call on March 15. The linked meeting notes are at `clients/acme/march-call.md`."

## Fallback

If `search_records` returns an error about the plugin not being found, let the user know the plugin may not be registered and suggest they check with `get_plugin_info` or initialize the plugin.
