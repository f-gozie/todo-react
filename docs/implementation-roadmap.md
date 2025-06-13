# Music Sync Hub – Full Implementation Roadmap

> **Goal** – Transform the current infrastructure-ready codebase into a feature-complete, production-ready application you can demo end-to-end (user logs in, connects Spotify/YouTube, synchronises playlists & liked songs, views status in the UI).

This document lists **every major deliverable** still outstanding, ordered by logical sequence.  Each item contains:

* **Why** – rationale / symptoms if missing.
* **What** – exact code, modules, tooling, configs to touch.
* **How** – concrete implementation steps (file paths, commands).
* **Definition of Done** (DoD).

---

## 0. Foundational Clean-up (quick wins)

| ID | Task | Time | Notes |
|----|------|------|-------|
| 0.1 | Remove legacy Jinja routes (or return JSON) | 15 min | Prevent 500s on `/` before React is ready. |
| 0.2 | Delete `backend/app/templates/` & related code | 5 min | Legacy HTMX UI is obsolete. |
| 0.3 | Create **`docs/`** directory for all markdown specs (this file lives here) | — | Maintains clean repo structure. |
| 0.4 | Add pre-commit `markdownlint` (optional) | 5 min | Enforces doc style. |

---

## 1. Database Layer (Task 3)

### 1.1 Why
* We currently run **PostgreSQL** container but **no tables**.
* Sync logic still stores everything in memory → cannot persist sessions, tokens, or sync history.

### 1.2 What
* Add **SQLAlchemy 2.0** models, Pydantic schemas, Alembic migrations, repository pattern.
* Tables:
  * `users` – auth core
  * `user_platform_accounts` – OAuth tokens per service
  * `playlists`, `tracks`, `playlist_tracks`
  * `sync_history` – each sync run
  * `user_preferences`
* Utility: base model mixin with `id`, `created_at`, `updated_at` (trigger uses `update_updated_at_column()` already defined).
* Environment variables already prepared (`DATABASE_URL`).

### 1.3 How (step-by-step)
1. **Dependencies**
   ```bash
   poetry add "sqlalchemy[asyncio]>=2" alembic psycopg2-binary asyncpg
   ```
   or append to `backend/pyproject.toml`.
2. **Folder** `backend/app/db/`
   * `session.py` – async engine + session factory (`async_sessionmaker`).
   * `base.py` – `DeclarativeBase` subclass.
3. **Models** in `backend/app/models/`.
4. **Repositories** in `backend/app/repositories/`.
5. **Pydantic schemas** in `backend/app/schemas/`.
6. **Alembic**
   * `alembic init migrations`
   * Edit `alembic.ini` → `sqlalchemy.url=${DATABASE_URL}`.
   * Generate first migration: `alembic revision --autogenerate -m "initial"`.
   * Update `docker-compose` backend command to run `alembic upgrade head` before Uvicorn.
7. **FastAPI dependency** that yields DB session per request.

### 1.4 DoD
* `make up-logs` shows Alembic creating tables on first run.
* `/health` augmented with `postgres=True` check (simple "SELECT 1").

---

## 2. Authentication (Tasks 4-6, 25)

### 2.1 Why
* OAuth flows exist but there's **no JWT login system**; sessions stored in RAM.
* Need MFA + Redis-backed sessions.

### 2.2 What
* Use **FastAPI Users** _or_ hand-rolled JWT (PyJWT / python-jose).
* Endpoints: `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/mfa/verify`.
* Store user password hash with `passlib[bcrypt]`.
* **Redis** for refresh-token blacklist + session cache.
* MFA: time-based one-time passwords (TOTP via `pyotp`).

### 2.3 How
1. Add deps: `python-jose[cryptography]`, `passlib[bcrypt]`, `pyotp`, `fastapi-users[sqlalchemy,redis]`.
2. Create `app/core/security.py` – token creation / validation.
3. Create `app/api/auth.py` endpoints.
4. Update Makefile `health` to call protected endpoint with token.

### 2.4 DoD
* Login returns access + refresh tokens.
* Accessing `/api/users/me` returns user object.
* MFA flow enabled behind env flag.

---

## 3. OAuth (PKCE) (Task 5)

* Replace plain OAuth with `oauthlib` PKCE helper.
* Update Spotify/YT auth URLs, store `code_verifier` in Redis keyed by state.
* Validate code_challenge in callback.

---

## 4. Repository & Service Layers (Tasks 8-9, 17-19)

