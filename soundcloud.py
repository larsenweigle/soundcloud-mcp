from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

async def send_soundcloud_request(
        url: str,
        method: str,
        data: dict[str, Any] = {},
        headers: dict[str, str] = {}
) -> Any:
    """
    Sends a request to the SoundCloud API.
    """
    
    # # get access token
    # access_token = get_soundcloud_token_client_credentials()

    # # add access token to headers
    # headers["Authorization"] = f"Bearer {access_token}"

    with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            error_string = f"Error sending soundcloud request: {e}"
            return {"error": error_string}

# ==== Track Search Tool ====
        
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


# TODO see which of these are required!
@mcp.tool()
async def search_tracks(
        query: Optional[str] = None,
        genres: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        bpm: Optional[BPM] = None,
        duration: Optional[Duration] = None,
        created_at: Optional[CreatedAt] = None
) -> List[Dict[str, Any]]:
    """
    Search for tracks on SoundCloud.

    Args:
        query (str): The query to search for
        genres (List[str]): The genres to search for (ex: Pop, House)
        tags (List[str]): The tags to search for
        bpm (BPM): The BPM range to search for
        duration (Duration): The duration range to search for
        created_at (CreatedAt): The date and time range to search for
    """
    
    url = "https://api.soundcloud.com/tracks"

    # TODO need to see what this looks like
    linked_partitioning = True

    params = {
        "q": query,
        "genres": ",".join(genres),
        "tags": ",".join(tags),
        "bpm[from]": bpm.min_bpm,
        "bpm": {
            "from": bpm.min_bpm,
            "to": bpm.max_bpm
        },
        "duration": {
            "from": duration.min_duration,
            "to": duration.max_duration
        },
        "created_at": {
            "from": created_at.min_created_at,
            "to": created_at.max_created_at
        },
        "linked_partitioning": linked_partitioning,
    }

    response = await send_soundcloud_request(url, "GET", params)

    print(f"search_tracks response: {response}")

    return response

# Constants
# NWS_API_BASE = "https://api.weather.gov"
# USER_AGENT = "weather-app/1.0"