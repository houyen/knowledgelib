import asyncio
import importlib
import json
import os
import sys
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt.algorithms import RSAAlgorithm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from access_auth import AccessMiddleware, AccessVerifier  # noqa: E402

TEAM, AUD = "acme", "aud-123"
CATALOG = {
    "units": [
        {"id": "software/devops/pytest-configuration", "canonical_question": "How to configure pytest",
         "aliases": [], "domain": "software > devops", "entity_type": "book_chapter"},
        {"id": "self-docs/database/secret-runbook", "canonical_question": "How to configure pytest secret runbook",
         "aliases": [], "domain": "self-docs > database", "entity_type": "book_chapter"},
    ]
}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for rel, body in [("software/devops/pytest-configuration", "# pytest\n\nBody."),
                      ("self-docs/database/secret-runbook", "# secret\n\nPrivate.")]:
        f = tmp_path / f"{rel}.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body, encoding="utf-8")
    (tmp_path / "catalog.json").write_text(json.dumps(CATALOG), encoding="utf-8")
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))
    return tmp_path


def _client_mod():
    import agent_client
    return importlib.reload(agent_client)


# ---- exclude domains ----
def test_exclude_off_keeps_old_behaviour(repo):
    ids = {r["id"] for r in _client_mod().KnowledgeLibClient().search("pytest configure", top_k=5)}
    assert "self-docs/database/secret-runbook" in ids


def test_exclude_hides_from_search_and_content(repo, monkeypatch):
    monkeypatch.setenv("KNOWLEDGELIB_EXCLUDE_DOMAINS", "self-docs")
    c = _client_mod().KnowledgeLibClient()
    ids = {r["id"] for r in c.search("pytest configure secret", top_k=5)}
    assert ids == {"software/devops/pytest-configuration"}
    assert c.get_unit_content("self-docs/database/secret-runbook").startswith("Error: Unit file not found")
    assert c.get_unit_content("self-docs/../self-docs/database/secret-runbook").startswith("Error:")


def test_path_traversal_blocked(repo):
    out = _client_mod().KnowledgeLibClient().get_unit_content("../../etc/passwd")
    assert out.startswith("Error: Unit file not found")


def test_web_ui_excluded_unit_is_404(repo, monkeypatch):
    monkeypatch.setenv("KNOWLEDGELIB_EXCLUDE_DOMAINS", "self-docs")
    import web_ui
    importlib.reload(web_ui)
    tc = TestClient(web_ui.app)
    assert tc.get("/unit/self-docs/database/secret-runbook").status_code == 404
    assert tc.get("/unit/software/devops/pytest-configuration").status_code == 200


# ---- readonly ----
def _tool_names(monkeypatch, readonly):
    if readonly:
        monkeypatch.setenv("KNOWLEDGELIB_READONLY", "1")
    else:
        monkeypatch.delenv("KNOWLEDGELIB_READONLY", raising=False)
    _client_mod()
    import mcp_server
    importlib.reload(mcp_server)
    tools = asyncio.run(mcp_server.mcp.list_tools())
    return {t.name for t in (tools.tools if hasattr(tools, "tools") else tools)}


def test_readonly_hides_write_tools(repo, monkeypatch):
    assert _tool_names(monkeypatch, True) == {"knowledgelib_search", "knowledgelib_get_content"}


def test_default_keeps_all_tools(repo, monkeypatch):
    assert {"knowledgelib_ingest", "knowledgelib_get_memory_index"} <= _tool_names(monkeypatch, False)


# ---- access JWT ----
@pytest.fixture(scope="module")
def keys():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(RSAAlgorithm.to_jwk(priv.public_key()))
    jwk["kid"] = "k1"
    return priv, other, {"keys": [jwk]}


def _token(priv, aud=AUD, exp=3600, iss=f"https://{TEAM}.cloudflareaccess.com", kid="k1"):
    return jwt.encode({"aud": [aud], "iss": iss, "exp": int(time.time()) + exp, "email": "a@b.c"},
                      priv, algorithm="RS256", headers={"kid": kid})


def _app(keys):
    verifier = AccessVerifier(TEAM, [AUD], jwks_fetcher=lambda: keys[2])

    async def inner(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"hit"})

    return AccessMiddleware(inner, verifier=verifier)


def _call(app, path="/x", headers=None, client=("1.2.3.4", 1)):
    out = {}

    async def send(m):
        if m["type"] == "http.response.start":
            out["status"] = m["status"]

    scope = {"type": "http", "path": path, "client": client,
             "headers": [(k.encode(), v.encode()) for k, v in (headers or {}).items()]}
    asyncio.run(app(scope, None, send))
    return out["status"]


def test_valid_token_passes(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": _token(keys[0])}) == 200


def test_missing_token_401(keys):
    assert _call(_app(keys)) == 401


def test_expired_token_401(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": _token(keys[0], exp=-10)}) == 401


def test_wrong_aud_401(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": _token(keys[0], aud="other")}) == 401


def test_wrong_issuer_401(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": _token(keys[0], iss="https://evil.example")}) == 401


def test_wrong_signing_key_401(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": _token(keys[1])}) == 401


def test_garbage_token_401(keys):
    assert _call(_app(keys), headers={"Cf-Access-Jwt-Assertion": "not.a.jwt"}) == 401


def test_healthz_localhost_only(keys):
    app = _app(keys)
    assert _call(app, "/healthz", client=("127.0.0.1", 1)) == 200
    assert _call(app, "/healthz", client=("8.8.8.8", 1)) == 403
    assert _call(app, "/healthz", headers={"Cf-Connecting-Ip": "9.9.9.9"}, client=("127.0.0.1", 1)) == 403


def test_disabled_without_env(monkeypatch):
    monkeypatch.delenv("CF_ACCESS_TEAM", raising=False)
    monkeypatch.delenv("CF_ACCESS_AUD", raising=False)

    async def inner(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})

    assert _call(AccessMiddleware(inner)) == 200
