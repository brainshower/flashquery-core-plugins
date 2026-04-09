---
name: plugin-creator
description: >
  Assemble a collection of skills, commands, MCP servers, agents, and hooks into a
  properly structured, installable Claude plugin (.plugin file). Use this skill whenever
  the user wants to package existing components into a plugin, bundle related skills
  together for sharing or distribution, convert standalone .claude/ configurations into a
  plugin, or create a plugin from a mix of inputs (skill folders, MCP configs, command
  files, agent definitions). Also trigger when the user says "create a plugin", "package
  my skills into a plugin", "bundle these into a plugin", "make a plugin from these",
  "I want to distribute my skills as a plugin", or when they hand you a set of components
  and ask you to wire them together. Even casual phrasing like "turn this into a plugin"
  or "I have some skills I want to share" should trigger this skill.
---

# Plugin Creator

Assemble a complete, installable Claude plugin from a set of supplied components. By the
end of this skill the user will have a `.plugin` file they can install in Claude Code,
Cowork, or any compatible Claude desktop environment.

> This skill is about **assembly and packaging** — not building components from scratch.
> You take what the user already has (or describes) and wire it into the proper structure.
> If the user needs help creating individual skills from scratch first, pause and do that,
> then come back here to package them.

## Overview

A Claude plugin is a zip file with a `.plugin` extension. It unpacks into a directory with
this layout:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json        ← required manifest
├── skills/                ← agent skills (auto-invoked by Claude)
│   └── skill-name/
│       └── SKILL.md
├── commands/              ← slash commands (user-invoked)
│   └── command-name.md
├── agents/                ← subagent definitions
│   └── agent-name.md
├── hooks/                 ← event hooks
│   └── hooks.json
├── .mcp.json              ← MCP server configs
├── settings.json          ← optional default settings (e.g. default agent)
└── README.md
```

Only create the directories that are actually needed. An empty `commands/` folder is
noise — leave it out.

See `references/plugin-structure.md` for the full manifest schema and component rules.
See `references/component-schemas.md` for detailed format specs for each component type.

---

## Workflow

Work through these phases in order, but stay flexible — if the user has already answered
a phase's questions in their initial request, skip ahead.

### Phase 1 — Inventory what you have

Understand what components exist and what still needs to be created. Ask only what you
don't already know:

- What skills, commands, MCPs, agents, or hooks do they want to include?
- Do the component files already exist on disk, or will you need to create them?
- For any existing files: where are they located? (Ask to read them, or have the user
  confirm the paths.)
- Is anything missing that the plugin clearly needs?

Read every existing component file before proceeding. You need to understand what's
there to make good decisions about the manifest and structure.

**Output of this phase**: A clear list of every component going into the plugin, with a
status of "exists" or "needs to be created."

### Phase 2 — Design the plugin manifest

Gather the metadata for `plugin.json`. If the user hasn't specified these, make
reasonable suggestions based on what the components do and ask for confirmation:

| Field | Notes |
|-------|-------|
| `name` | Kebab-case, becomes the skill namespace prefix (e.g., `code-tools` → `/code-tools:review`) |
| `description` | One sentence explaining what the plugin does |
| `version` | Start at `0.1.0` for new plugins. For updates to existing plugins, read the current `plugin.json` and suggest the appropriate bump: PATCH for fixes, MINOR for new features, MAJOR for breaking changes. |
| `author.name` | Who built it |
| `keywords` | Optional but useful for discoverability |

**Name rules**: lowercase, hyphens only, no spaces or special characters.

Confirm the manifest with the user before building.

### Phase 3 — Assemble the plugin

Create the plugin directory in `/tmp/` and populate it:

1. Create `<plugin-name>/.claude-plugin/plugin.json`
2. For each component:
   - **Existing files**: Copy them into the correct location in the plugin tree.
   - **Components to create**: Author them now, following the schemas in
     `references/component-schemas.md`.
3. If the plugin includes an agent that should be active by default, create
   `settings.json` at the plugin root with `{ "agent": "agent-name" }`. See
   `references/plugin-structure.md` for details. Only create this file if a default
   agent is actually needed — most plugins don't need it.
4. Create a `README.md` documenting the plugin's purpose and components.

**Directory placement rules** (these trip people up):
- `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json`, and `settings.json` go at
  the **plugin root**, NOT inside `.claude-plugin/`
- `.claude-plugin/` contains ONLY `plugin.json`
- Skill folders nest one level deep: `skills/skill-name/SKILL.md`
- Use `${CLAUDE_PLUGIN_ROOT}` for any intra-plugin path references in hooks/MCP configs

**Skill adaptation**: When copying an existing standalone skill into a plugin, the skill's
content and `SKILL.md` body stay exactly the same. The only thing that changes is the
namespace — a standalone skill `/my-skill` becomes `/plugin-name:my-skill` after
installation. No content edits needed unless the skill internally references its own path.

**MCP adaptation**: If the user has an existing `.mcp.json`, copy it to the plugin root.
Replace any hardcoded absolute paths with `${CLAUDE_PLUGIN_ROOT}/...`.

### Phase 4 — Validate and Lint

Do a comprehensive structure check, then lint skills for common issues.

**Structure validation:**

```bash
# Confirm required files exist
ls <plugin-dir>/.claude-plugin/plugin.json

