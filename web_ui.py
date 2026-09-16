#!/usr/bin/env python3
"""
KnowledgeLib Local Web UI (FastAPI + HTMX).
No build step: HTMX loaded from CDN, Jinja2 server-rendered fragments.
Binds to 127.0.0.1 only — not meant to be exposed on the network.
"""

import os

import markdown as md
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agent_client import KnowledgeLibClient

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="KnowledgeLib")


def get_client() -> KnowledgeLibClient:
    # Re-instantiate per request instead of a module-level singleton so tests
    # can point KNOWLEDGELIB_PATH at a fixture repo and get it picked up.
    data_path = os.environ.get(
        "KNOWLEDGELIB_PATH", os.path.abspath(os.path.dirname(__file__))
    )
    return KnowledgeLibClient(data_path=data_path)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = Query(default=""), top_k: int = Query(default=5)):
    results = []
    if q.strip():
        results = get_client().search(q, top_k=top_k)
    return templates.TemplateResponse(
        request, "_results.html", {"query": q, "results": results}
    )


@app.get("/unit/{unit_id:path}", response_class=HTMLResponse)
def unit_detail(
    request: Request,
    unit_id: str,
    hx_request: str | None = Header(default=None, alias="HX-Request"),
):
    if unit_id.endswith(".md"):
        unit_id = unit_id[: -len(".md")]

    client = get_client()
    file_path = os.path.join(client.data_path, f"{unit_id}.md")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Unit not found: {unit_id}")

    raw_content = client.get_unit_content(unit_id)
    content_html = md.markdown(raw_content, extensions=["fenced_code", "tables"])

    context = {"unit_id": unit_id, "content_html": content_html}
    if hx_request == "true":
        return templates.TemplateResponse(request, "_unit_partial.html", context)
    return templates.TemplateResponse(request, "unit_page.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
