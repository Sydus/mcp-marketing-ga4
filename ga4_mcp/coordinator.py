"""Singleton MCP/app per evitare import ciclici tra server e tools."""
from mcp_common import create_mcp_app

mcp, app, main = create_mcp_app(
    name="Google Analytics 4",
    instructions=(
        "Espone Google Analytics 4 in lettura: liste di metric/dimension "
        "disponibili per la property, query di reporting (analytics.runReport) "
        "con filtri, ordini, breakdown temporali. Tutti i tool richiedono "
        "identity: il property_id e le credenziali del service account "
        "vengono risolti dall'api-key del cliente."
    ),
    port=8128,
)
