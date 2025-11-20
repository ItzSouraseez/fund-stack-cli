import requests

# Base Firebase project details
API_KEY = "YOUR_FIREBASE_API_KEY"

# Firebase Auth REST endpoints
FIREBASE_AUTH_SIGNUP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_AUTH_LOGIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# Your Realtime Database URL
DATABASE_URL = "https://YOUR_PROJECT_ID.firebaseio.com"