import json
import logging
import pprint
from typing import Any, Dict, List, Optional

import httpx


class SoundCloudClient:
    """
    A basic client for the SoundCloud API.
    """
    def __init__(self, user_access_token: str):
        self.user_access_token = user_access_token
        self.client = httpx.AsyncClient()
        self.logger = logging.getLogger(__name__)

    async def _send_soundcloud_request(
            self,
            url: str,
            method: str,
            params: dict[str, Any] = {}
    ) -> Any:
        """
        Sends a request to the SoundCloud API using the requests library.
        """
        headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.user_access_token}"
        }

        self.logger.info(f"Sending request to {url} with method {method} and params {params}")
        try:
            response = await self.client.request(method, url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


    async def search_tracks(
            self,
            query: Optional[str] = None,
            genres: Optional[List[str]] = None,
            tags: Optional[List[str]] = None,
            bpm: Optional[Dict[str, int]] = None,
            duration: Optional[Dict[str, int]] = None,
            created_at: Optional[Dict[str, str]] = None,
            limit: int=10
    ) -> List[Dict[str, Any]]:
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
        url = "https://api.soundcloud.com/tracks"

        # TODO need to see what this looks like
        linked_partitioning = True

        # Start with empty params dict
        params = {}
        
        # Only add parameters that are not None
        if query is not None:
            params["q"] = query
            
        if genres is not None:
            params["genres"] = ",".join(genres)
            
        if tags is not None:
            params["tags"] = ",".join(tags)
            
        if bpm is not None:
            params["bpm[from]"] = bpm.min_bpm
            params["bpm"] = {
                "from": bpm.min_bpm,
                "to": bpm.max_bpm
            }
            
        if duration is not None:
            params["duration"] = {
                "from": duration.min_duration,
                "to": duration.max_duration
            }
            
        if created_at is not None:
            params["created_at"] = {
                "from": created_at.min_created_at,
                "to": created_at.max_created_at
            }

        params["limit"] = limit
        
        # Always add linked_partitioning
        params["linked_partitioning"] = linked_partitioning

        # Call the synchronous function directly
        response = await self._send_soundcloud_request(url, "GET", params)

        print(f"Track search results:")
        pprint.pprint(response)

        return response

if __name__ == "__main__":
    import asyncio
    # Fetch user credentials from the token json file for now.
    with open("soundcloud_token.json", "r") as f:
        soundcloud_token = json.load(f)
        user_access_token = soundcloud_token["access_token"]

    test_client = SoundCloudClient(user_access_token=user_access_token)

    print("Searching for tracks with query 'Summertime Blues'")
    asyncio.run(test_client.search_tracks(query="Summertime Blues"))

    print("Searching for tracks with query 'Summertime Blues' and genres 'House'")
    asyncio.run(test_client.search_tracks(query="Summertime Blues", genres=["House"]))
