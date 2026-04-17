---
name: menu
description: >
  Use this skill when the user asks what the Product Brain can do, wants
  to see available skills, or needs help figuring out where to start.
  Trigger on "what can the product brain do", "show me the menu",
  "help", "what skills are available", "what are my options", "how do I
  use this", "where do I start", or any request for an overview of
  Product Brain capabilities. Also trigger right after Init when the
  vault is fresh and the user needs orientation, or when the user seems
  unsure what to do next. Even casual asks like "what now?" or "what
  else can you do?" in a Product Brain context should trigger this skill.
  This is not a static help page — it reflects the current state of the
  vault and suggests the most useful next action.
---

# Menu

Shows what the Product Brain can do right now, in plain language. Not a static help page — the menu is contextually aware and suggests the most useful starting point based on what's in the vault.

## Steps

### 1. Check vault state

Call `search_memory` with:
- `query`: `"product-brain-config"`
- `tags`: `["product-brain-config"]`

If no configuration is found, the Product Brain hasn't been initialized. Tell the user and offer to run **Init**.

If configuration exists, gather current state:

a. Call `search_records` on `projects` to list active projects.

b. Call `list_files` on the inbox path to count pending items.

c. Call `search_records` on `documents` with `filters: { "status": "active" }` and `limit: 1` to check whether any content exists yet.

### 2. Present available skills

Present the skills in natural language, grouped by what the user might want to do. Highlight what's most relevant based on the vault state.

**Capture something:**
- **Capture** — save a thought, observation, link, bug, task, or idea. Say it and it's filed.

**Get oriented:**
- **Orient** — morning brief: where you left off, what's in the inbox, what needs attention.
- **Close** — end-of-day wrap-up: log what got done, capture discoveries, set up tomorrow.

**Find and understand:**
- **Retrieve** — search the vault. "What do we know about X?" "What have users said about Y?"
- **Brief** — synthesized summary of a topic, feature, or milestone. Traces the full lineage.

**Build and define:**
- **Draft** — turn accumulated research into a feature spec. The handoff artifact for development.
- **Update** — change a document's status (resolved, shipped, archived).

**Maintain and organize:**
- **Review Loop** — process what's accumulated: route inbox items, do cursory research, surface connections.
- **Organize** — thorough cleanup pass: route misplaced items, consolidate, archive stale content.

**Manage projects:**
- **Add Project** — create a new project, list projects, switch active project, archive a project.

### 3. Suggest a starting point

Based on the vault state, suggest the most natural thing to do right now:

- **No projects yet** → "Start with Add Project to set up your first product."
- **Empty vault** → "Try Capture to add your first thought or observation."
- **Items in the inbox** → "You have N items in the inbox — Review Loop can process them, or you can Capture more."
- **Active research** → "You have open research threads — Orient can brief you on where things stand."
- **General orientation needed** → "Orient gives you a quick overview of where things are."

One suggestion, not a list of options. The user can always ask for something different.

## Notes

- Menu is read-only — it doesn't modify anything.
- The `plugin_id` for all tool calls is `"product-brain"`.
- Keep the presentation conversational. The user is asking "what can you do?" — answer like a person would, not like a man page.
