#========================
#FILE: api_auth.py
#========================

"""
API Authentication Dependency Module.

This module provides FastAPI dependency functions for authenticating
API requests using Firebase Auth tokens. It:
- Extracts the Bearer token from the Authorization header
- Verifies the token via Firebase Auth REST API (getAccountInfo)
- Writes session.json so existing service functions work without modification
- Returns user identity (uid + idToken) for use in route handlers
"""

import json  # For writing session data
import requests  # For Firebase Auth verification
from fastapi import Depends, HTTPException, Header  # FastAPI dependency injection
from firebase_config import API_KEY  # Firebase API key for token verification

# Firebase Auth REST API endpoint for verifying tokens
FIREBASE_VERIFY_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"

SESSION_FILE = "session.json"  # Must match auth_service.py's SESSION_FILE


def _write_session(data: dict):
    """
    Writes session data to session.json so existing service functions
    (wallet_service, budget_service, etc.) can read the auth token.

    Args:
        data (dict): Session data containing at least 'idToken' and 'localId'.
    """
    with open(SESSION_FILE, "w") as f:  # Open session file for writing
        json.dump(data, f)  # Serialize and write session data


async def get_current_user(authorization: str = Header(..., description="Bearer <Firebase idToken>")):
    """
    FastAPI dependency that authenticates the current user.

    Extracts the Bearer token from the Authorization header,
    verifies it against Firebase Auth REST API, and returns
    the user's uid and idToken.

    Args:
        authorization (str): The Authorization header value (e.g., "Bearer abc123...").

    Returns:
        dict: Contains 'uid' (user's Firebase UID) and 'idToken' (the verified token).

    Raises:
        HTTPException: 401 if token is missing, invalid, or verification fails.
    """
    # Extract Bearer token from Authorization header
    if not authorization.startswith("Bearer "):  # Validate header format
        raise HTTPException(status_code=401, detail="Authorization header must be: Bearer <token>")

    token = authorization[7:]  # Strip "Bearer " prefix to get raw token

    if not token:  # Check if token is empty
        raise HTTPException(status_code=401, detail="Token is missing")

    # Verify token with Firebase Auth REST API
    try:
        response = requests.post(FIREBASE_VERIFY_URL, json={"idToken": token})  # Send verification request
        data = response.json()  # Parse response JSON

        if "error" in data:  # Check for Firebase errors
            raise HTTPException(status_code=401, detail=f"Invalid token: {data['error']['message']}")

        users = data.get("users", [])  # Extract user list from response
        if not users:  # No users found for this token
            raise HTTPException(status_code=401, detail="Token verification failed: no user found")

        uid = users[0]["localId"]  # Extract user ID from first (and only) user

    except HTTPException:  # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:  # Catch any unexpected errors
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

    # Write session.json so existing service functions can authenticate
    # This is the pragmatic bridge between the API layer and the existing service layer
    session_data = {"idToken": token, "localId": uid}  # Minimal session data
    _write_session(session_data)  # Persist to session.json

    return {"uid": uid, "idToken": token}  # Return authenticated user info
