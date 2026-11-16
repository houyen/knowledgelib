#!/usr/bin/env python3
"""
Extra search aliases kept outside the unit files.

Most units are English (synced from upstream), while questions often arrive in Vietnamese. Rather than
editing ~2,000 unit files, Vietnamese search phrases live in `config/aliases_vi.json`:

    {"<unit id>": ["cụm tìm kiếm", ...], ...}

They are merged into the unit's aliases wherever search text is built (BM25 index, embedding text).
Unit frontmatter and catalog.json stay untouched, so an upstream re-sync cannot wipe them.
"""

import json
import os

OVERLAY_RELATIVE_PATH = os.path.join("config", "aliases_vi.json")

_CACHE = {}


def load_extra_aliases(repo_dir: str) -> dict:
    """Return {unit_id: [aliases]}; empty when the overlay file is missing or unreadable."""
    path = os.path.join(repo_dir, OVERLAY_RELATIVE_PATH)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return {}
    cached = _CACHE.get(path)
    if cached and cached[0] == mtime:
        return cached[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return {}
    data = {
        str(uid): [str(a).strip() for a in aliases if str(a).strip()]
        for uid, aliases in raw.items()
        if isinstance(aliases, list)
    } if isinstance(raw, dict) else {}
    _CACHE[path] = (mtime, data)
    return data


def merged_aliases(unit: dict, extra: dict) -> list:
    """Unit's own aliases followed by overlay aliases, without duplicates (case-insensitive)."""
    out, seen = [], set()
    for alias in list(unit.get("aliases", []) or []) + list(extra.get(unit.get("id"), [])):
        text = str(alias)
        key = text.lower()
        if key not in seen:
            seen.add(key)
            out.append(text)
    return out
