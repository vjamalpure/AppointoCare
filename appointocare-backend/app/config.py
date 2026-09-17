import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", 30)))
    JWT_TOKEN_LOCATION = ["headers", "json"]
    JWT_REFRESH_JSON_KEY = "refresh_token"
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",") if origin.strip()]
    RAZORPAY_ENABLED = os.getenv("RAZORPAY_ENABLED", "false").lower() == "true"
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mock" if APP_ENV != "production" else "none")
    WHATSAPP_ENABLED = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
    WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "mock" if APP_ENV != "production" else "none")
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "mock" if APP_ENV != "production" else "none")
    EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "AppointoCare")
    SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "mock" if APP_ENV != "production" else "none")
    SMS_API_KEY = os.getenv("SMS_API_KEY", "")
    SMS_API_SECRET = os.getenv("SMS_API_SECRET", "")
    SMS_FROM = os.getenv("SMS_FROM", "")
    REMINDERS_ENABLED = os.getenv("REMINDERS_ENABLED", "true").lower() == "true"
