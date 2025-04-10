"""
Utility functions for the SoundCloud MCP server.
"""

import json
import os
from typing import Dict, Optional, Any


def get_access_token() -> Optional[str]:
    """
    Get the SoundCloud access token from environment variable or token file.
    
    Returns:
        Optional[str]: The access token, or None if not found
    """
    # Try environment variable first
    token = os.getenv("SOUNDCLOUD_ACCESS_TOKEN")
    if token:
        return token
    
    # Try token file
    try:
        with open("soundcloud_token.json", "r") as f:
            token_data = json.load(f)
            return token_data.get("access_token")
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def format_track_info(track: Dict[str, Any]) -> str:
    """
    Format track information into a readable string.
    
    Args:
        track: Track data from SoundCloud API
        
    Returns:
        Formatted track info as string
    """
    if not track or not isinstance(track, dict):
        return "Invalid track data"
    
    parts = [
        f"Title: {track.get('title', 'Unknown')}",
        f"Artist: {track.get('user', {}).get('username', 'Unknown')}",
        f"Duration: {format_duration(track.get('duration', 0))}",
    ]
    
    if "genre" in track and track["genre"]:
        parts.append(f"Genre: {track['genre']}")
    
    if "permalink_url" in track:
        parts.append(f"Link: {track['permalink_url']}")
    
    return "\n".join(parts)


def format_duration(milliseconds: int) -> str:
    """
    Format milliseconds as mm:ss.
    
    Args:
        milliseconds: Duration in milliseconds
        
    Returns:
        Formatted duration as mm:ss
    """
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}" 