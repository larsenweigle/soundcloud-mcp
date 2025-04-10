"""
Alternative entry point for the SoundCloud MCP server.
"""

from mcp.server import create_server


def run_server(transport="stdio", port=8082, host="localhost", access_token=None):
    """
    Create and run the SoundCloud MCP server.
    
    Args:
        transport (str): Transport mechanism ("stdio" or "sse")
        port (int): Port for SSE transport
        host (str): Host for SSE transport
        access_token (str): Optional SoundCloud access token
    """
    server = create_server(
        access_token=access_token,
        port=port,
        host=host
    )
    server.run(transport=transport)


if __name__ == "__main__":
    run_server() 