import os
import requests
import base64

CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOUNDCLOUD_CLIENT_SECRET")

# ----- Client Credentials Token Exchange Flow -----

"""
# obtain the access token

$ curl -X POST "https://secure.soundcloud.com/oauth/token" \
     -H  "accept: application/json; charset=utf-8" \
     -H  "Content-Type: application/x-www-form-urlencoded" \
     -H  "Authorization: Basic Base64(client_id:client_secret)" \
     --data-urlencode "grant_type=client_credentials"

# If your client_id is "my_client_id" and client_secret is "my_client_secret"
# The concatenated string would be "my_client_id:my_client_secret"
# The Base64 encoded string of "my_client_id:my_client_secret" is "bXlfY2xpZW50X2lkOm15X2NsaWVudF9zZWNyZXQ="
"""

def get_soundcloud_token_client_credentials() -> str:
    """
    Uses Client Credentials Token Exchange Flow to get an access token.

    Note that this is for server-to-server authentication.

    See: https://developers.soundcloud.com/docs/api/guide#authentication
        
    Returns:
        str: The access token or None if an error occurred
    """
    url = "https://secure.soundcloud.com/oauth/token"
    
    # Create the Base64 encoded credentials for Basic auth
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "accept": "application/json; charset=utf-8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }

    data = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        print(f"Successfully got soundcloud token: {response.json()}")
        return response.json()["access_token"]
    except Exception as e:
        print(f"Error getting soundcloud token: {e}")
        return None
    

"""
# refresh token

$ curl -X POST "https://secure.soundcloud.com/oauth/token" \
     -H  "accept: application/json; charset=utf-8" \
     -H  "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=refresh_token" \
     --data-urlencode "client_id=YOUR_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_CLIENT_SECRET" \
     --data-urlencode "refresh_token=YOUR_TOKEN" \
"""

def refresh_soundcloud_token(refresh_token: str) -> str:
    """
    Refreshes the SoundCloud access token using the refresh token.

    See: https://developers.soundcloud.com/docs/api/guide#authentication
        
    Args:
        refresh_token (str): The refresh token to use

    Returns:
        str: The new access token or None if an error occurred
    """
    url = "https://secure.soundcloud.com/oauth/token"

    headers = {
        "accept": "application/json; charset=utf-8",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Error refreshing soundcloud token: {e}")
        return None


if __name__ == "__main__":
    import json
    # Save the token to a file
    token = get_soundcloud_token_client_credentials()
    with open("soundcloud_token.json", "w") as f:
        json.dump({"token": token}, f)
