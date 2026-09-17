import os
from app import create_app, db
from flask_cors import CORS
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)
