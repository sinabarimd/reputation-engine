#!/usr/bin/env python3
"""
sync_pending_actions.py — Phase 1: one-way dashboard -> pending_actions.md sync.

Fetches /webhook/daily-todos and reconciles the Auto-Synced section of
pending_actions.md. Lines with <!-- todo_id: X --> markers are managed
by this script; all other lines are left untouched.

Usage:
    python3 scripts/sync_pending_actions.py [--dry-run]

Requires: N8N_BASE_URL environment variable.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import date

PENDING_ACTIONS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pending_actions.md",
)

AUTO_SECTION_HEADER = "## Auto-Synced Daily Todos"
AUTO_SECTION_COMMENT = (
    "<!-- This section is managed by sync_pending_actions.py. "
    "Do not edit lines with todo_id markers; they will be reconciled on next sync. -->"
)
OPERATOR_SECTION = "## Operator Action Required"
COMPLETED_SECTION = "## Completed"
TODO_ID_RE = re.compile(r"<!--\s*todo_id:\s*(.+?)\s*-->")


def fetch_todos():
    base = os.environ.get("N8N_BASE_URL")
    if not base:
        print("ERROR: N8N_BASE_URL not set", file=sys.stderr)
        sys.exit(1)

    url = f"{base}/webhook/daily-todos"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: failed to fetch {url}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict) or "todos" not in data:
        print(f"ERROR: malformed response from {url}", file=sys.stderr)
        sys.exit(1)

    return data["todos"]


def parse_file(path):
    if not os.path.exists(path):
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return f.readlines()


def find_tracked_todos(lines):
    """Return {todo_id: line_index} for all lines with a todo_id marker."""
    tracked = {}
    for i, line in enumerate(lines):
        m = TODO_ID_RE.search(line)
        if m:
            tid = m.group(1)
            if tid not in tracked:
                tracked[tid] = i
            else:
                # Duplicate — record for cleanup
                tracked.setdefault("__dupes__", []).append(i)
    return tracked


def find_section_index(lines, header):
    """Return the line index of a section header, or -1."""
    for i, line in enumerate(lines):
        if line.strip().startswith(header):
            return i
    return -1


def run(dry_run=False):
    todos = fetch_todos()
    api_ids = {t["todo_id"] for t in todos}
    api_by_id = {t["todo_id"]: t for t in todos}

    lines = parse_file(PENDING_ACTIONS)
    tracked = find_tracked_todos(lines)
    dupe_indices = tracked.pop("__dupes__", [])
    file_ids = set(tracked.keys())

    to_add = api_ids - file_ids
    to_complete = file_ids - api_ids
    unchanged = file_ids & api_ids

    today = date.today().isoformat()

    # --- Remove duplicates (keep first, mark rest for deletion) ---
    remove_indices = set(dupe_indices)

    # --- Mark completed ---
    completed_lines = []
    for tid in to_complete:
        idx = tracked[tid]
        old_line = lines[idx]
        new_line = old_line.replace("- [ ]", "- [x]", 1)
        if "- [x]" not in new_line:
            new_line = "- [x]" + new_line.lstrip("- [] ")
        completed_lines.append(new_line.rstrip("\n") + "\n")
        remove_indices.add(idx)

    # --- Build new lines to add ---
    add_lines = []
    for tid in sorted(to_add):
        t = api_by_id[tid]
        add_lines.append(
            f"- [ ] {today} | {t['label']} <!-- todo_id: {tid} -->\n"
        )

    # --- Rebuild file ---
    # Remove marked lines
    new_lines = [line for i, line in enumerate(lines) if i not in remove_indices]

    # Ensure Auto-Synced section exists
    auto_idx = find_section_index(new_lines, AUTO_SECTION_HEADER)
    if auto_idx == -1:
        # Insert before Operator Action Required
        op_idx = find_section_index(new_lines, OPERATOR_SECTION)
        if op_idx == -1:
            # Fallback: insert before Completed
            op_idx = find_section_index(new_lines, COMPLETED_SECTION)
        if op_idx == -1:
            op_idx = len(new_lines)

        insert_block = [
            f"\n{AUTO_SECTION_HEADER}\n",
            f"{AUTO_SECTION_COMMENT}\n",
            "\n",
        ]
        for il in reversed(insert_block):
            new_lines.insert(op_idx, il)
        auto_idx = op_idx

    # Find insertion point: right after the section header + comment
    insert_at = auto_idx + 1
    while insert_at < len(new_lines) and (
        new_lines[insert_at].strip().startswith("<!--")
        or new_lines[insert_at].strip() == ""
    ):
        insert_at += 1

    # Insert new lines
    for al in reversed(add_lines):
        new_lines.insert(insert_at, al)

    # Move completed lines to top of Completed section
    if completed_lines:
        comp_idx = find_section_index(new_lines, COMPLETED_SECTION)
        if comp_idx != -1:
            insert_comp = comp_idx + 1
            for cl in reversed(completed_lines):
                new_lines.insert(insert_comp, cl)

    # --- Write ---
    if dry_run:
        print(f"DRY RUN: {len(to_add)} to add, {len(to_complete)} to complete, {len(unchanged)} unchanged")
        if to_add:
            print("  ADD:", ", ".join(sorted(to_add)))
        if to_complete:
            print("  COMPLETE:", ", ".join(sorted(to_complete)))
    else:
        with open(PENDING_ACTIONS, "w") as f:
            f.writelines(new_lines)
        print(f"synced: {len(to_add)} added, {len(to_complete)} completed, {len(unchanged)} unchanged")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
