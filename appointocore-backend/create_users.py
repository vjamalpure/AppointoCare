# create_users.py
import os
import sys
from app import create_app
from sample_data import seed_all_sample_data

if __name__ == "__main__":
    if os.getenv("APP_ENV") == "production" and os.getenv("SEED_DEMO_DATA", "false").lower() == "true":
        raise RuntimeError("Demo data seeding is disabled in production")

    app = create_app()
    with app.app_context():
        reset_flag = "--reset" in sys.argv or os.getenv("RESET_DATA", "false").lower() == "true"
        seed_all_sample_data(reset=reset_flag)
