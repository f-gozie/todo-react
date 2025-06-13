"""
User profiles router for Music Sync Hub.

This module handles displaying user profile information from various music services.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.errors import HttpError as GoogleHttpError

# Internal imports
from ..utils.dependencies import (
    get_valid_spotify_client,
    get_valid_deezer_token,
    get_valid_youtube_service
)
from ..deezer_client import get_deezer_user_info


router = APIRouter(prefix="/me", tags=["profiles"])
templates = Jinja2Templates(directory="templates")


@router.get("/spotify", response_class=HTMLResponse)
async def show_spotify_profile(request: Request) -> HTMLResponse:
    """Display Spotify user profile."""
    try:
        sp = get_valid_spotify_client()
        user = sp.current_user()
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user_data": user, "service_name": "Spotify"}
        )
    except HTTPException:
        return RedirectResponse("/auth/spotify/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/deezer", response_class=HTMLResponse)
async def show_deezer_profile(request: Request) -> HTMLResponse:
    """Display Deezer user profile."""
    try:
        token = get_valid_deezer_token()
        user_info = get_deezer_user_info(token)
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user_data": user_info, "service_name": "Deezer"}
        )
    except HTTPException:
        return RedirectResponse("/auth/deezer/login")
    except Exception as e:
        return HTMLResponse(
            f"Error: {e} <a href='/'>Home</a>",
            status_code=500
        )


@router.get("/youtube", response_class=HTMLResponse)
async def show_youtube_profile(request: Request) -> HTMLResponse:
    """Display YouTube user profile."""
    try:
        service = get_valid_youtube_service()
        response = service.channels().list(part="snippet", mine=True).execute()
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user_data": response, "service_name": "YouTube"}
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