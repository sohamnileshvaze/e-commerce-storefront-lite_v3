# Foundation Module

Provides shared configuration, logging, security helpers, and exception middleware for the E-Commerce Storefront Lite backend. It does not register routers or start the application; other modules import this package for reusable utilities.

## Configuration
- `JWT_SECRET_KEY` must be set in the environment or `.env` before importing `app.core.config`. See `.env.example` for guidance.
- Defaults: SQLite database at `sqlite:///./ecommerce.db`, JWT algorithm `HS256`, access token lifetime 60 minutes, CORS origin `http://localhost:3000`.

## Logging
- `app.core.logger` configures a rotating file handler at `./logs/app.log` (5 MB max, 3 backups) and a console handler. Logs exclude sensitive data such as passwords and secrets.

## Security
- `app.core.security` exposes password hashing/verification and JWT creation/decoding using bcrypt and HS256 via `python-jose`.
- Use `get_password_hash`, `verify_password`, `create_access_token`, and `decode_access_token` directly where needed.

## Exception Handling
- Wire `app.http_exception_handler` as the FastAPI `HTTPException` handler to return consistent JSON error payloads.
