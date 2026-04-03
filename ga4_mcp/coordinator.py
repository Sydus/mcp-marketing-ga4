"""
This module declares the singleton MCP instance.

This allows other modules (server, tools) to import the same mcp object
without creating circular dependencies.
"""
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "Google Analytics 4",
    transport_security=TransportSecuritySettings(allowed_hosts=["mcp.agent24.it"]),
)
