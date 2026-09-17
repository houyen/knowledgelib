#!/usr/bin/env python3
"""
KnowledgeLib MCP Server (stdio).
Wraps KnowledgeLibClient (agent_client.py) and run_import (import_knowledge.py)
as MCP tools, so agents call them directly instead of shelling out to the CLI.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from mcp.server.mcpserver import MCPServer

from agent_client import KnowledgeLibClient
from import_knowledge import run_import
from query_miss_log import log_miss

mcp = MCPServer("knowledgelib")


@mcp.tool()
def knowledgelib_search(query: str, top_k: int = 3) -> list[dict]:
    """Search KnowledgeLib (hybrid vector + keyword). Returns up to top_k matches with score/distance so the agent can pick among candidates, not just the top-1."""
    client = KnowledgeLibClient()
    results = client.search(query, top_k=top_k)
    if not results:
        log_miss(query, source="mcp_search")
    return results


@mcp.tool()
def knowledgelib_get_content(unit_id: str) -> str:
    """Read the full Markdown content of a KnowledgeLib unit by its id."""
    client = KnowledgeLibClient()
    return client.get_unit_content(unit_id)


@mcp.tool()
def knowledgelib_ingest(
    file_path: str | None = None,
    domain_path: str = "software/imported-books",
    domain: str = "software > imported_knowledge",
    entity_type: str = "book_chapter",
    sync_only: bool = False,
    use_llm_split: bool = True,
) -> dict:
    """Import a document (PDF/MD/TXT) into KnowledgeLib and re-index, or re-sync existing markdown files when sync_only=True. Uses LLM-assisted splitting by default with regex fallback."""
    return run_import(
        file_path,
        domain_path=domain_path,
        domain=domain,
        entity_type=entity_type,
        sync_only=sync_only,
        use_llm_split=use_llm_split,
    )


@mcp.tool()
def knowledgelib_get_memory_index(domain: str = "self-docs") -> str:
    """Get compact working memory snapshot of canonical self-docs, runbooks, and critical gotchas to load into agent context."""
    from memory_loader import get_memory_index

    return get_memory_index(domain=domain)


if __name__ == "__main__":
    mcp.run(transport="stdio")
