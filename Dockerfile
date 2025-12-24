FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (some packages need compilation). Keep image small afterwards.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
# Install requirements and ensure gunicorn (>=20.1.0) is available for the CMD
RUN pip install --no-cache-dir -r requirements.txt "gunicorn>=20.1.0"

# Copy app sources
COPY . .

# Run as non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Use gunicorn for production serving; adjust workers as needed
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
