# Relapse API

This is a minimal Flask API for Relapse — shared albums that unlock after a configured date/time.

Environment variables
- `DATABASE_URL` (optional): SQLAlchemy database URI. Defaults to `sqlite:///relapse.db`.
- `AWS_S3_BUCKET`: S3 bucket name (required for photo uploads).
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS credentials/config.

Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run

```bash
export AWS_S3_BUCKET=your-bucket
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
python app.py
```

Endpoints
- `POST /photo/save` — multipart form with `file` (required) and optional `event_uuid`. Provide `X-User-Id` header (or `user_id` form field). Returns presigned URL.
- `POST /event/create` — JSON with `process_datetime` (ISO format) and optional `name`. Returns `event_uuid`.
- `GET /event/view/<event_uuid>` — If now is before `process_datetime` returns 201 and `{"message": "photos not ready"}`; otherwise returns list of photos for event.
- `GET /photos/view` — Provide `X-User-Id` header (or `user_id` query param) to list all user photos.

Notes
- This is a minimal starting implementation. It uses presigned URLs that expire after 1 hour.
- Authentication is intentionally minimal (X-User-Id header). Replace with proper auth for production.
