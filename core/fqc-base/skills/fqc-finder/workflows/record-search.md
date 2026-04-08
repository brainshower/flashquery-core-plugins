# Record Search Workflow

Use this workflow when the user wants to find structured data from a plugin — contacts, opportunities, or other plugin-defined records.

## When to use

- "Find the contact who mentioned competitor pricing"
- "Do I have a record for Acme?"
- "Find contacts at Acme Corp"
- Any query about structured data (contacts, deals, records) rather than free-form documents

## Important note

Core FQC skills can call `search_records` for general queries, but plugin-specific skills own the schema context needed to interpret record fields correctly. If a dedicated plugin skill is available (e.g., fqc-crm's `crm-intel`), prefer using it. Use this workflow when no plugin skill is available.

## Tool: `search_records`

```
search_records(
  plugin_id: "crm",            // required — the plugin ID
  table: "contacts",           // optional — narrow to a specific table
  query: "competitor pricing", // natural-language semantic query
  filters: { company: "Acme" }, // optional field filters
  mode: "semantic",            // "semantic" | "filter" | "mixed"
  limit: 10
)
```

| Mode | When to use |
|------|-------------|
| `"semantic"` | Natural-language query ("who talked about X?") |
| `"filter"` | Exact field matching ("find contacts at Acme Corp") |
| `"mixed"` | Both — semantic ranked first |

## Steps

1. Identify the plugin ID from context.
2. Formulate the search (semantic query, field filters, or both).
3. Call `search_records`. Review returned records.
4. If a record has an `fqc_id` field, call `get_document` to retrieve the linked vault document (e.g., meeting notes for that contact).
5. Synthesize and respond, linking to related documents where available.

## Example

**"Find the contact who mentioned competitor pricing"**
```
search_records(plugin_id: "crm", query: "competitor pricing", mode: "semantic")
```
If result includes `fqc_id: "a1b2c3..."`:
```
get_document(identifier: "a1b2c3-...")
```
→ "Found Sarah Chen at Acme Corp — she mentioned competitor pricing in your March 15 call. Meeting notes: `clients/acme/march-call.md`."
