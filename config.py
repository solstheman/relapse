import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///relapse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
