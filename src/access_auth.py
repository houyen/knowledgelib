#!/usr/bin/env python3
"""
Cloudflare Access JWT guard (ASGI middleware), lớp bảo vệ thứ hai sau Access.

Bật khi có CF_ACCESS_TEAM và CF_ACCESS_AUD (aud có thể nhiều giá trị, phân tách bằng dấu phẩy).
Mỗi request phải có header Cf-Access-Jwt-Assertion: JWT RS256 ký bởi khoá trong
https://<team>.cloudflareaccess.com/cdn-cgi/access/certs, đúng `iss` và `aud`, chưa hết hạn.
Không bật thì không làm gì (hành vi cũ). /healthz chỉ cho localhost.
"""

import json
import os
import threading
import time
import urllib.request

import jwt
from jwt.algorithms import RSAAlgorithm

JWT_HEADER = "cf-access-jwt-assertion"
JWKS_TTL = 3600
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}


class AccessVerifier:
    def __init__(self, team: str, audiences: list, jwks_fetcher=None):
        self.team = team
        self.audiences = audiences
        self.issuer = f"https://{team}.cloudflareaccess.com"
        self._fetch = jwks_fetcher or self._fetch_remote
        self._keys = {}
        self._fetched_at = 0.0
        self._lock = threading.Lock()

    def _fetch_remote(self) -> dict:
        with urllib.request.urlopen(f"{self.issuer}/cdn-cgi/access/certs", timeout=5) as r:
            return json.load(r)

    def _refresh(self) -> None:
        data = self._fetch()
        self._keys = {k["kid"]: RSAAlgorithm.from_jwk(json.dumps(k)) for k in data.get("keys", []) if k.get("kid")}
        self._fetched_at = time.time()

    def _key_for(self, kid: str):
        with self._lock:
            stale = time.time() - self._fetched_at > JWKS_TTL
            if stale or kid not in self._keys:
                # Kid lạ: thử nạp lại một lần (xoay khoá), nhưng không quá 1 lần/phút để khỏi bị spam.
                if stale or time.time() - self._fetched_at > 60:
                    self._refresh()
            return self._keys.get(kid)

    def verify(self, token: str) -> dict:
        kid = jwt.get_unverified_header(token).get("kid")
        key = self._key_for(kid)
        if key is None:
            raise jwt.InvalidTokenError("unknown kid")
        return jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience=self.audiences,
            issuer=self.issuer,
            options={"require": ["exp", "iss", "aud"]},
        )


def verifier_from_env():
    """AccessVerifier nếu env bật, không thì None."""
    team = os.environ.get("CF_ACCESS_TEAM", "").strip()
    aud = [a.strip() for a in os.environ.get("CF_ACCESS_AUD", "").split(",") if a.strip()]
    if not team or not aud:
        return None
    return AccessVerifier(team, aud)


class AccessMiddleware:
    def __init__(self, app, verifier=None):
        self.app = app
        self.verifier = verifier if verifier is not None else verifier_from_env()

    async def _deny(self, send, status: int, text: str):
        body = text.encode()
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"text/plain"), (b"content-length", str(len(body)).encode())]})
        await send({"type": "http.response.body", "body": body})

    async def __call__(self, scope, receive, send):
        if self.verifier is None or scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)
        if scope["type"] == "websocket":
            return await send({"type": "websocket.close", "code": 1008})

        client_host = (scope.get("client") or ("", 0))[0]
        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        if scope.get("path") == "/healthz":
            # Chỉ localhost, và không được đi qua tunnel (tunnel luôn kèm header cf-*).
            if client_host in LOCAL_HOSTS and "cf-connecting-ip" not in headers:
                return await self._deny(send, 200, "ok")
            return await self._deny(send, 403, "forbidden")

        token = headers.get(JWT_HEADER)
        if not token:
            return await self._deny(send, 401, "missing access token")
        try:
            self.verifier.verify(token)
        except Exception:  # InvalidTokenError, lỗi mạng khi nạp JWKS... đều từ chối
            return await self._deny(send, 401, "invalid access token")
        return await self.app(scope, receive, send)
