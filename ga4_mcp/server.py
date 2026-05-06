"""GA4 MCP server — Agent24 pattern (mcp-common)."""
from __future__ import annotations
import os, sys
from ga4_mcp.coordinator import app, main, mcp  # noqa: F401  (mcp serve ai tool import)
from ga4_mcp.tools import metadata, reporting  # noqa: F401  (registra i @tool)

# Preload dello schema GA4: usa property_id bootstrap da env (lo schema è
# generico, non dipende dalle credenziali utente). Sync, top-level: blocca
# l'avvio ma una volta sola.
try:
    from ga4_mcp.tools.metadata import get_property_schema_uncached
    _schema = get_property_schema_uncached(os.environ.get("GA4_PROPERTY_ID_BOOTSTRAP", ""))
    metadata.PROPERTY_SCHEMA = _schema
    reporting.PROPERTY_SCHEMA = _schema
except Exception as e:
    print(f"WARNING: Could not preload GA4 schema: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
