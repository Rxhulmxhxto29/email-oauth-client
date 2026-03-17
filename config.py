"""
Application configuration.

Secrets are loaded from a .env file (local dev) or real environment
variables (production / Render). Never hardcoded.
"""

import os
from dotenv import load_dotenv  # type: ignore

# Load .env file if it exists (ignored in production where real env vars are set)
load_dotenv()

# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# ---------------------------------------------------------------------------
# Google OAuth 2.0
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# The ONLY Gmail scope allowed — read-only access.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Redirect URI — override via env var when deploying (e.g. on Render).
# Example: https://your-app-name.onrender.com/oauth2callback
REDIRECT_URI = os.environ.get(
    "OAUTH_REDIRECT_URI", "http://localhost:5000/oauth2callback"
)

# Google's OAuth endpoints (stable, public values).
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
