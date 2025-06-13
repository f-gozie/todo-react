"""
FastAPI dependencies for Music Sync Hub.

This module contains dependency functions that provide authenticated clients
for various music services.
"""

from typing import Optional
from fastapi import HTTPException
import spotipy
from google.auth.exceptions import RefreshError as GoogleRefreshError

# Internal imports - Spotify
from app.services.spotify_client import (
    get_spotify_client,
    temporary_token_cache as spotify_token_cache
)

# Internal imports - Deezer
# from app.services.deezer_client import temporary_token_cache as deezer_token_cache

# Internal imports - YouTube
from app.services.youtube_client import (
    get_youtube_client_service,
    temporary_token_cache as youtube_token_cache
)


def get_valid_spotify_client(raise_exception: bool = True) -> Optional[spotipy.Spotify]:
    """
    Get a validated Spotify client from the token cache.
    
    Args:
        raise_exception: Whether to raise an HTTPException if not authenticated
        
    Returns:
        Spotify client instance or None if not authenticated
        
    Raises:
        HTTPException: If raise_exception is True and user is not authenticated
    """
    token_info = spotify_token_cache.get('spotify_token_info')
    if not token_info:
        if raise_exception:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify.")
        return None
    return get_spotify_client(token_info)


def get_valid_deezer_token(raise_exception: bool = True) -> Optional[str]:
    """
    Get a validated Deezer access token from the token cache.
    
    Args:
        raise_exception: Whether to raise an HTTPException if not authenticated
        
    Returns:
        Deezer access token or None if not authenticated
        
    Raises:
        HTTPException: If raise_exception is True and user is not authenticated
    """
    return None
    # access_token = deezer_token_cache.get('deezer_access_token')
    # if not access_token:
    #     if raise_exception:
    #         raise HTTPException(status_code=401, detail="Not authenticated with Deezer.")
    #     return None
    # return access_token


def get_valid_youtube_service(raise_exception: bool = True):
    """
    Get a validated YouTube service instance from the token cache.
    
    Args:
        raise_exception: Whether to raise an HTTPException if not authenticated
        
    Returns:
        YouTube service instance or None if not authenticated
        
    Raises:
        HTTPException: If raise_exception is True and user is not authenticated
    """
    credentials_json_str = youtube_token_cache.get('youtube_credentials')
    if not credentials_json_str:
        if raise_exception:
            raise HTTPException(status_code=401, detail="Not authenticated with YouTube.")
        return None
    
    try:
        return get_youtube_client_service(credentials_json_str)
    except GoogleRefreshError as e:
        youtube_token_cache.pop('youtube_credentials', None)
        if raise_exception:
            raise HTTPException(status_code=401, detail=f"YouTube token refresh failed: {e}.")
        return None
    except Exception as e:
        youtube_token_cache.pop('youtube_credentials', None)
        if raise_exception:
            raise HTTPException(status_code=401, detail=f"Invalid YouTube credentials: {e}.")
        return None 