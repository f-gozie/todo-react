# Music Sync Hub

A modern web application for synchronizing your liked songs across Spotify, Deezer, and YouTube Music platforms.

![Music Sync Hub](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Multi-Platform Support**: Connect and manage your music across Spotify, Deezer, and YouTube Music
- **Liked Songs Synchronization**: Analyze differences in your liked songs across platforms and sync them with one click
- **Beautiful UI**: Modern, futuristic interface with glassmorphism effects and smooth animations
- **Playlist Management**: View and manage playlists from all connected services
- **User Profiles**: Access your profile information from each music service
- **Real-time Search**: Search through your liked songs instantly
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3 (with glassmorphism), JavaScript
- **APIs**: Spotify Web API, Deezer API, YouTube Data API v3
- **UI Framework**: HTMX for dynamic interactions
- **Authentication**: OAuth 2.0 for all platforms

## Prerequisites

- Python 3.8 or higher
- API credentials for:
  - [Spotify Developer App](https://developer.spotify.com/dashboard)
  - [Deezer Application](https://developers.deezer.com/myapps)
  - [Google Cloud Console Project](https://console.cloud.google.com/) with YouTube Data API v3 enabled

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/music-sync-hub.git
   cd music-sync-hub
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**

   Create a `config.py` file in the project root:
   ```python
   # Spotify Configuration
   SPOTIFY_CLIENT_ID = "your_spotify_client_id"
   SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
   SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback/spotify"
   SPOTIFY_SCOPES = "user-library-read user-library-modify playlist-read-private user-read-private user-read-email"

   # Deezer Configuration
   DEEZER_APP_ID = "your_deezer_app_id"
   DEEZER_APP_SECRET = "your_deezer_app_secret"
   DEEZER_REDIRECT_URI = "http://localhost:8000/callback/deezer"

   # YouTube Configuration
   YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", 
                     "https://www.googleapis.com/auth/youtube"]
   YOUTUBE_REDIRECT_URI = "http://localhost:8000/callback/youtube"
   ```

5. **Set up YouTube credentials**
   - Download your OAuth 2.0 credentials from Google Cloud Console
   - Save as `client_secret_youtube.json` in the project root

## Usage

1. **Start the application**
   ```bash
   python -m uvicorn main:app --reload
   ```
   Or directly:
   ```bash
   python main.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

3. **Connect your accounts**
   - Click on "Connect" for each service you want to sync
   - Authorize the application to access your music data
   - The connection status will be indicated by a green dot

4. **Sync your liked songs**
   - Click "Analyze Song Differences" to compare your libraries
   - Review the proposed sync actions
   - Click "Add" buttons to sync individual songs to specific platforms

## Project Structure

```
music_sync_app/
├── main.py                 # Main FastAPI application
├── config.py              # Configuration file (create this)
├── spotify_client.py      # Spotify API integration
├── deezer_client.py       # Deezer API integration
├── youtube_client.py      # YouTube API integration
├── sync_manager.py        # Synchronization logic
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html        # Home page
│   ├── profile.html      # User profile page
│   ├── liked_songs.html  # Liked songs page
│   ├── playlists.html    # Playlists page
│   └── _proposed_sync_actions.html  # Sync results partial
└── client_secret_youtube.json  # YouTube OAuth credentials
```

## API Endpoints

### Authentication
- `GET /login/{service}` - Initiate OAuth flow
- `GET /callback/{service}` - Handle OAuth callback

### User Data
- `GET /me/{service}` - View user profile
- `GET /{service}/liked-songs` - View liked songs
- `GET /{service}/playlists` - View playlists
- `GET /{service}/playlists/{id}/tracks` - Get playlist tracks

### Synchronization
- `POST /sync/liked/analyze` - Analyze differences between platforms
- `POST /sync/liked/add` - Add a song to a specific platform

## Security Considerations

- Never commit your `config.py` or `client_secret_youtube.json` files
- Use environment variables for production deployments
- Tokens are stored in memory only (consider using Redis for production)
- All OAuth flows use state parameters to prevent CSRF attacks

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes

### Testing
```bash
# Run tests (when implemented)
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Spotipy](https://spotipy.readthedocs.io/) for Spotify API wrapper
- [HTMX](https://htmx.org/) for making dynamic UIs simple
- All the music platforms for providing their APIs

## Troubleshooting

### Common Issues

1. **OAuth Error**: Make sure your redirect URIs match exactly in both your code and app settings
2. **API Rate Limits**: The app implements basic rate limiting, but you may hit platform limits with heavy usage
3. **Token Expiration**: Tokens are refreshed automatically, but you may need to re-login occasionally

### Support

For issues and questions, please create an issue on GitHub. 