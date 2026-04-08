# CRM Tag Taxonomy

This file defines the native tag vocabulary for the CRM plugin. Skills reference this file when applying or interpreting tags on contacts, companies, and interactions.

Tags follow FQC Principle 2: they are bounded, user-meaningful categories — visible in Obsidian's tag pane, queryable via Supabase, and something the user would consciously choose. Tags are never used for system bookkeeping or cross-entity linking (use wikilinks for that — Principle 3).

## How tags are applied

Tags live in two places simultaneously: document frontmatter (visible in Obsidian) and the record's `tags` field in Supabase (queryable). The `apply_tags` MCP tool syncs both atomically — always use it rather than updating one side manually.

When the user's language implies a tag change, apply it. When the user explicitly names a tag or stage, apply it. When in doubt, confirm with the user before applying.

---

## Status tags

Applies to: **contacts, companies**

These are managed by FQC and should always be present on every entity.

| Tag | When to apply | User might say |
|-----|---------------|----------------|
| `#status/active` | Default on creation. Entity is current and relevant. | *(applied automatically)* |
| `#status/archived` | Entity is no longer active — left the company, business closed, relationship ended. | "Archive this contact", "we're done with them", "they went out of business" |

---

## Pipeline stage tags

Applies to: **contacts, companies**

These represent where an entity sits in your business development pipeline. Stages are sequential — when applying a new stage, remove the previous one. Only one `#stage/` tag should be active at a time per entity.

| Tag | When to apply | User might say |
|-----|---------------|----------------|
| `#stage/prospect` | Initial awareness. You know about them but haven't qualified the opportunity. | "New lead", "someone I should keep an eye on", "potential opportunity" |
| `#stage/qualified` | You've confirmed there's a real opportunity worth pursuing. | "This is real", "they have budget", "qualified lead", "worth pursuing" |
| `#stage/proposal` | You've sent or are preparing a proposal, SOW, or pitch. | "I sent the proposal", "pitching them next week", "SOW is out" |
| `#stage/negotiation` | Active deal discussion — pricing, terms, scope, timeline. | "We're negotiating", "discussing terms", "working out the contract" |
| `#stage/won` | Deal closed / won, they're a client. | "We won it", "deal closed", "they signed" |
| `#stage/lost` | Opportunity didn't materialize. Distinct from archived — the entity is still active, just not in the pipeline. | "We lost it", "they went with someone else", "deal fell through", "not happening" |
| `#stage/paused` | Opportunity is on hold — not dead, but not moving. | "On hold", "they're pausing", "pushed to next quarter", "back burner" |

---

## Relationship type tags

Applies to: **contacts**

Describes the nature of your relationship with a person. A contact may have multiple relationship tags (e.g., a former client who is now a referral partner).

| Tag | When to apply | User might say |
|-----|---------------|----------------|
| `#relationship/prospect` | Someone who could become a client or lead to business. | "Potential client", "could be a lead" |
| `#relationship/client` | Active paying client. | "They're a client", "we work with them" |
| `#relationship/former-client` | Was a client, engagement has ended. | "Used to be a client", "we worked with them last year" |
| `#relationship/partner` | Referral partner, collaborator, or strategic ally. | "Referral partner", "we collaborate", "sends us work" |
| `#relationship/vendor` | Someone who provides services to you. | "They're a vendor", "we buy from them" |
| `#relationship/advisor` | Mentor, advisor, or board member. | "My advisor", "on our advisory board" |
| `#relationship/peer` | Industry peer, fellow practitioner, community connection. | "Colleague", "peer", "met at a conference", "met while networking", "industry friend" |

---

## Industry tags

Applies to: **companies**

Describes the company's primary industry or sector. Apply based on what the company does, not what you do for them. Use the most specific tag that fits; avoid stacking multiple industry tags unless the company genuinely operates across sectors.

| Tag | Example user language |
|-----|----------------------|
| `#industry/technology` | "Tech company", "software", "SaaS" |
| `#industry/finance` | "Financial services", "fintech", "banking" |
| `#industry/healthcare` | "Healthcare", "medtech", "health system" |
| `#industry/energy` | "Energy company", "oil and gas", "renewables" |
| `#industry/retail` | "Retail", "e-commerce", "consumer goods" |
| `#industry/manufacturing` | "Manufacturing", "industrial" |
| `#industry/media` | "Media", "publishing", "entertainment" |
| `#industry/education` | "Education", "edtech", "university" |
| `#industry/real-estate` | "Real estate", "property", "development" |
| `#industry/nonprofit` | "Nonprofit", "NGO", "foundation" |
| `#industry/government` | "Government", "public sector" |
| `#industry/professional-services` | "Consulting", "agency", "law firm", "accounting" |

This list is intentionally broad. If the user's vocabulary calls for finer-grained industry tags (e.g., `#industry/biotech` instead of `#industry/healthcare`), create them — the convention is `#industry/<slug>` where the slug is always lowercase, hyphen-separated, and never contains whitespace (e.g., `real-estate` not `real estate`). This applies to all tag slugs across the CRM, not just industry. User-defined industry tags should be saved as a CRM preference memory so all skills recognize them going forward.

---

## Interaction type tags

Applies to: **interactions** (used by the `log-interaction` skill)

| Tag | When to apply | User might say |
|-----|---------------|----------------|
| `#interaction/meeting` | In-person meeting, coffee, lunch, on-site visit. | "Had a meeting", "grabbed coffee", "met with them" |
| `#interaction/call` | Phone call or video call. | "Had a call", "jumped on a Zoom", "phone call" |
| `#interaction/email` | Email exchange. | "Sent an email", "emailed them", "email thread" |
| `#interaction/message` | Chat message — Slack, text, LinkedIn DM. | "Messaged them", "sent a Slack", "DM'd them" |

---

## User-defined tags

The tags above are the CRM plugin's native vocabulary. Users may want to introduce additional tags specific to their workflow — for example, `#source/conference`, `#priority/vip`, or `#service/branding`.

When a user applies a tag that doesn't match the native taxonomy, the skill should:

1. Apply the tag as requested (don't block it — tags belong to the user, per P-02).
2. Save a CRM preference memory noting the custom tag and when the user intends it to be used. This ensures all skills recognize the tag in future conversations.

**Example:** If the user says "mark Sarah as VIP", apply `#priority/vip` and save a preference memory: "User uses #priority/vip to flag high-value contacts who should be surfaced prominently in briefings and follow-up lists."
