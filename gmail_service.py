"""
Gmail API communication layer.

Builds a Gmail service object and fetches the latest emails from the
user's inbox.
"""

import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from utils.email_classifier import categorize_email

logger = logging.getLogger(__name__)


def get_gmail_service(credentials: Credentials):
    """
    Build and return an authorised Gmail API service object.

    Args:
        credentials: Valid OAuth2 Credentials with gmail.readonly scope.

    Returns:
        googleapiclient.discovery.Resource (Gmail service)
    """
    service = build("gmail", "v1", credentials=credentials)
    logger.info("Gmail API service built successfully.")
    return service


def fetch_latest_emails(service, max_results: int = 10, query: str = "") -> list[dict]:
    """
    Retrieve the latest *max_results* emails from the user's inbox.

    Args:
        service: Authorised Gmail API service object.
        max_results: Number of emails to retrieve (default 10).
        query: Optional search query string (e.g., 'from:linkedin').

    Returns:
        List of dicts with keys: ``from``, ``subject``, ``date``, ``preview``, ``category``.

    Raises:
        HttpError: On Gmail API errors.
        Exception: On unexpected failures.
    """
    emails: list[dict] = []

    try:
        # Step 1 — list message IDs from the user's inbox matching the query
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results, labelIds=["INBOX"], q=query)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            logger.info("No messages found in inbox.")
            return emails

        # Array to store the emails in the exact order returned by the original list call
        emails = [None] * len(messages)

        def callback(request_id, response, exception):
            if exception is not None:
                logger.error("Error fetching message ID %s: %s", request_id, exception)
                return

            idx = int(request_id)
            headers = {
                h["name"]: h["value"]
                for h in response.get("payload", {}).get("headers", [])
            }
            preview = response.get("snippet", "")

            email_info = {
                "from": headers.get("From", "(unknown sender)"),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", "(unknown date)"),
                "preview": preview,
            }
            email_info["category"] = categorize_email(email_info)
            emails[idx] = email_info

        # Step 2 — fetch metadata + snippet for each message using HTTP Batching
        batch = service.new_batch_http_request(callback=callback)
        
        for idx, msg_meta in enumerate(messages):
            req = service.users().messages().get(
                userId="me", 
                id=msg_meta["id"], 
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            )
            # Use the loop index as the request_id to preserve the correct chronological order
            batch.add(req, request_id=str(idx))

        # Execute all 10 grouped requests in a single network round-trip
        batch.execute()

        # Filter out any 'None' values from failed requests
        emails = [e for e in emails if e is not None]

        logger.info("Fetched %d email(s) via batch request with insights.", len(emails))

    except HttpError as exc:
        logger.error("Gmail API HTTP error: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error fetching emails: %s", exc)
        raise

    return emails
