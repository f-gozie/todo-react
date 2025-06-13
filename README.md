# 🎵 Music Sync Hub

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/music-sync-hub/music-sync-hub)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)](https://github.com/music-sync-hub/music-sync-hub/actions)

> **Synchronize your music libraries across streaming platforms with ease**

A modern, production-ready web application for synchronizing music libraries across multiple streaming platforms including Spotify, YouTube Music, and more. Built with FastAPI backend and React frontend.

## ✨ Features

### 🔄 **Multi-Platform Synchronization**
- **Spotify & YouTube Music** support with more platforms coming
- **Bidirectional sync** with intelligent conflict resolution
- **Selective synchronization** - choose what to sync
- **Automated scheduling** for hands-off maintenance

### 🔐 **Enterprise-Grade Security**
- **JWT authentication** with refresh tokens
- **OAuth2 with PKCE** for enhanced security
- **Multi-factor authentication** support
- **Rate limiting** and DDoS protection
- **GDPR compliant** data handling

### 🎨 **Modern User Experience**
- **React + TypeScript** frontend
- **Real-time sync progress** indicators
- **Drag-and-drop** playlist management
- **Mobile-responsive** design
- **Dark/light theme** support
- **Accessibility compliant** (WCAG 2.1)

### 🚀 **Production Ready**
- **PostgreSQL** database with Redis caching
- **Celery** background job processing
- **Docker** containerization
- **Kubernetes** deployment ready
- **Comprehensive monitoring** and logging
- **95% test coverage** target

## 🏗️ Architecture

```
music-sync-hub/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and settings
│   │   ├── db/             # Database models and connections
│   │   ├── models/         # Pydantic models and schemas
│   │   ├── services/       # Business logic and external APIs
│   │   └── utils/          # Utility functions and helpers
│   ├── tests/              # Backend test suite
│   ├── migrations/         # Database migrations
│   └── pyproject.toml      # Python dependencies and config
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components and routing
│   │   ├── services/       # API clients and external services
│   │   ├── store/          # State management (Redux)
│   │   ├── styles/         # CSS and styling
│   │   └── utils/          # Frontend utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies and scripts
├── docker-compose.yml      # Local development setup
├── kubernetes/             # K8s deployment manifests
└── docs/                   # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** and **Node.js 18+**
- **PostgreSQL 14+** and **Redis 6+**
- **Docker** and **Docker Compose** (recommended)

### 🐳 Docker Development (Recommended)

```bash
# Clone the repository
git clone https://github.com/music-sync-hub/music-sync-hub.git
cd music-sync-hub

# Quick setup with environment variables
make setup

# Edit .env file with your API credentials
# (Spotify, YouTube, etc.)

# Build and start all services
make build
make up

# Or build and start with logs
make up-logs

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Celery Flower (monitoring): http://localhost:5555
```

### 🔧 Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev

# The frontend will be available at http://localhost:3000
```

## 🔐 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/music_sync_hub
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# External Services
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

### API Credentials Setup

1. **Spotify Developer App**
   - Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app and get your Client ID and Secret

2. **YouTube Data API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials

## 📊 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```bash
# Authentication
POST /auth/login              # User login
POST /auth/register           # User registration
POST /auth/refresh            # Refresh access token

# Platform Connections
GET  /platforms               # List connected platforms
POST /platforms/spotify/connect     # Connect Spotify
POST /platforms/youtube/connect     # Connect YouTube

# Synchronization
POST /sync/analyze            # Analyze sync differences
POST /sync/execute            # Execute synchronization
GET  /sync/history            # Sync history

# User Management
GET  /users/me                # Current user profile
PUT  /users/me                # Update user profile
```

## 🐳 Docker Operations

### Development Commands

```bash
# Start services
make up                 # Start in background
make up-logs           # Start with logs

# Stop services
make down              # Stop all services
make restart           # Restart all services

# View logs
make logs              # All services
make logs-backend      # Backend only
make logs-frontend     # Frontend only
make logs-db           # Database only

# Access shells
make shell-backend     # Backend container bash
make shell-frontend    # Frontend container shell
make db-shell         # PostgreSQL shell
make redis-shell      # Redis CLI

# Health checks
make health           # Check all services
make ps              # Show running containers
```

### Database Operations

```bash
# Database management
make db-backup        # Create backup
make db-restore BACKUP_FILE=backup.sql
make redis-flush      # Clear Redis cache
```

## 🧪 Testing

### Backend Tests

```bash
# Local testing
cd backend
pytest
pytest --cov=app --cov-report=html

# Docker testing
make test-backend
make test-coverage
```

### Frontend Tests

```bash
# Local testing
cd frontend
npm test
npm run test:coverage

# Docker testing
make test-frontend
make test
```

## 🚢 Deployment

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -l app=music-sync-hub
```

## 🔧 Development

### Code Quality

```bash
# Run all quality checks
npm run lint          # Lint all code
npm run format        # Format all code
npm run type-check    # TypeScript type checking

# Backend specific
cd backend
black .               # Format Python code
ruff check .          # Lint Python code
mypy app              # Type checking
```

### Git Hooks

Pre-commit hooks are automatically installed to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/health/detailed
```

### Metrics

- **Prometheus metrics**: http://localhost:8000/metrics
- **Application logs**: Available in `backend/logs/`
- **Performance monitoring**: Integrated with Sentry

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use type hints, 90%+ test coverage
- **TypeScript**: Strict mode, ESLint + Prettier, comprehensive testing
- **EditorConfig**: Consistent indentation and line endings via [.editorconfig](.editorconfig)
- **Git**: Conventional commits, meaningful commit messages
- **Documentation**: Update docs for any API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [Spotipy](https://spotipy.readthedocs.io/) - Spotify API wrapper
- [Google APIs](https://developers.google.com/youtube/v3) - YouTube integration

## 📞 Support

- **Documentation**: [docs.musicsync.hub](https://docs.musicsync.hub)
- **Issues**: [GitHub Issues](https://github.com/music-sync-hub/music-sync-hub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/music-sync-hub/music-sync-hub/discussions)

---

<div align="center">
  <p>Built with ❤️ by the Music Sync Hub team</p>
  <p>
    <a href="https://github.com/music-sync-hub/music-sync-hub">⭐ Star us on GitHub</a> •
    <a href="https://twitter.com/musicsync_hub">🐦 Follow on Twitter</a> •
    <a href="https://discord.gg/musicsync">💬 Join Discord</a>
  </p>
</div>
