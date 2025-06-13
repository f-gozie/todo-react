# Development Guidelines

The project includes a set of rules under `.cursor/rules/music-sync-hub.mdc`. Key points:

- **Use `make` commands** for all tooling. Avoid invoking Python, Node, or lint/test commands directly. Examples include `make up`, `make test`, and `make lint-fix`.
- **Backend tests** should run via `make test-backend`.
- **Frontend tests** should run via `make test-frontend`.
- **Linting** is done with `make lint` (or `make lint-fix` for auto-fixes).
- The folder `music_sync_app/` is a **legacy implementation** and is usually ignored during development.

## Commits and Documentation

- Follow **conventional commits** for commit messages.
- If you change any API behaviour or environment variables, update the documentation accordingly.
