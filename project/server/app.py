from flask import Flask
from src.api.routes import app as apis
from src.config.logging_config import setup_logging
from src.config.env_config import load_env
import os

# Load environment variables & setup logging
load_env()
setup_logging()

# Initialize Flask app
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(apis)

if __name__ == "__main__":
    #app.run(debug=False)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 5000)))
