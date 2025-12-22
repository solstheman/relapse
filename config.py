import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///relapse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Google Cloud Storage configuration
    GCP_BUCKET = os.getenv("GCP_BUCKET")
    # Optional path to service account JSON file. If not provided, the client
    # will use Application Default Credentials (ADC).
    GCP_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
