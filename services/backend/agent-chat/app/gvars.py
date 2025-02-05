import os

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = os.getenv("FLASK_PORT", "8000")
DEBUG = os.getenv("DEBUG", True)
