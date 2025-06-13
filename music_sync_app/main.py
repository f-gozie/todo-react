"""
Music Sync Hub - Main FastAPI Application

This module provides the main FastAPI application for synchronizing music
across Spotify and YouTube Music platforms.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .routers import auth, profiles, liked_songs, playlists, sync
from .utils.helpers import slugify
from .utils.session_manager import session_manager
from .config import DEBUG, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🎵 Music Sync Hub starting up...")
    
    # Clean up any expired sessions on startup
    cleaned = session_manager.cleanup_expired_sessions()
    logger.info(f"Cleaned {cleaned} expired sessions on startup")
    
    # Start periodic session cleanup task
    cleanup_task = asyncio.create_task(periodic_session_cleanup())
    
    yield
    
    # Shutdown
    logger.info("🎵 Music Sync Hub shutting down...")
    
    # Cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Final session cleanup
    cleaned = session_manager.cleanup_expired_sessions()
    logger.info(f"Final cleanup: {cleaned} sessions cleaned")


async def periodic_session_cleanup():
    """Periodic task to clean up expired sessions."""
    while True:
        try:
            # Wait 1 hour between cleanups
            await asyncio.sleep(3600)
            cleaned = session_manager.cleanup_expired_sessions()
            if cleaned > 0:
                logger.info(f"Periodic cleanup: {cleaned} expired sessions removed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic session cleanup: {e}")


app = FastAPI(
    title="Music Sync Hub",
    description="Synchronize your music across Spotify and YouTube Music",
    version="2.0.0",
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None,
    lifespan=lifespan
)

# Add security middleware
if not DEBUG:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.localhost", "*.local", "*.yourdomain.com"]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"] if DEBUG else [],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Templates setup
templates = Jinja2Templates(directory="templates")
templates.env.filters['slugify'] = slugify

# Include routers
app.include_router(auth.router)
app.include_router(profiles.router) 
app.include_router(liked_songs.router)
app.include_router(playlists.router)
app.include_router(sync.router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Home page with sync functionality."""
    logger.info(f"Home page accessed from {request.client.host if request.client else 'unknown'}")
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Music Sync Hub",
        "version": "2.0.0"
    }


# Global exception handler
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "An internal server error occurred."},
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Music Sync Hub...")
    uvicorn.run(
        "music_sync_app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
