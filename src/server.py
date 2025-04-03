import sys
from typing import List, Optional
import json

from pydantic import BaseModel, Field
import mcp.server.stdio
import mcp.types as types
from mcp.server.fastmcp import FastMCP

from soundcloud_client import SoundCloudClient

# Create MCP server
server = FastMCP(
    name="soundcloud-mcp",
    instructions=(
        "Use the search tracks tool to search for tracks on soundcloud."
    ),
    port=8082,
    host="localhost",
)

def setup_logger():
    class Logger:
        def info(self, message):
            print(f"[INFO] {message}", file=sys.stderr)

        def error(self, message):
            print(f"[ERROR] {message}", file=sys.stderr)

    return Logger()


logger = setup_logger()

# Fetch user credentials from the token json file for now.
with open("soundcloud_token.json", "r") as f:
    soundcloud_token = json.load(f)
    user_access_token = soundcloud_token["access_token"]

soundcloud_client = SoundCloudClient(user_access_token=user_access_token)

# ===== MCP Tool Schemas =====

class ToolModel(BaseModel):
    @classmethod
    def as_tool(cls):
        return types.Tool(
            name="SoundCloud" + cls.__name__,
            description=cls.__doc__,
            inputSchema=cls.model_json_schema()
        )


class BPM(BaseModel):
    min_bpm: int
    max_bpm: int


# TODO test if this is seconds or minutes
class Duration(BaseModel):
    min_duration: int = Field(..., description="In seconds")
    max_duration: int = Field(..., description="In seconds")


class CreatedAt(BaseModel):
    min_created_at: str = Field(..., description="In the format YYYY-MM-DD HH:MM:SS")
    max_created_at: str = Field(..., description="In the format YYYY-MM-DD HH:MM:SS")
   

# TODO: determine which ones are actually needed
class SearchTracks(ToolModel):
    """
    Search for tracks on SoundCloud.

    Args:
        query (str): The name of the track to search for.
        genres (List[str]): The genres to search for (ex: Pop, House).
        tags (List[str]): The tags to search for.
        bpm (BPM): The BPM range to search for.
        duration (Duration): The duration range to search for.
        created_at (CreatedAt): The date and time range to search for.
    """
    query: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    bpm: Optional[BPM] = None
    duration: Optional[Duration] = None
    created_at: Optional[CreatedAt] = None

# ===== MCP Server Setup =====

tools = [
    SearchTracks.as_tool(),
]

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return []


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return []


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("Listing available tools")
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    return tools


@server.call_tool()
async def handle_call_tool( name: str, arguments: dict | None) -> List[types.CallToolResult]:
    if name not in [tool.name for tool in tools]:
        logger.error(f"Tool {name} not found. Use the `list_tools` tool to see available tools.")
        tool_result = types.CallToolResult(
            content=[types.TextContent(text=f"Tool {name} not found. Use the `list_tools` tool to see available tools.")],
            isError=True
        )   
        return [tool_result]
    
    tool_name = name[len("SoundCloud"):]
    logger.info(f"Calling tool {tool_name} with arguments {arguments}")
    try:
        match tool_name:
            case "SearchTracks":
                result = await soundcloud_client.search_tracks(
                    query=arguments.get("query", None),
                    genres=arguments.get("genres", None),
                    tags=arguments.get("tags", None),
                    bpm=arguments.get("bpm", None),
                    duration=arguments.get("duration", None),
                    created_at=arguments.get("created_at", None),
                    limit=arguments.get("limit", 10)
                )
                return [types.CallToolResult(
                    content=[types.TextContent(text=f"Search tracks result: {result}")],
                    isError=False
                )]
            
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.CallToolResult(
            content=[types.TextContent(text=f"Error calling tool {name}: {e}")],
            isError=True
        )]
    

if __name__ == "__main__":
    server.run(transport="sse")