---
title: "{{name}}"
fqc_id: "{{fqc_id}}"
status: active
tags:
  - "#status/active"
created: "{{created}}"
updated: "{{updated}}"
---

# Company Information

<!-- Basic identifying information: website, LinkedIn, location, size, and any other factual details. Keep factual and brief — deeper narrative belongs in "What They Do" below. Industry is expressed as a tag (#industry/energy) rather than a field, consistent with P-02. -->

# What They Do

<!-- A concise description of the company's business, products, services, and market focus. Write this in plain prose — the AI reads this section when preparing briefings. Update it as your understanding of their business evolves. -->

# Key Contacts

<!-- All contacts at this company appear here as [[wikilinks]], added via insert_in_doc (add_contact skill). Example: [[Sarah Chen]], [[Marcus Webb]]. get_doc_outline reads this section to traverse the company→contact relationship without loading the full document. Never use tags like #company/acme-corp to link contacts — use wikilinks (P-03). -->

# Opportunities

<!-- Free-form notes about current or potential business opportunities with this company. Include deal stage, context, and any relevant history. This is the narrative layer — structured filtering happens via the businesses record and tags. -->

# Notes

<!-- General intelligence accumulated over time: market observations, org changes, competitive signals, news, relationship dynamics. This is the long-term memory of your company relationship. Volatile impressions (e.g. "heard their CEO is leaving") are better stored as memories (crm_memory skill) until confirmed. -->