### Highlights
* Move sync logic into `app/services/sync_service.py` with clear interface.
* Platform adapters (`spotify_adapter.py`, `youtube_adapter.py`, future Apple/Deezer).
* All third-party calls async.
* Celery tasks `sync.liked_songs`, `sync.playlists` accept user_id.

---

## 5. Error Handling & Middleware (Task 10)

* Global `app.middleware("http")` that catches exceptions → JSON body.
* RateLimiter using `slowapi` (Redis backend).
* Sentry ASGI middleware (env `SENTRY_DSN`).

---

## 6. Frontend (Tasks 11-16, 24)

### 6.1 Project Setup Status
* **Vite + React 18 + TS** skeleton exists, but **no pages/components yet**.
* Nginx serves built app; proxy path `/api` points to backend.

### 6.2 Required Pages & Features
| Page | Route | Components |
|------|-------|------------|
| Auth | `/login` `/register` | `<AuthForm>` `<OAuthButton service="spotify"/>` |
| Dashboard | `/dashboard` | `<AccountStatusCard>`, `<SyncNowButton>` |
| Playlists | `/playlists` | `<PlaylistTable>` `<SyncStatusTag>` |
| Liked Songs | `/liked` | `<SongTable>` |
| Settings | `/settings` | MFA toggle, API key management |

### 6.3 State Management
* Recommend **Zustand** or **Redux Toolkit**.  RTK Query → backend `/api`.
* React Query already listed as dep; either can coexist.

### 6.4 API layer (`src/services/api.ts`)
* Axios instance with interceptor that injects JWT access token from localStorage and refreshes when 401.

### 6.5 Routing (`react-router-dom v6`)
* Setup protected routes component (`<RequireAuth>`).

### 6.6 Styling
* TailwindCSS already installed; run `npx tailwindcss init -p` and add paths.

### 6.7 Environment Vars
* In `.env` → `VITE_API_BASE_URL`, `VITE_SPOTIFY_CLIENT_ID` if needed client-side.

### 6.8 Testing (Task 24)
* Vitest + RTL for components.

### 6.9 DoD
* End-to-end flow:
  1. Register user.
  2. Login → dashboard shows "Connect Spotify"/"Connect YouTube".
  3. Click connect → PKCE flow passes, backend stores tokens.
  4. Click **Sync Now** → Celery task enqueued, status visible.
  5. Playlists/Liked pages list combined data.

---

## 7. Monitoring & Observability (Task 21)

* Add **Prometheus FastAPI instrumentation**.
* Grafana docker-compose service (optional).
* Flower now works (port 5555) – ensure exposed in README.

---

## 8. CI/CD (Task 22)

* GitHub Actions workflow matrix: lint → test → build docker → push.
* Cache Docker layers with `actions/cache`.

---

## 9. Kubernetes & Helm (Task 23)

* Write Helm chart values for config secrets, env vars.
* Use PostgreSQL/Redis operators or external managed services.

---

## 10. Documentation Polish

* Update main `README.md` quick-start flow after UI is ready.
* Publish OpenAPI docs snapshot.

---

## ⌚ Suggested Timeline

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| **Phase 1** | 0.x + 1.x + 2.x | 3–4 days |
| **Phase 2** | 3.x + 4.x + 5.x | 3 days |
| **Phase 3** | 6.x (frontend UI) | 5 days |
| **Phase 4** | 7.x + 8.x + 9.x | 2 days |
| **Total** | — | **~13-14 dev days** |

---

## 🔑 Key Milestone to Demo

1. **Backend API stable** (Phases 1–2).  Use Swagger to call `/sync/analyze` manually.
2. **React auth + dashboard working** (Phase 3 partial).  User can:
   * Register, login
   * Connect Spotify/YouTube
   * Trigger sync and see result status text (manual refresh OK)
3. **🎉 Demo** – run `make up-logs`, open `http://localhost:3000`, record screencast.

---

### Appendix – Repo Checklist Before Demo

- [ ] `README.md` top badges updated (build passing).
- [ ] `.env.example` values validated.
- [ ] `docker-compose.yml` starts clean with `make up-logs`.
- [ ] Flower UI reachable at `:5555`.
- [ ] Swagger UI reachable at `:8000/api/docs`.
- [ ] React build (`npm run build`) produces assets served by Nginx.

---

> **Next step in this chat** – decide which chunk you'd like to implement first (DB models, auth, or initial React scaffolding). 