#!/usr/bin/env python3
"""
KnowledgeLib MCP Server (stdio mặc định; streamable-http khi KNOWLEDGELIB_MCP_TRANSPORT=streamable-http).
Env: KNOWLEDGELIB_MCP_HOST (127.0.0.1), KNOWLEDGELIB_MCP_PORT (8001), KNOWLEDGELIB_READONLY=1
(không đăng ký ingest và get_memory_index), KNOWLEDGELIB_EXCLUDE_DOMAINS (xem agent_client),
CF_ACCESS_TEAM + CF_ACCESS_AUD (bật kiểm JWT Cloudflare Access, xem access_auth).
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


def _readonly() -> bool:
    return os.environ.get("KNOWLEDGELIB_READONLY", "").strip().lower() in ("1", "true", "yes", "on")

_CLIENT_CACHE = {"key": None, "client": None}


def _client() -> KnowledgeLibClient:
    """Reuse one client (catalog, BM25 index, embedding model) until catalog.json changes on disk."""
    path = os.path.join(
        os.environ.get("KNOWLEDGELIB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))),
        "catalog.json",
    )
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = None
    key = (KnowledgeLibClient, path, mtime)
    if _CLIENT_CACHE["key"] != key:
        _CLIENT_CACHE["client"] = KnowledgeLibClient()
        _CLIENT_CACHE["key"] = key
    return _CLIENT_CACHE["client"]


@mcp.tool()
def knowledgelib_search(query: str, top_k: int = 3) -> list[dict]:
    """Search KnowledgeLib (hybrid vector + keyword). Returns up to top_k matches with score/distance so the agent can pick among candidates, not just the top-1."""
    client = _client()
    results = client.search(query, top_k=top_k)
    if not results:
        log_miss(query, source="mcp_search")
    return results


@mcp.tool()
def knowledgelib_get_content(unit_id: str) -> str:
    """Read the full Markdown content of a KnowledgeLib unit by its id."""
    client = _client()
    return client.get_unit_content(unit_id)


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


def knowledgelib_get_memory_index(domain: str = "self-docs") -> str:
    """Get compact working memory snapshot of canonical self-docs, runbooks, and critical gotchas to load into agent context."""
    from memory_loader import get_memory_index

    return get_memory_index(domain=domain)


# Tool ghi/nội bộ chỉ đăng ký khi không ở chế độ chỉ đọc.
if not _readonly():
    mcp.tool()(knowledgelib_ingest)
    mcp.tool()(knowledgelib_get_memory_index)


def build_http_app():
    """ASGI app streamable-http, bọc middleware Access JWT (no-op nếu chưa cấu hình CF_ACCESS_*)."""
    from mcp.server.transport_security import TransportSecuritySettings

    from access_auth import AccessMiddleware

    host = os.environ.get("KNOWLEDGELIB_MCP_HOST", "127.0.0.1")
    # Host header qua tunnel là hostname công khai, không phải localhost: tắt chống DNS-rebinding
    # (chỉ bind localhost, truy cập duy nhất qua cloudflared + Access JWT).
    app = mcp.streamable_http_app(
        host=host,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    return AccessMiddleware(app)


if __name__ == "__main__":
    transport = os.environ.get("KNOWLEDGELIB_MCP_TRANSPORT", "stdio").strip().lower()
    if transport == "streamable-http":
        import uvicorn

        uvicorn.run(
            build_http_app(),
            host=os.environ.get("KNOWLEDGELIB_MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("KNOWLEDGELIB_MCP_PORT", "8001")),
        )
    else:
        mcp.run(transport="stdio")
