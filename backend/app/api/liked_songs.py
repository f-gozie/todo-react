"""
Liked songs router for Music Sync Hub.

This module handles displaying liked songs and videos from various music services.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.errors import HttpError as GoogleHttpError

# Internal imports
from app.utils.dependencies import (
    get_valid_spotify_client,
    # get_valid_deezer_token,
    get_valid_youtube_service
)
from app.services.spotify_client import get_liked_songs as get_spotify_liked_songs
# from app.services.deezer_client import get_liked_songs as get_deezer_liked_songs
from app.services.youtube_client import get_liked_videos as get_youtube_liked_videos


router = APIRouter(tags=["liked-songs"])
templates = Jinja2Templates(directory="templates")


@router.get("/spotify/liked-songs", response_class=HTMLResponse)
async def spotify_liked_songs(request: Request) -> HTMLResponse:
    """Display Spotify liked songs."""
    try:
        sp = get_valid_spotify_client()
        songs = get_spotify_liked_songs(sp)
        return templates.TemplateResponse(
            "liked_songs.html",
            {"request": request, "songs": songs, "service_name": "Spotify"}
        )
    except HTTPException:
        return RedirectResponse("/auth/spotify/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/deezer/liked-songs", response_class=HTMLResponse)
async def deezer_liked_songs(request: Request) -> HTMLResponse:
    """Display Deezer liked songs."""
    try:
        return HTMLResponse(
            "Deezer liked songs not implemented yet",
            status_code=501
        )
        # token = get_valid_deezer_token()
        # songs = get_deezer_liked_songs(token)
        # return templates.TemplateResponse(
        #     "liked_songs.html",
        #     {"request": request, "songs": songs, "service_name": "Deezer"}
        # )
    except HTTPException:
        return RedirectResponse("/auth/deezer/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/youtube/liked-videos", response_class=HTMLResponse)
async def youtube_liked_videos(request: Request) -> HTMLResponse:
    """Display YouTube liked videos."""
    try:
        service = get_valid_youtube_service()
        videos = get_youtube_liked_videos(service)
        return templates.TemplateResponse(
            "liked_songs.html",
            {"request": request, "songs": videos, "service_name": "YouTube"}
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