# Check no component directories are inside .claude-plugin/
ls <plugin-dir>/.claude-plugin/  # should only show plugin.json

# Confirm each skill has SKILL.md
for d in <plugin-dir>/skills/*/; do ls "$d/SKILL.md"; done

# Check plugin.json is valid JSON
python3 -c "import json; json.load(open('<plugin-dir>/.claude-plugin/plugin.json'))"
```

**Skill linting:**

After structure validation passes, lint each skill file using Python:

```python
import os
import re

PLUGIN_DIR = "<plugin-dir>"
LINTS = []

# Check 1: #status tag misuse (should use "status" frontmatter property instead)
skills_dir = os.path.join(PLUGIN_DIR, "skills")
if os.path.exists(skills_dir):
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
        if os.path.exists(skill_path):
            with open(skill_path) as f:
                content = f.read()
            
            # Look for #status tag usage in the body (after frontmatter)
            # Pattern: find #status/ tags anywhere in the skill content
            if re.search(r'#status/\w+', content):
                LINTS.append({
                    "skill": skill_name,
                    "issue": "#status tag found",
                    "details": "Skills should not use #status tags. Use the 'status' frontmatter property instead to set document status (e.g., status: draft)",
                    "severity": "warning"
                })

# Report linting results
if LINTS:
    print("⚠️ LINTING WARNINGS:\n")
    for lint in LINTS:
        print(f"  {lint['skill']}: {lint['issue']}")
        print(f"    → {lint['details']}\n")
else:
    print("✓ All linting checks passed.")
```

Fix any warnings or errors before proceeding. Warnings may be ignored with user confirmation, but errors must be fixed.

### Phase 5 — Package and deliver

Create the `.plugin` file and copy the plugin folder to the output directory using the built-in packager.

**Output directory**: Default to `flashquery-core/plugins/` inside the user's workspace folder (under flashquery-core-plugins). Resolve the actual absolute path at runtime. If the path is ambiguous or doesn't exist, ask before writing.

Both outputs go into this directory:
- `<plugin-name>.plugin` — the installable zip archive
- `<plugin-name>/` — the unpacked plugin folder (used by the marketplace manifest as the source)

**Integrated Python packager** (no external build script needed):

```python
import os
import json
import zipfile
import shutil

PLUGIN_NAME = "<plugin-name>"
PLUGIN_DIR = os.path.join(os.getcwd(), "<plugin-relative-path>", PLUGIN_NAME)
OUTPUT_DIR = os.path.join(os.getcwd(), "<output-dir>")  # resolve at runtime
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{PLUGIN_NAME}.plugin")

# Validate before building
manifest_path = os.path.join(PLUGIN_DIR, ".claude-plugin", "plugin.json")
if not os.path.exists(manifest_path):
    raise FileNotFoundError(f"Missing {manifest_path}")

with open(manifest_path) as f:
    manifest = json.load(f)
    if not all(k in manifest for k in ["name", "version", "description"]):
        raise ValueError("plugin.json missing required fields")

# Package: create .plugin file (zip)
with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PLUGIN_DIR):
        # Skip excluded patterns
        dirs[:] = [d for d in dirs if d not in ["__pycache__", "evals", ".DS_Store"]]
        for file in files:
            if file == ".DS_Store":
                continue
            filepath = os.path.join(root, file)
            # Archive name: relative to parent of PLUGIN_DIR
            arcname = os.path.relpath(filepath, os.path.dirname(PLUGIN_DIR))
            zf.write(filepath, arcname)

print(f"✓ {PLUGIN_NAME}.plugin created ({os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB)")

# Copy plugin folder to output (clean replace, not merge)
output_folder = os.path.join(OUTPUT_DIR, PLUGIN_NAME)
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
shutil.copytree(PLUGIN_DIR, output_folder)

print(f"✓ {PLUGIN_NAME}/ folder copied to output")
```

This packager is built directly into the workflow — no external `build_plugin.py` script needed. Both the `.plugin` file and folder are ready for distribution or marketplace integration.

### Phase 6 — Sync versions and update the marketplace manifest

`plugin.json` is the single source of truth for the version. Before the plugin is
considered ready to ship, the version must be consistent everywhere it appears.

**Step 1 — Propagate the version**

Read the `version` field from `.claude-plugin/plugin.json`. Then check and update
every other location where a version string appears:

| Location | Field | Action |
|----------|-------|--------|
| `.claude-plugin/plugin.json` | `"version"` | Source of truth — do not change here |
| `README.md` frontmatter | `version:` | Update to match `plugin.json` |
| `.claude-plugin/marketplace.json` entry | `"version"` | Update to match `plugin.json` |

If `README.md` doesn't have a `version` in its frontmatter, add one. If other files
reference a version string (e.g., a changelog heading, an install command in the docs),
update those too.

**Step 2 — Update `marketplace.json`**

The manifest is at `<workspace>/flashquery-core/.claude-plugin/marketplace.json`.
Add or update the entry for this plugin (match on `name`):

```json
{
  "name": "<plugin-name>",
  "description": "<one-sentence description from plugin.json>",
  "version": "<version — must match plugin.json exactly>",
  "source": "./flashquery-core/plugins/<plugin-name>"
}
```

The `source` path is relative to the repo root and follows the pattern
`./flashquery-core/plugins/<plugin-name>`.

**Step 3 — Verify consistency**

After writing all files, do a quick cross-check:

```bash
PLUGIN_DIR="<output-dir>/<plugin-name>"
VERSION_PLUGIN=$(python3 -c "import json; print(json.load(open('${PLUGIN_DIR}/.claude-plugin/plugin.json'))['version'])")
VERSION_README=$(grep -m1 '^version:' "${PLUGIN_DIR}/README.md" | awk '{print $2}')
VERSION_MARKET=$(python3 -c "import json; d=json.load(open('<workspace>/flashquery-core/.claude-plugin/marketplace.json')); print(next(p['version'] for p in d['plugins'] if p['name']=='<plugin-name>'))")

echo "plugin.json:      $VERSION_PLUGIN"
echo "README.md:        $VERSION_README"
echo "marketplace.json: $VERSION_MARKET"
```

If any version differs, fix it before delivering.

After all three steps are complete, present the `.plugin` file with a `computer://`
link and give the user a brief summary of what's inside and what changed.

---

## Linting Rules

The plugin-creator automatically lints all skills during Phase 4 validation. These checks catch common issues early:

### Rule: No #status tags in skill instructions

**What it checks**: Skills should never use `#status/` tags in their instructions or guidance. The `status` property is a frontmatter field for markdown documents, not a tag.

**Why**: Tags are user-facing organizational vocabulary. System properties like document status belong in frontmatter, not in tags. Mixing them confuses the distinction between user-managed tags and system properties.

**What to fix**: If a skill mentions "#status/draft" or similar, replace it with guidance to use the frontmatter `status: draft` property instead. Example:

❌ Bad: "Tag the document with #status/draft to mark it as incomplete"
✓ Good: "Set the frontmatter status field to 'draft' to mark it as incomplete"

**Trigger**: The linter searches all skill SKILL.md files for the pattern `#status/` anywhere in the content (excluding the skill metadata frontmatter itself — that's fine).

More linting rules may be added in future versions. The linter is extensible and designed to grow as plugin patterns mature.

---

## Common Patterns

### Bundling an existing standalone `.claude/skills/` directory

The user has skills in `.claude/skills/` and wants to share them as a plugin:

1. Read each `SKILL.md` to understand the skills
2. Design the manifest (the plugin `name` becomes the namespace prefix for all skills)
3. Copy the skill directories into `plugin-name/skills/`
4. If there are commands in `.claude/commands/`, copy those to `plugin-name/commands/`
5. Package

### Adding an MCP to a skill plugin

When a plugin bundles both skills and an MCP server:

1. Include the MCP config in `.mcp.json` at the plugin root
2. In the skills that use the MCP, update tool references to use the plugin-namespaced
   MCP tool name: `mcp__<server-name>__<tool>` (the server name comes from `.mcp.json`)
3. Document required environment variables in `README.md`

### Creating new skills on the fly

If the user says "I want a skill that does X" and it doesn't exist yet, pause and author
the `SKILL.md` following the conventions in `references/component-schemas.md`, then
include it in the plugin assembly. Don't guess at skill content — ask what the skill
should do and how it should be triggered.

---

## Quality Checklist

Before delivering, confirm:

- [ ] `plugin.json` has `name`, `description`, `version`
- [ ] Plugin `name` is kebab-case with no spaces
- [ ] No component directories are nested inside `.claude-plugin/`
- [ ] Each skill has a `name` and `description` in its SKILL.md frontmatter
- [ ] Each command describes what Claude should DO, written as directives (not docs)
- [ ] MCP configs use `${CLAUDE_PLUGIN_ROOT}` for local paths, not hardcoded paths
- [ ] `settings.json` is present only if a default agent is intentionally configured
- [ ] `README.md` explains what the plugin does and lists components
- [ ] The `.plugin` zip file opens cleanly (the top-level entry is the plugin folder)
- [ ] Both the `.plugin` file and the plugin folder are present in `flashquery-core/flashquery-core/plugins/`
- [ ] Version is consistent across `plugin.json`, `README.md` frontmatter, and `marketplace.json` (verified programmatically in Phase 6)
- [ ] `marketplace.json` entry has correct `name`, `description`, `version`, and `source` path

---

## Additional Resources

- **`references/plugin-structure.md`** — Full manifest schema, all optional fields,
  versioning, hooks structure, `.mcp.json` format
- **`references/component-schemas.md`** — Detailed format specs for every component
  type with annotated examples
