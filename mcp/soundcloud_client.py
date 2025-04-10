import json
import logging
from typing import Any, Dict, List, Optional

import httpx


class SoundCloudClient:
    """
    A client for the SoundCloud API.
    """
    def __init__(self, user_access_token: str):
        self.user_access_token = user_access_token
        self.client = httpx.AsyncClient()
        self.logger = logging.getLogger(__name__)
        self.api_base_url = "https://api.soundcloud.com"

    async def _send_soundcloud_request(
            self,
            endpoint: str,
            method: str = "GET",
            params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Sends a request to the SoundCloud API.
        
        Args:
            endpoint: The API endpoint (without the base URL)
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.user_access_token}"
        }

        self.logger.info(f"Sending request to {url} with method {method} and params {params}")
        try:
            response = await self.client.request(
                method, 
                url, 
                headers=headers, 
                params=params, 
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except httpx.TimeoutException:
            self.logger.error("Request timed out")
            return {"error": "Request timed out"}
        except Exception as e:
            self.logger.error(f"Error sending request: {str(e)}")
            return {"error": str(e)}

    async def search_tracks(
            self,
            query: Optional[str] = None,
            genres: Optional[List[str]] = None,
            tags: Optional[List[str]] = None,
            bpm: Optional[Dict[str, int]] = None,
            duration: Optional[Dict[str, int]] = None,
            created_at: Optional[Dict[str, str]] = None,
            limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for tracks on SoundCloud.

        Args:
            query: The search query
            genres: List of genres to filter by
            tags: List of tags to filter by
            bpm: Dictionary with "from" and "to" keys for BPM range
            duration: Dictionary with "from" and "to" keys for duration range in seconds
            created_at: Dictionary with "from" and "to" keys for creation date range
            limit: Maximum number of results to return
            
        Returns:
            Search results as dictionary
        """
        params = {}
        
        # Only add parameters that are not None
        if query is not None:
            params["q"] = query
            
        if genres is not None:
            params["genres"] = ",".join(genres)
            
        if tags is not None:
            params["tags"] = ",".join(tags)
            
        if bpm is not None:
            params["bpm[from]"] = bpm["from"]
            params["bpm[to]"] = bpm["to"]
            
        if duration is not None:
            params["duration[from]"] = duration["from"]
            params["duration[to]"] = duration["to"]
            
        if created_at is not None:
            params["created_at[from]"] = created_at["from"]
            params["created_at[to]"] = created_at["to"]

        params["limit"] = limit
        
        # Always add linked_partitioning for pagination support
        params["linked_partitioning"] = "1"

        return await self._send_soundcloud_request("tracks", "GET", params)

if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    # For testing the client directly
    load_dotenv()
    
    async def main():
        # Get token from environment or file
        user_access_token = os.getenv("SOUNDCLOUD_ACCESS_TOKEN")
        if not user_access_token:
            try:
                with open("soundcloud_token.json", "r") as f:
                    soundcloud_token = json.load(f)
                    user_access_token = soundcloud_token["access_token"]
            except (FileNotFoundError, json.JSONDecodeError):
                print("Error: No SoundCloud access token found")
                return
                
        # Create client and run tests
        client = SoundCloudClient(user_access_token)
        
        print("\nTesting search for 'Summertime Blues':")
        results = await client.search_tracks(query="Summertime Blues")
        print(f"Found {len(results.get('collection', []))} tracks")
        
        print("\nTesting search with genre filter:")
        results = await client.search_tracks(query="Summertime", genres=["House"])
        print(f"Found {len(results.get('collection', []))} House tracks")
        
        print("\nTesting search with BPM range:")
        results = await client.search_tracks(
            query="Techno", 
            bpm={"from": 120, "to": 140}
        )
        print(f"Found {len(results.get('collection', []))} Techno tracks with BPM 120-140")
    
    asyncio.run(main())
