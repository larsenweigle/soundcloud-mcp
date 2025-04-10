import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.soundcloud_client import SoundCloudClient
from mcp.utils import get_access_token, format_track_info

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("soundcloud-mcp")

# Models for parameter validation
class BPM(BaseModel):
    min_bpm: int = Field(..., description="Minimum BPM")
    max_bpm: int = Field(..., description="Maximum BPM")

class Duration(BaseModel):
    min_duration: int = Field(..., description="Minimum duration in seconds")
    max_duration: int = Field(..., description="Maximum duration in seconds")

class CreatedAt(BaseModel):
    min_created_at: str = Field(..., description="Minimum created date in the format YYYY-MM-DD HH:MM:SS")
    max_created_at: str = Field(..., description="Maximum created date in the format YYYY-MM-DD HH:MM:SS")

def create_server(access_token: Optional[str] = None, **kwargs) -> FastMCP:
    """
    Create and configure a SoundCloud MCP server.
    
    Args:
        access_token: SoundCloud access token (optional, will try env var or token file if not provided)
        **kwargs: Additional arguments to pass to FastMCP constructor
        
    Returns:
        Configured FastMCP server
    """
    # Get SoundCloud token - prioritize passed token, then use utility function
    user_access_token = access_token or get_access_token()
    if not user_access_token:
        logger.error("No SoundCloud access token found. Search functionality will not work.")

    # Initialize SoundCloud client
    soundcloud_client = SoundCloudClient(user_access_token) if user_access_token else None

    # Create MCP server
    server = FastMCP(
        name="soundcloud-mcp",
        instructions=(
            "Use the search tracks tool to search for tracks on SoundCloud."
        ),
        dependencies=["httpx", "pydantic"],
        **kwargs
    )

    @server.tool()
    async def search_tracks(
        query: Optional[str] = None,
        genres: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        bpm: Optional[BPM] = None,
        duration: Optional[Duration] = None,
        created_at: Optional[CreatedAt] = None,
        limit: int = 10,
        format_results: bool = True,
    ) -> Dict[str, Any]:
        """
        Search for tracks on SoundCloud.

        Args:
            query (str): The name of the track to search for.
            genres (List[str]): The genres to search for (ex: Pop, House).
            tags (List[str]): The tags to search for.
            bpm (BPM): The BPM range to search for.
            duration (Duration): The duration range to search for.
            created_at (CreatedAt): The date and time range to search for.
            limit (int): Maximum number of results to return (default: 10)
            format_results (bool): Whether to format results in a human-readable way (default: True)
        """
        if not soundcloud_client:
            return {
                "error": "SoundCloud client not initialized. Please set SOUNDCLOUD_ACCESS_TOKEN."
            }
        
        try:
            # Convert Pydantic models to dictionaries for the client
            bpm_dict = None
            if bpm:
                bpm_dict = {
                    "from": bpm.min_bpm,
                    "to": bpm.max_bpm
                }
                
            duration_dict = None
            if duration:
                duration_dict = {
                    "from": duration.min_duration,
                    "to": duration.max_duration
                }
                
            created_at_dict = None
            if created_at:
                created_at_dict = {
                    "from": created_at.min_created_at,
                    "to": created_at.max_created_at
                }
            
            # Use the SoundCloudClient to search for tracks
            response = await soundcloud_client.search_tracks(
                query=query,
                genres=genres,
                tags=tags,
                bpm=bpm_dict,
                duration=duration_dict,
                created_at=created_at_dict,
                limit=limit
            )
            
            if isinstance(response, dict) and "error" in response:
                logger.error(f"Error from SoundCloud API: {response['error']}")
                return response
                
            # Count tracks found
            track_count = len(response.get("collection", [])) if isinstance(response, dict) else 0
            logger.info(f"Found {track_count} tracks")
            
            # Format the results if requested
            if format_results and track_count > 0:
                formatted_tracks = []
                for track in response.get("collection", []):
                    formatted_tracks.append(format_track_info(track))
                
                return {
                    "count": track_count,
                    "tracks": formatted_tracks,
                    "raw_data": response
                }
                
            return response or {"error": "No results found"}
        
        except Exception as e:
            logger.error(f"Error searching tracks: {str(e)}")
            return {"error": f"Failed to search tracks: {str(e)}"}
            
    return server

if __name__ == "__main__":
    # For testing directly
    import asyncio
    
    # Create and run the server
    server = create_server()
    
    if get_access_token():
        print("Testing search_tracks...")
        # Get the search_tracks function from the server tools
        async def test_search():
            try:
                result = await server.tools["search_tracks"].func(query="Summertime Blues")
                track_count = len(result.get('collection', [])) if isinstance(result, dict) else 0
                print(f"Found {track_count} tracks")
            except Exception as e:
                print(f"Error testing search: {e}")
        
        # Run the test
        asyncio.run(test_search())
    
    # Run the server
    server.run(transport="sse")
