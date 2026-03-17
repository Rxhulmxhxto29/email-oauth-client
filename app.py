"""
Email OAuth Client — Flask application.

Routes
------
/               Home page (login button)
/login          Initiates Google OAuth redirect
/oauth2callback Handles the OAuth callback
/emails         Displays the user's latest 10 Gmail emails
/logout         Clears the session
"""

import os
import logging
from flask import Flask, redirect, url_for, session, request, render_template, jsonify  # type: ignore
from werkzeug.middleware.proxy_fix import ProxyFix  # type: ignore

from config import SECRET_KEY, SCOPES  # type: ignore
from auth import (  # type: ignore
    get_authorization_url,
    exchange_code_for_credentials,
    credentials_to_session,
    credentials_from_session,
)
from gmail_service import get_gmail_service, fetch_latest_emails  # type: ignore

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Respect X-Forwarded-Proto headers so OAuth generated URLs use HTTPS correctly behind load balancers.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Allow OAuth over plain HTTP during local development only.
# In production (or without a .env override), this safely defaults to "0".
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.environ.get(
    "OAUTHLIB_INSECURE_TRANSPORT", "0"
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Home page — shows a login button."""
    return render_template("index.html")


@app.route("/login")
def login():
    """Redirect the user to Google's OAuth consent screen."""
    try:
        authorization_url, state = get_authorization_url()
        session["oauth_state"] = state
        logger.info("User redirected to Google OAuth consent screen.")
        return redirect(authorization_url)
    except Exception as exc:
        logger.error("Failed to initiate OAuth login: %s", exc)
        return render_template("index.html", error="Failed to start login. Please try again."), 500


@app.route("/oauth2callback")
def oauth2callback():
    """
    Handle the callback from Google after the user grants (or denies)
    permission.
    """
    # Check for errors returned by Google
    error = request.args.get("error")
    if error:
        logger.warning("OAuth callback received error: %s", error)
        return render_template("index.html", error=f"Authentication failed: {error}"), 400

    try:
        credentials = exchange_code_for_credentials(request.url)
        session["credentials"] = credentials_to_session(credentials)
        logger.info("OAuth callback successful — credentials stored in session.")
        return redirect(url_for("emails"))
    except Exception as exc:
        logger.error("OAuth callback failed: %s", exc)
        return render_template("index.html", error="Authentication failed. Please try again."), 500


@app.route("/emails")
def emails():
    """Fetch and display the user's latest 10 Gmail emails."""
    if "credentials" not in session:
        logger.warning("Unauthenticated access to /emails — redirecting to login.")
        return redirect(url_for("login"))

    try:
        query = request.args.get("q", "")
        creds = credentials_from_session(session["credentials"])
        service = get_gmail_service(creds)
        email_list = fetch_latest_emails(service, max_results=10, query=query)

        # Categorize and group the returned emails
        grouped_emails = {
            "Important": [],
            "Work / Jobs": [],
            "Social": [],
            "Notifications": [],
            "Promotions": [],
            "Other": [],
        }
        for email in email_list:
            cat = email.get("category", "Other")
            if cat in grouped_emails:
                grouped_emails[cat].append(email)
            else:
                grouped_emails["Other"].append(email)

        # If the token was refreshed, persist the updated credentials.
        session["credentials"] = credentials_to_session(creds)

        logger.info("Displaying %d emails for user with query '%s'.", len(email_list), query)
        return render_template(
            "emails.html", 
            grouped_emails=grouped_emails, 
            query=query, 
            total_emails=len(email_list)
        )

    except Exception as exc:
        logger.error("Error fetching emails: %s", exc)
        session.pop("credentials", None)
        return render_template(
            "index.html",
            error="Failed to retrieve emails. Your session may have expired — please log in again.",
        ), 500


@app.route("/logout")
def logout():
    """Clear the session and redirect to the home page."""
    session.clear()
    logger.info("User logged out — session cleared.")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Entry point (local development)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
