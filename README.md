# Cross-Platform Music Sync Application

## Overview

This application allows users to synchronize their liked songs and playlists across multiple music streaming services: Spotify, Deezer, and YouTube Music. It provides a web interface for users to authenticate with these services, analyze differences in their libraries, and manually or automatically perform synchronization tasks.

## Features

*   **Multi-Platform Authentication:** Secure OAuth 2.0 based authentication for Spotify, Deezer, and YouTube Music.
*   **Web Interface:** Built with FastAPI (Python) for the backend and HTMX for dynamic frontend updates, providing a responsive user experience without complex JavaScript.
*   **Library Analysis:**
    *   **Liked Songs:** Identifies liked songs present on one service but missing on others.
    *   **Playlists:** Identifies playlists by name that are missing on certain services. It also analyzes tracks within commonly named playlists to find missing songs in each version.
*   **Manual Synchronization:**
    *   Add missing liked songs to a target service.
    *   Create missing playlists on a target service.
    *   Add missing tracks to existing playlists on a target service.
*   **Automated Background Synchronization:** Periodically (e.g., every 4 hours by default) runs an automated cycle to:
    *   Analyze differences in liked songs and playlists.
    *   Automatically attempt to add missing liked songs.
    *   Automatically attempt to create missing playlists.
    *   Automatically attempt to add missing tracks to existing common playlists.
*   **Persistent Token Storage:** Authentication tokens are stored persistently in a local `tokens.json` file, surviving application restarts. Includes basic refresh token handling for Spotify and YouTube.
*   **Logging:** Comprehensive logging to both console and a `music_sync.log` file for monitoring and debugging.

## Setup Instructions

### 1. Prerequisites

*   **Python:** Version 3.9 or newer is recommended.
*   **pip:** Python's package installer, usually included with Python. ([Install pip](https://pip.pypa.io/en/stable/installation/))
*   **Git:** For cloning the repository.

### 2. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 3. Install Python Dependencies

Navigate to the application's root directory (where `requirements.txt` is located, likely inside `music_sync_app` or the main repo root if `music_sync_app` is the module name) and run:

