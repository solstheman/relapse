# Relapse API

This is a minimal Flask API for Relapse — shared albums that unlock after a configured date/time.

Environment variables
- `DATABASE_URL` (optional): SQLAlchemy database URI. Defaults to `sqlite:///relapse.db`.
- `GCP_BUCKET`: Google Cloud Storage bucket name (required for photo uploads).
- `GOOGLE_APPLICATION_CREDENTIALS` (optional): path to a service account JSON file. If not set, Application Default Credentials will be used.

Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run

```bash
export GCP_BUCKET=your-bucket
# Optionally set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
python app.py
```

Endpoints
- `POST /photo/save` — multipart form with `file` (required) and optional `event_uuid`. Provide `X-User-Id` header (or `user_id` form field). Returns a signed URL for temporary access.
- `POST /event/create` — JSON with `process_datetime` (ISO format) and optional `name`. Returns `event_uuid`.
- `GET /event/view/<event_uuid>` — If now is before `process_datetime` returns 201 and `{"message": "photos not ready"}`; otherwise returns list of photos for event.
- `GET /photos/view` — Provide `X-User-Id` header (or `user_id` query param) to list all user photos.

Notes
- This is a minimal starting implementation. It uses presigned URLs that expire after 1 hour.
- Authentication is intentionally minimal (X-User-Id header). Replace with proper auth for production.
