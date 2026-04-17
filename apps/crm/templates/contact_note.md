---
title: "{{name}}"
fqc_id: "{{fqc_id}}"
status: active
tags:
  - "#status/active"
created: "{{created}}"
updated: "{{updated}}"
---

# Contact Information

<!-- Add the contact's email, phone, job title, company, and any other identifying details here. This section is for factual "how to reach this person" data — keep it brief and current. Company association should also appear as a [[wikilink]] in the Relationship Context section below. -->

# Relationship Context

<!-- Describe how you know this person, the nature of the relationship, and any relevant background. Include [[wikilinks]] to associated companies or contacts (e.g. [[Acme Corp]], [[Jane Doe]]). The add_contact skill uses insert_in_doc to add wikilinks programmatically when creating or updating associations. -->

# Communication

<!-- Note communication preferences, response patterns, and any logistics to be aware of. This section informs the AI when drafting messages or scheduling follow-ups. Detailed impressions about timing and channel preferences are better stored as memories (crm_memory skill). -->

# Opportunities

<!-- Free-form notes about active or potential opportunities with this contact. Include deal stage, timeline, any relevant context. This is the human-readable narrative layer — structured queries happen via the contacts record and tags. -->

# Next Steps

<!-- Track concrete action items and follow-ups. Include dates where relevant. Format: YYYY-MM-DD — action description. The AI reads this section when preparing briefings (crm_intel skill). -->

# Interaction Timeline

<!-- Chronological record of all interactions. Entries are appended here via insert_in_doc (log_interaction skill). Each entry follows this format:

## YYYY-MM-DD
**Type:** meeting / call / email / message
**Summary:** What was discussed, key points, outcomes
**Action Items:** Any commitments or follow-ups from this interaction

Do not edit entries manually unless correcting a factual error — the log_interaction skill maintains this section. -->
