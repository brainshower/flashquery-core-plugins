#!/usr/bin/env python3
"""Build fqc-base.plugin from the fqc-base/ directory."""

import os
import json
import zipfile
import sys

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "fqc-base")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "fqc-base.plugin")

def validate():
    errors = []

    # Check plugin.json exists and is valid JSON
    manifest_path = os.path.join(PLUGIN_DIR, ".claude-plugin", "plugin.json")
    if not os.path.exists(manifest_path):
        errors.append(f"MISSING: {manifest_path}")
    else:
        with open(manifest_path) as f:
            try:
                manifest = json.load(f)
                required = ["name", "version", "description"]
                for field in required:
                    if field not in manifest:
                        errors.append(f"plugin.json missing required field: {field}")
                print(f"  plugin.json: OK (name={manifest.get('name')}, version={manifest.get('version')})")
            except json.JSONDecodeError as e:
                errors.append(f"plugin.json is invalid JSON: {e}")

    # Check no component dirs inside .claude-plugin/
    claude_plugin_dir = os.path.join(PLUGIN_DIR, ".claude-plugin")
    for item in os.listdir(claude_plugin_dir):
        if item != "plugin.json":
            errors.append(f".claude-plugin/ should only contain plugin.json, found: {item}")

    # Check each skill has SKILL.md
    skills_dir = os.path.join(PLUGIN_DIR, "skills")
    if os.path.exists(skills_dir):
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if os.path.isdir(skill_path):
                skill_md = os.path.join(skill_path, "SKILL.md")
                if not os.path.exists(skill_md):
                    errors.append(f"Skill '{skill_name}' missing SKILL.md")
                else:
                    print(f"  skill/{skill_name}/SKILL.md: OK")

    # Check commands exist
    commands_dir = os.path.join(PLUGIN_DIR, "commands")
    if os.path.exists(commands_dir):
        for cmd in os.listdir(commands_dir):
            print(f"  commands/{cmd}: OK")

    return errors

def build():
    print("\n=== Validating ===")
    errors = validate()
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print("  All checks passed.")

    print("\n=== Building plugin ===")
    file_count = 0
    with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PLUGIN_DIR):
            # Skip excluded patterns
            dirs[:] = [d for d in dirs if d not in ["__pycache__", "evals", ".DS_Store"]]
            for file in files:
                if file == ".DS_Store":
                    continue
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, os.path.dirname(PLUGIN_DIR))
                zf.write(filepath, arcname)
                file_count += 1
                print(f"  + {arcname}")

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"\nDone: fqc-base.plugin ({file_count} files, {size_kb:.1f} KB)")
    print(f"Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
