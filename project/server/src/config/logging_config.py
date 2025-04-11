import logging
import os

# Define log directory relative to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# Ensure the 'logs' directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    """Configures logging for the application"""
    logging.basicConfig(
        filename=LOG_FILE_PATH,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.getLogger().addHandler(console_handler)

    logging.info("Logging setup complete. Logs will be saved in logs/app.log")
