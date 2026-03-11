"""
auth/firebase_auth.py
─────────────────────
Firebase Authentication helpers for AutoML Studio.

Uses Firebase Authentication (Email/Password provider) via pyrebase4.
No user data is stored locally — Firebase handles everything.

Setup (one-time):
  1. Go to https://console.firebase.google.com → create a project
  2. Authentication → Sign-in method → enable Email/Password
  3. Project Settings → General → scroll to "Your apps" → Web app → copy config
  4. Paste your values into FIREBASE_CONFIG below
  5. pip install pyrebase4

Username UX is preserved: we store username as a display name in Firebase
and use <username>@automlstudio.app as the internal email — users never
see or type an email address.
"""

import streamlit as st

# ── Paste your Firebase project config here ───────────────────────────────────
FIREBASE_CONFIG = {
    "apiKey":            "AIzaSyC8iVVGmR5DQ8RZzn8uU47w4jLf6-_0ANk",
    "authDomain":        "automl-assistant.firebaseapp.com",
    "projectId":         "automl-assistant",
    "storageBucket":     "automl-assistant.firebasestorage.app",
    "messagingSenderId": "493105345729",
    "appId":             "1:493105345729:web:bc41e0ce267d521f1f9040",
    "measurementId":     "G-SBFTKXMFKH",
}


@st.cache_resource
def _get_firebase():
    """
    Initialise pyrebase once and cache it for the lifetime of the app.
    pyrebase4 requires databaseURL — we point it to a dummy placeholder
    since we only use Firebase Auth, not the Realtime Database.
    """
    import pyrebase
    config = {
        **FIREBASE_CONFIG,
        "databaseURL": f"https://{FIREBASE_CONFIG['projectId']}-default-rtdb.firebaseio.com",
    }
    fb = pyrebase.initialize_app(config)
    return fb.auth()


def _to_email(username: str) -> str:
    """Map a plain username to a deterministic internal email for Firebase."""
    safe = "".join(c for c in username.lower() if c.isalnum() or c in "-_.")
    return f"{safe}@automlstudio.app"


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Create a new Firebase user. Returns (success, message)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        auth = _get_firebase()
        user = auth.create_user_with_email_and_password(_to_email(username), password)
        auth.update_profile(user["idToken"], display_name=username)
        return True, "Account created successfully."
    except Exception as e:
        msg = str(e)
        if "EMAIL_EXISTS" in msg:
            return False, "Username already exists. Please choose another."
        if "WEAK_PASSWORD" in msg:
            return False, "Password must be at least 6 characters."
        return False, f"Registration failed: {msg}"


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Verify credentials against Firebase. Returns (success, message)."""
    username = username.strip()
    if not username or not password:
        return False, "Please enter both username and password."
    try:
        auth = _get_firebase()
        auth.sign_in_with_email_and_password(_to_email(username), password)
        return True, "Login successful."
    except Exception as e:
        msg = str(e)
        if "EMAIL_NOT_FOUND" in msg or "USER_NOT_FOUND" in msg:
            return False, "No account found with that username."
        if "INVALID_PASSWORD" in msg or "INVALID_LOGIN_CREDENTIALS" in msg:
            return False, "Incorrect password."
        return False, f"Login failed: {msg}"