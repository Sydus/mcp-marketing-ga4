"""GA4 MCP server — Agent24 pattern (FastAPI + FastMCP streamable_http + _IdentityMiddleware)."""
from __future__ import annotations
import json as _json, os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from ga4_mcp.coordinator import mcp
from ga4_mcp.identity import resolve_credentials, _request_creds
from ga4_mcp.session import AlertMiddleware, SessionMiddleware
from ga4_mcp.tools import metadata, reporting

async def _asgi_json(send, body: dict, status: int) -> None:
    data = _json.dumps(body).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"),
                            (b"content-length", str(len(data)).encode())]})
    await send({"type": "http.response.body", "body": data})

class _IdentityMiddleware:
    def __init__(self, app): self._app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self._app(scope, receive, send); return
        if scope.get("path", "") == "/health":
            await self._app(scope, receive, send); return
        headers = dict(scope.get("headers", []))
        api_key = headers.get(b"x-api-key", b"").decode()
        if not api_key:
            await _asgi_json(send, {"error": "Unauthorized"}, 401); return
        creds = await resolve_credentials(api_key, mcp_name="mcp-marketing-ga4")
        _st = creds.pop("_status", None)
        if _st == 403:
            await _asgi_json(send, {"error": "Forbidden"}, 403); return
        if _st == 401:
            await _asgi_json(send, {"error": "Unauthorized"}, 401); return
        token = _request_creds.set(creds)
        try:
            await self._app(scope, receive, send)
        finally:
            _request_creds.reset(token)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carica schema GA4 usando credenziali dal primo utente disponibile (startup)
    # Lo schema è generico e non dipende dalle credenziali utente
    try:
        from ga4_mcp.tools.metadata import get_property_schema_uncached
        # Usa property_id placeholder per caricare lo schema dei campi disponibili
        PROPERTY_SCHEMA = get_property_schema_uncached(
            os.environ.get("GA4_PROPERTY_ID_BOOTSTRAP", "")
        )
        metadata.PROPERTY_SCHEMA = PROPERTY_SCHEMA
        reporting.PROPERTY_SCHEMA = PROPERTY_SCHEMA
    except Exception as e:
        import sys
        print(f"WARNING: Could not preload GA4 schema: {e}", file=sys.stderr)
    async with mcp.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(AlertMiddleware)
app.add_middleware(SessionMiddleware)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.mount("/", mcp.streamable_http_app())
app = _IdentityMiddleware(app)

def main():
    uvicorn.run("ga4_mcp.server:app", host="0.0.0.0",
                port=int(os.environ.get("PORT", "8128")))
