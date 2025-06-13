"""
Playlists router for Music Sync Hub.

This module handles displaying playlists and playlist tracks from various music services.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.errors import HttpError as GoogleHttpError

# Internal imports
from app.utils.dependencies import (
    get_valid_spotify_client,
    # get_valid_deezer_token,
    get_valid_youtube_service
)
from app.services.spotify_client import (
    get_playlists as get_spotify_playlists,
    get_playlist_tracks as get_spotify_playlist_tracks
)
# from app.services.deezer_client import (
#     get_playlists as get_deezer_playlists,
#     get_playlist_tracks as get_deezer_playlist_tracks
# )
from app.services.youtube_client import (
    get_playlists as get_youtube_playlists,
    get_playlist_items as get_youtube_playlist_items
)


router = APIRouter(tags=["playlists"])
templates = Jinja2Templates(directory="templates")


# ============================================================================
# Playlist Display Routes
# ============================================================================

@router.get("/spotify/playlists", response_class=HTMLResponse)
async def spotify_playlists(request: Request) -> HTMLResponse:
    """Display Spotify playlists."""
    try:
        sp = get_valid_spotify_client()
        playlists = get_spotify_playlists(sp)
        return templates.TemplateResponse(
            "playlists.html",
            {"request": request, "playlists": playlists, "service_name": "Spotify"}
        )
    except HTTPException:
        return RedirectResponse("/auth/spotify/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/deezer/playlists", response_class=HTMLResponse)
async def deezer_playlists(request: Request) -> HTMLResponse:
    """Display Deezer playlists."""
    try:
        return HTMLResponse(
            "Deezer playlists not implemented yet",
            status_code=501
        )
        # token = get_valid_deezer_token()
        # playlists = get_deezer_playlists(token)
        # return templates.TemplateResponse(
        #     "playlists.html",
        #     {"request": request, "playlists": playlists, "service_name": "Deezer"}
        # )
    except HTTPException:
        return RedirectResponse("/auth/deezer/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/youtube/playlists", response_class=HTMLResponse)
async def youtube_playlists(request: Request) -> HTMLResponse:
    """Display YouTube playlists."""
    try:
        service = get_valid_youtube_service()
        playlists = get_youtube_playlists(service)
        return templates.TemplateResponse(
            "playlists.html",
            {"request": request, "playlists": playlists, "service_name": "YouTube"}
        )
    except HTTPException:
        return RedirectResponse("/auth/youtube/login")
    except GoogleHttpError as e:
        return HTMLResponse(
            f"YouTube API Error: {e._get_reason()} "
            f"<a href='/auth/youtube/login'>Login again</a>",
            status_code=e.resp.status
        )
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


# ============================================================================
# Playlist Tracks API Routes
# ============================================================================

@router.get("/spotify/playlists/{playlist_id}/tracks", response_class=JSONResponse)
async def spotify_playlist_tracks_route(playlist_id: str) -> JSONResponse:
    """Get tracks for a specific Spotify playlist."""
    try:
        sp = get_valid_spotify_client()
        return get_spotify_playlist_tracks(sp, playlist_id)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail, "login_url": "/auth/spotify/login"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'detail': str(e)})


@router.get("/deezer/playlists/{playlist_id}/tracks", response_class=JSONResponse)
async def deezer_playlist_tracks_route(playlist_id: str) -> JSONResponse:
    """Get tracks for a specific Deezer playlist."""
    try:
        return JSONResponse(
            status_code=501,
            content={"detail": "Deezer playlist tracks not implemented yet"}
        )
        # token = get_valid_deezer_token()
        # return get_deezer_playlist_tracks(token, playlist_id)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail, "login_url": "/auth/deezer/login"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'detail': str(e)})


@router.get("/youtube/playlists/{playlist_id}/items", response_class=JSONResponse)
async def youtube_playlist_items_route(playlist_id: str) -> JSONResponse:
    """Get items for a specific YouTube playlist."""
    try:
        service = get_valid_youtube_service()
        return get_youtube_playlist_items(service, playlist_id)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail, "login_url": "/auth/youtube/login"}
        )
    except GoogleHttpError as e:
        return JSONResponse(
            status_code=e.resp.status,
            content={'detail': e._get_reason()}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'detail': str(e)}) 