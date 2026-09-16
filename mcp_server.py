#!/usr/bin/env python3
"""
KnowledgeLib MCP Server (stdio).
Wraps KnowledgeLibClient (agent_client.py) and run_import (import_knowledge.py)
as MCP tools, so agents call them directly instead of shelling out to the CLI.
"""

from mcp.server.mcpserver import MCPServer

from agent_client import KnowledgeLibClient
from import_knowledge import run_import

mcp = MCPServer("knowledgelib")


@mcp.tool()
def knowledgelib_search(query: str, top_k: int = 3) -> list[dict]:
    """Search KnowledgeLib (hybrid vector + keyword). Returns up to top_k matches with score/distance so the agent can pick among candidates, not just the top-1."""
    client = KnowledgeLibClient()
    return client.search(query, top_k=top_k)


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
) -> dict:
    """Import a document (PDF/MD/TXT) into KnowledgeLib and re-index, or re-sync existing markdown files when sync_only=True."""
    return run_import(
        file_path,
        domain_path=domain_path,
        domain=domain,
        entity_type=entity_type,
        sync_only=sync_only,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
