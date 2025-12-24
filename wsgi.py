from app import create_app

# Expose a WSGI callable named "app" for Gunicorn
app = create_app()
