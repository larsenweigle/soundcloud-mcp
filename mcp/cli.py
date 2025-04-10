#!/usr/bin/env python3
"""
CLI entry point for the SoundCloud MCP server
"""

import argparse
import sys
import os
from typing import Optional

from mcp.server import create_server


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Run the SoundCloud MCP server")
    
    parser.add_argument(
        "--token",
        type=str,
        help="SoundCloud access token (otherwise will use SOUNDCLOUD_ACCESS_TOKEN env var or soundcloud_token.json)",
    )
    
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mechanism (stdio or sse, default: stdio)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="Port for SSE transport (default: 8082)",
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for SSE transport (default: localhost)",
    )
    
    args = parser.parse_args()
    
    # Create the server
    server = create_server(
        access_token=args.token,
        port=args.port,
        host=args.host
    )
    
    # Run the server with the specified transport
    server.run(transport=args.transport)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 