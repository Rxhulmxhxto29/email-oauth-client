"""
OAuth 2.0 authentication helpers.

Uses google_auth_oauthlib.flow.Flow for web-server OAuth (not InstalledAppFlow,
which is designed for CLI/desktop apps).
"""

import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    SCOPES,
    REDIRECT_URI,
    GOOGLE_AUTH_URI,
    GOOGLE_TOKEN_URI,
)

logger = logging.getLogger(__name__)


def _client_config() -> dict:
    """Build the client-config dict from environment variables."""
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "redirect_uris": [REDIRECT_URI],
        }
    }


def get_auth_flow() -> Flow:
    """Return a configured OAuth Flow bound to the redirect URI."""
    flow = Flow.from_client_config(
        client_config=_client_config(),
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def get_authorization_url() -> tuple[str, str]:
    """
    Generate the Google consent-screen URL.

    Returns:
        (authorization_url, state)  — the state token is stored in the
        session to prevent CSRF.
    """
    flow = get_auth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    logger.info("Generated authorization URL for OAuth login.")
    return authorization_url, state


def exchange_code_for_credentials(authorization_response_url: str) -> Credentials:
    """
    Exchange the authorization code (in the callback URL) for OAuth
    credentials.

    Args:
        authorization_response_url: The full callback URL including query
        parameters.

    Returns:
        google.oauth2.credentials.Credentials

    Raises:
        Exception: If the token exchange fails.
    """
    flow = get_auth_flow()
    flow.fetch_token(authorization_response=authorization_response_url)
    logger.info("Successfully exchanged auth code for credentials.")
    return flow.credentials


def credentials_to_session(credentials: Credentials) -> dict:
    """Serialise Credentials into a plain dict safe for Flask session storage."""
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or []),
    }


def credentials_from_session(session_data: dict) -> Credentials:
    """Reconstruct Credentials from the dict stored in the Flask session."""
    return Credentials(
        token=session_data["token"],
        refresh_token=session_data.get("refresh_token"),
        token_uri=session_data["token_uri"],
        client_id=session_data["client_id"],
        client_secret=session_data["client_secret"],
        scopes=session_data.get("scopes"),
    )