```bash
pip install -r music_sync_app/requirements.txt
```
*(Adjust path to `requirements.txt` if it's in the repo root: `pip install -r requirements.txt`)*

### 4. API Credentials Setup

You need to set up developer applications and obtain credentials for each music service.

*   **Spotify:**
    1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    2.  Create a new App.
    3.  Note your **Client ID** and **Client Secret**.
    4.  Edit Settings: Add a **Redirect URI**. For local development, this should be `http://localhost:8000/callback/spotify`.

*   **Deezer:**
    1.  Go to [Deezer Developers](https://developers.deezer.com/myapps).
    2.  Create a new Application.
    3.  Note your **Application ID** (App ID) and **Secret Key**.
    4.  Set the **Application Domain** (e.g., `localhost`).
    5.  Set the **Redirect URI after authentication** to `http://localhost:8000/callback/deezer`.

*   **YouTube Music (Google Cloud Console):**
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  Create a new project (or select an existing one).
    3.  **Enable the YouTube Data API v3:**
        *   Navigate to "APIs & Services" > "Library".
        *   Search for "YouTube Data API v3" and enable it for your project.
    4.  **Create OAuth 2.0 Client ID:**
        *   Navigate to "APIs & Services" > "Credentials".
        *   Click "+ CREATE CREDENTIALS" > "OAuth client ID".
        *   Select "Web application" as the Application type.
        *   Give it a name (e.g., "Music Sync App Client").
        *   Under "Authorized JavaScript origins", add `http://localhost:8000` (if you plan to run the app on this origin).
        *   Under "Authorized redirect URIs", add `http://localhost:8000/callback/youtube`.
        *   Click "CREATE".
    5.  **Download Client Secret JSON:** After creation, a dialog will show your Client ID and Client Secret. Click "DOWNLOAD JSON" to get the client secrets file. Rename this file to `client_secret_youtube.json`.

### 5. Configure the Application (`music_sync_app/config.py`)

1.  Open the `music_sync_app/config.py` file.
2.  Fill in your credentials obtained in the previous step into the corresponding placeholder variables:
    *   `SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"`
    *   `SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"`
    *   `SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback/spotify"` (Ensure this matches your Spotify app settings)

    *   `DEEZER_APP_ID = "YOUR_DEEZER_APP_ID"`
    *   `DEEZER_APP_SECRET = "YOUR_DEEZER_APP_SECRET"`
    *   `DEEZER_REDIRECT_URI = "http://localhost:8000/callback/deezer"` (Ensure this matches your Deezer app settings)

    *   `GOOGLE_OAUTH_CLIENT_SECRETS_FILE = "client_secret_youtube.json"` (This is the name of the file you downloaded and renamed).
    *   `YOUTUBE_REDIRECT_URI = "http://localhost:8000/callback/youtube"` (Ensure this matches your Google Cloud OAuth client settings).
    *   (Optional) `YOUTUBE_API_KEY` can be set if you need direct, non-OAuth API access for public data, but it's not used for user data synchronization.

3.  **Place `client_secret_youtube.json`:**
    *   Put the downloaded and renamed `client_secret_youtube.json` file into the `music_sync_app` directory (or the same directory as your `config.py` and `main.py` if your structure differs, ensuring the path matches `GOOGLE_OAUTH_CLIENT_SECRETS_FILE` in `config.py`).

### 6. Token Storage and Logging Files

*   **`tokens.json`:** This file will be created automatically in the application's root directory (where `main.py` is run) when you first authenticate with the services. It stores your OAuth tokens.
*   **`music_sync.log`:** This file will also be created in the application's root directory and will contain detailed logs of the application's activity.

**Important for Git Users:** If you are versioning your instance of this application, add `tokens.json` and `*.log` (or specifically `music_sync.log`) to your `.gitignore` file to prevent committing sensitive tokens and large log files:
```
# .gitignore
tokens.json
*.log
music_sync.log
```

## Running the Application

1.  Ensure your current working directory is the root of the repository (e.g., the directory containing the `music_sync_app` folder).
2.  Run the FastAPI application using Uvicorn:

    ```bash
    python -m uvicorn music_sync_app.main:app --reload --port 8000
    ```
    *(If your main.py is in the root and your app module is `main:app`, adjust accordingly. The command above assumes `main.py` is inside `music_sync_app` which acts as a Python package).*

    Alternatively, if `main.py` includes `uvicorn.run(app, ...)` in its `if __name__ == "__main__":` block, you might be able to run it directly (though this is generally for development):
    ```bash
    python music_sync_app/main.py
    ```

3.  Open your web browser and go to: `http://localhost:8000`

## How to Use

1.  **Login:** On the main page, you'll see sections for Spotify, Deezer, and YouTube. Click the "Login" button for each service you want to use. This will redirect you to the service's authentication page. Authorize the application.
2.  **View Profile (Optional):** After logging in, you can click "View Profile" links to see basic information retrieved from the service, confirming your login status.
3.  **View Library Data (Optional):** Use the "View Liked Songs" or "View Playlists" buttons in each service section to load and display these items directly on the page using HTMX.
4.  **Analyze Liked Songs:**
    *   Click the "Analyze Liked Songs Differences" button in the "Liked Songs Synchronization" section.
    *   The results will show songs missing from each service.
    *   For each proposed addition, click the "Add to [Service]" button to attempt to find and add that song to the target service's liked songs. Status messages will appear next to each button.
5.  **Analyze Playlists:**
    *   Click the "Analyze Playlist Differences" button in the "Playlist Synchronization" section.
    *   The results will show:
        *   **Proposed Playlist Creations:** Playlists found on one service but not others, with buttons to "Create on [Service]".
        *   **Proposed Track Additions:** Tracks found in a common playlist on one service but missing from another service's version of that same playlist. Buttons allow you to "Add to [Service] Playlist".
    *   Status messages will appear for each action.
6.  **Automated Background Sync:**
    *   The application automatically runs a synchronization cycle in the background (default: every 4 hours).
    *   This cycle performs the analysis and then *executes* the proposed additions for liked songs, playlist creations, and track additions to playlists.
    *   Progress and errors for the background sync are logged to `music_sync.log` and the console.

## Known Limitations / Future Work

*   **Token Stability:** While refresh tokens are used, long-term non-interactive refresh for the automated background sync might eventually fail for some services, requiring manual re-authentication via the web UI.
*   **No Deletion/Removal Sync:** The current synchronization logic only handles additions (new liked songs, new playlists, new tracks to playlists). It does not remove items from a target service if they are removed from a source service.
*   **Basic Error Reporting in UI:** While backend logging is comprehensive, error messages displayed in the UI for failed actions are sometimes basic.
*   **No Advanced Conflict Resolution:** For playlists with slightly different names or tracks with very different metadata, the matching logic is based on normalization and might not always be perfect. No manual conflict resolution interface exists.
*   **YouTube Music Specifics:** YouTube Music operates on top of YouTube videos. "Liked songs" are "Liked videos" (often from the "LM" auto-generated playlist). Track matching relies on video titles and channel information, which can be less precise than ISRC-based matching on Spotify/Deezer.
*   **Scalability:** For extremely large libraries (tens of thousands of songs/playlists), the current analysis and UI display methods might become slow. Pagination for UI displays is basic.
*   **Security of `tokens.json`:** The `tokens.json` file stores sensitive OAuth tokens. While convenient for a local application, ensure the file has restricted permissions on your system. For a deployed application, a more secure token storage mechanism (e.g., encrypted database, environment variables, or a secrets manager) would be essential.

## Project Structure (Simplified)

```
.
├── music_sync_app/
│   ├── __init__.py
│   ├── config.py                 # API keys and configuration settings
│   ├── deezer_client.py          # Deezer API interaction logic
│   ├── logging_config.py         # Logging setup
│   ├── main.py                   # FastAPI application, UI endpoints, main logic
│   ├── requirements.txt          # Python dependencies
│   ├── spotify_client.py         # Spotify API interaction logic
│   ├── sync_manager.py           # Core synchronization analysis and action logic
│   ├── token_store.py            # Persistent token storage (tokens.json)
│   ├── youtube_client.py         # YouTube/Google API interaction logic
│   └── templates/                # HTML templates for the web interface
│       ├── index.html            # Main page
│       ├── _proposed_sync_actions.html  # Partial for liked song sync results
│       ├── _proposed_playlist_sync_actions.html # Partial for playlist sync results
│       └── _service_items_display.html # Partial for displaying lists of items
├── music_sync.log                # Log file (auto-generated, in .gitignore)
└── tokens.json                   # Persistent token storage (auto-generated, in .gitignore)
└── README.md                     # This file
```

---

This README aims to provide a good starting point. Depending on further development or specific deployment needs, sections might need to be added or expanded.
