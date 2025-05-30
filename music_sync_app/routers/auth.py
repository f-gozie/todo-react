"""
Authentication router for Music Sync Hub.

This module handles OAuth authentication flows for Spotify, Deezer, and YouTube.
"""

from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import spotipy

# Internal imports
from ..spotify_client import (
    create_spotify_oauth,
    temporary_token_cache as spotify_token_cache
)
from ..deezer_client import (
    get_deezer_auth_url,
    get_deezer_access_token,
    temporary_token_cache as deezer_token_cache
)
from ..youtube_client import (
    create_youtube_flow,
    temporary_token_cache as youtube_token_cache,
    temporary_state_cache as youtube_state_cache
)
from google.oauth2.credentials import Credentials as GoogleCredentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import OAuthError as GoogleOAuthError


router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# Spotify Authentication
# ============================================================================

@router.get("/spotify/login")
async def login_spotify() -> RedirectResponse:
    """Initiate Spotify OAuth flow."""
    sp_oauth = create_spotify_oauth()
    return RedirectResponse(sp_oauth.get_authorize_url())


@router.get("/spotify/callback")
async def callback_spotify(request: Request, code: Optional[str] = None) -> HTMLResponse:
    """Handle Spotify OAuth callback."""
    sp_oauth = create_spotify_oauth()
    
    if not code:
        error = request.query_params.get('error', 'No code provided.')
        return HTMLResponse(
            f"<html><body>Spotify login failed: {error} "
            f"<a href='/auth/spotify/login'>Try again</a></body></html>",
            status_code=400
        )
    
    try:
        spotify_token_cache['spotify_token_info'] = sp_oauth.get_access_token(code, check_cache=False)
        return HTMLResponse(
            "<html><body>Spotify Login Successful! <a href='/'>Home</a></body></html>"
        )
    except spotipy.SpotifyOauthError as e:
        return HTMLResponse(
            f"<html><body>Spotify Auth Error: {e} <a href='/'>Home</a></body></html>",
            status_code=400
        )


# ============================================================================
# Deezer Authentication
# ============================================================================

@router.get("/deezer/login")
async def login_deezer() -> RedirectResponse:
    """Initiate Deezer OAuth flow."""
    return RedirectResponse(get_deezer_auth_url())


@router.get("/deezer/callback")
async def callback_deezer(
    request: Request,
    code: Optional[str] = None,
    error_reason: Optional[str] = None
) -> HTMLResponse:
    """Handle Deezer OAuth callback."""
    if error_reason:
        return HTMLResponse(
            f"<html><body>Deezer login failed: {error_reason} "
            f"<a href='/auth/deezer/login'>Try again</a></body></html>",
            status_code=400
        )
    
    if not code:
        return HTMLResponse(
            "<html><body>Deezer login failed: No code. "
            "<a href='/auth/deezer/login'>Try again</a></body></html>",
            status_code=400
        )
    
    token = get_deezer_access_token(code)
    if not token:
        return HTMLResponse(
            "<html><body>Deezer Token Error. <a href='/'>Home</a></body></html>",
            status_code=400
        )
    
    deezer_token_cache['deezer_access_token'] = token
    return HTMLResponse(
        "<html><body>Deezer Login Successful! <a href='/'>Home</a></body></html>"
    )


# ============================================================================
# YouTube Authentication
# ============================================================================

@router.get("/youtube/login")
async def login_youtube() -> RedirectResponse:
    """Initiate YouTube OAuth flow."""
    try:
        flow = create_youtube_flow()
        auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
        youtube_state_cache['oauth_state'] = state
        return RedirectResponse(auth_url)
    except Exception as e:
        return HTMLResponse(
            f"YouTube Login Error: {e}. Ensure 'client_secret_youtube.json' is configured. "
            f"<a href='/'>Home</a>",
            status_code=500
        )


@router.get("/youtube/callback")
async def callback_youtube(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
) -> HTMLResponse:
    """Handle YouTube OAuth callback."""
    if error:
        return HTMLResponse(
            f"<html><body>YouTube login failed: {error} "
            f"<a href='/auth/youtube/login'>Try again</a></body></html>",
            status_code=400
        )
    
    if not code:
        return HTMLResponse(
            "<html><body>YouTube login failed: No code. "
            "<a href='/auth/youtube/login'>Try again</a></body></html>",
            status_code=400
        )
    
    try:
        flow = create_youtube_flow()
        flow.fetch_token(code=code)
        youtube_token_cache['youtube_credentials'] = flow.credentials.to_json()
        return HTMLResponse(
            "<html><body>YouTube Login Successful! <a href='/'>Home</a></body></html>"
        )
    except GoogleOAuthError as e:
        return HTMLResponse(
            f"<html><body>YouTube OAuth Error: {e} <a href='/'>Home</a></body></html>",
            status_code=400
        ) 