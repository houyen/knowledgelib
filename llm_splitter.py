#!/usr/bin/env python3
"""
LLM-Assisted Document Splitter for KnowledgeLib.
Uses Gemini Developer API to intelligently segment unstructured text into Knowledge Units.
Falls back safely to regex splitting if API key is not configured or calls fail.
"""

import json
import os
import re

MAX_CHARS_PER_BATCH = 35000


def _clean_json_text(text: str) -> str:
    """Strip markdown code fences and extraneous whitespace."""
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    return raw


def _split_batch_with_llm(text: str, doc_name: str, api_key: str) -> list[dict] | None:
    """Call Gemini API on a batch of text to extract units as JSON."""
    try:
        from google import genai
    except ImportError:
        return None

    prompt = (
        f"You are an expert knowledge engineering document splitter.\n"
        f"Analyze the following text from document '{doc_name}' and split it into logical Knowledge Units "
        f"(e.g. chapters, sections, or distinct topics).\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. Preserve the original text verbatim for each unit's 'content'. Do NOT summarize, rewrite, or paraphrase.\n"
        f"2. Return ONLY a valid JSON array of objects. Do not wrap in markdown code blocks or add explanatory text.\n"
        f"3. Each object must have exactly two non-empty string fields:\n"
        f"   - \"title\": concise, descriptive title or heading of the section\n"
        f"   - \"content\": the full verbatim text belonging to this section\n\n"
        f"Text to split:\n{text}"
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if not response or not response.text:
            return None

        cleaned = _clean_json_text(response.text)
        data = json.loads(cleaned)
        if not isinstance(data, list):
            return None

        valid_units = []
        for item in data:
            if not isinstance(item, dict):
                continue
            title = item.get("title")
            content = item.get("content")
            if isinstance(title, str) and title.strip() and isinstance(content, str) and content.strip():
                valid_units.append({
                    "title": title.strip(),
                    "content": content.strip(),
                })

        return valid_units if valid_units else None
    except Exception:
        return None


def split_text_with_llm(
    pages: list[tuple[int, str]],
    doc_name: str,
    api_key: str | None = None,
) -> list[dict] | None:
    """
    Split document pages into Knowledge Units using Gemini Developer API.
    Returns list[{"num": str, "title": str, "content": str}] or None.
    Never raises an exception -- returns None on any failure so caller can safely fallback to regex.
    """
    if not pages:
        return None

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None

    # Group pages into batches if total text is large
    batches: list[str] = []
    current_batch: list[str] = []
    current_len = 0

    for _, page_text in pages:
        p_len = len(page_text)
        if current_batch and (current_len + p_len > MAX_CHARS_PER_BATCH):
            batches.append("\n\n".join(current_batch))
            current_batch = [page_text]
            current_len = p_len
        else:
            current_batch.append(page_text)
            current_len += p_len

    if current_batch:
        batches.append("\n\n".join(current_batch))

    all_units = []
    for batch_text in batches:
        units = _split_batch_with_llm(batch_text, doc_name, key)
        if not units:
            return None
        all_units.extend(units)

    if not all_units:
        return None

    # Assign sequential 2-digit numbers
    for idx, u in enumerate(all_units, start=1):
        u["num"] = f"{idx:02d}"

    return all_units
