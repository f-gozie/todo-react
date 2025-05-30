"""
Music Sync Hub - Main FastAPI Application

This module provides the main FastAPI application for synchronizing music
across Spotify, Deezer, and YouTube Music platforms.
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .routers import auth, profiles, liked_songs, playlists, sync
from .utils.helpers import slugify


app = FastAPI(
    title="Music Sync Hub",
    description="Synchronize your music across Spotify, Deezer, and YouTube Music",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


templates = Jinja2Templates(directory="templates")
templates.env.filters['slugify'] = slugify


app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(liked_songs.router)
app.include_router(playlists.router)
app.include_router(sync.router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
