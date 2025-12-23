import os
import io
import uuid
from datetime import datetime, timezone
from dateutil import parser as dateparser
from flask import Flask, request, jsonify, send_file
try:
    from google.cloud import storage
    from google.oauth2 import service_account
except Exception:
    storage = None
    service_account = None

from datetime import timedelta

from dotenv import load_dotenv

# Load .env from the repository root so environment variables are available
# to `Config` and the rest of the app.
load_dotenv()

from config import Config
from models import db, Event, Photo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Ensure database tables exist (create within app context)
    with app.app_context():
        db.create_all()

    # GCS client configured from environment
    gcs_bucket_name = app.config.get('GCP_BUCKET')
    gcs_client = None
    if storage is None:
        app.logger.warning('google-cloud-storage not installed; GCS operations will fail')
    else:
        creds_path = app.config.get('GCP_CREDENTIALS_JSON')
        try:
            if creds_path and service_account is not None:
                creds = service_account.Credentials.from_service_account_file(creds_path)
                gcs_client = storage.Client(credentials=creds)
            else:
                gcs_client = storage.Client()
        except Exception as e:
            app.logger.exception('Failed to create GCS client: %s', e)


    def generate_signed_url(key, expires_in=3600):
        if gcs_client is None or not gcs_bucket_name:
            return None
        try:
            bucket = gcs_client.bucket(gcs_bucket_name)
            blob = bucket.blob(key)
            url = blob.generate_signed_url(expiration=timedelta(seconds=expires_in), version='v4')
            return url
        except Exception:
            return None

    @app.route('/photo/save', methods=['POST'])
    def photo_save():
        user_id = request.headers.get('X-User-Id') or request.form.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing X-User-Id header or user_id form field"}), 400

        if 'file' not in request.files:
            return jsonify({"error": "file is required"}), 400

        file = request.files['file']
        event_uuid = request.form.get('event_uuid') or request.args.get('event_uuid')
        event = None
        if event_uuid:
            event = Event.query.filter_by(uuid=event_uuid).first()
            if not event:
                return jsonify({"error": "event_uuid not found"}), 400

        # Build key
        ext = os.path.splitext(file.filename)[1] or ''
        key = f"photos/{user_id}/{uuid.uuid4()}{ext}"
        bucket_name = gcs_bucket_name
        if not bucket_name or gcs_client is None:
            return jsonify({"error": "GCS bucket not configured or client unavailable (set GCP_BUCKET and provide credentials)"}), 500
        try:
            bucket = gcs_client.bucket(bucket_name)
            blob = bucket.blob(key)
            # upload_from_file accepts a file-like object
            blob.upload_from_file(file.stream, content_type=(file.mimetype or 'application/octet-stream'))
        except Exception as e:
            return jsonify({"error": "Failed to upload to GCS", "details": str(e)}), 500

        photo = Photo(user_id=user_id, event_id=(event.id if event else None), s3_key=key, content_type=file.mimetype)
        db.session.add(photo)
        db.session.commit()

        url = generate_signed_url(key)
        return jsonify({"photo_id": photo.id, "url": url}), 201

    @app.route('/event/create', methods=['POST'])
    def event_create():
        data = request.get_json(force=True, silent=True) or {}
        name = data.get('name')
        process_dt = data.get('process_datetime')
        if not process_dt:
            return jsonify({"error": "process_datetime is required in ISO format"}), 400

        try:
            dt = dateparser.parse(process_dt)
            if dt.tzinfo is None:
                # assume UTC
                dt = dt.replace(tzinfo=timezone.utc)
            # store naive UTC for compatibility with SQLite; convert to UTC
            dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception as e:
            return jsonify({"error": "Invalid process_datetime", "details": str(e)}), 400

        event = Event(name=name, process_datetime=dt_utc)
        db.session.add(event)
        db.session.commit()
        return jsonify({"event_uuid": event.uuid}), 201

    @app.route('/event/view/<string:event_uuid>', methods=['GET'])
    def event_view(event_uuid):
        event = Event.query.filter_by(uuid=event_uuid).first()
        if not event:
            return jsonify({"error": "Event not found"}), 404

        # Compare current UTC (naive) with stored naive UTC
        now = datetime.utcnow()
        if now < event.process_datetime:
            return jsonify({"message": "photos not ready"}), 201

        photos = Photo.query.filter_by(event_id=event.id).order_by(Photo.created_at.asc()).all()
        items = []
        for p in photos:
            url = generate_presigned_url(p.s3_key)
            items.append({"photo_id": p.id, "url": url, "created_at": p.created_at.isoformat()})
        return jsonify({"event": event.uuid, "photos": items}), 200

    @app.route('/photos/view', methods=['GET'])
    def photos_view():
        user_id = request.headers.get('X-User-Id') or request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing X-User-Id header or user_id query param"}), 400

        photos = Photo.query.filter_by(user_id=user_id).order_by(Photo.created_at.desc()).all()
        items = []
        for p in photos:
            url = generate_presigned_url(p.s3_key)
            items.append({"photo_id": p.id, "url": url, "event_uuid": (p.event.uuid if p.event else None), "created_at": p.created_at.isoformat()})
        return jsonify({"user_id": user_id, "photos": items}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
