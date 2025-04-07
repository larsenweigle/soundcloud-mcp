import sys
from typing import List, Optional
import json

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from soundcloud_client import SoundCloudClient


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


# ===== MCP Server Setup =====

# Create MCP server
server = FastMCP(
    name="soundcloud-mcp",
    instructions=(
        "Use the search tracks tool to search for tracks on soundcloud."
    ),
    # port=8082,
    # host="localhost",
)


class BPM(BaseModel):
    min_bpm: int
    max_bpm: int


class Duration(BaseModel):
    min_duration: int = Field(..., description="In seconds")
    max_duration: int = Field(..., description="In seconds")


class CreatedAt(BaseModel):
    min_created_at: str = Field(..., description="In the format YYYY-MM-DD HH:MM:SS")
    max_created_at: str = Field(..., description="In the format YYYY-MM-DD HH:MM:SS")
   

@server.tool()
async def search_tracks(
    query: str = None,
    genres: List[str] = None,
    tags: List[str] = None,
    bpm: BPM = None,
    duration: Duration = None,
    created_at: CreatedAt = None
) -> str:
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
    result = await soundcloud_client.search_tracks(
        query=query,
        genres=genres,
        tags=tags,
        bpm=bpm,
        duration=duration,
        created_at=created_at
    )

    return result
    

if __name__ == "__main__":
    server.run(transport="stdio")