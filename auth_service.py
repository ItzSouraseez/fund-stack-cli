#========================
#FILE: auth_service.py
#========================

"""
Authentication Service Module.

This module handles user authentication operations including:
- User registration
- User login
- Session management (saving, retrieving, clearing session)
- User profile creation in the database
"""

import json, os, requests #For making HTTP requests to Firebase Auth and Database
from rich.console import Console #For rich text output
from rich.panel import Panel #For displaying panels in the console
from firebase_config import FIREBASE_AUTH_LOGIN, FIREBASE_AUTH_SIGNUP, DATABASE_URL #Firebase configuration constants

console = Console() #Rich console for styled output
SESSION_FILE = "session.json" #Local file to store user session data

def save_session(data): #Saves the user session data to a local JSON file
    """
    Saves the user session data to a local JSON file.

    Args:
        data (dict): The session data returned from Firebase Auth.
    """
    with open(SESSION_FILE, "w") as f: #Write session data to file
        json.dump(data, f) #Serialize and save session data

def get_session(): #Retrieves the current user session if it exists
    """
    Retrieves the current user session if it exists.

    Returns:
        dict or None: The session data if the file exists, otherwise None.
    """
    if not os.path.exists(SESSION_FILE): return None #Return None if session file doesn't exist
    with open(SESSION_FILE, "r") as f: return json.load(f) #Load and return session data

def clear_session(): #Clears the user session by deleting the local session file
    """
    Clears the local session file, effectively logging the user out.
    """
    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE) #Delete session file if it exists


def register_user(email, password, name, age, phone, pan): #Registers a new user with Firebase Auth and creates a user profile in the database.
    """
    Registers a new user with Firebase Auth and creates a user profile in the database.

    Args:
        email (str): User's email address.
        password (str): User's password.
        name (str): User's full name.
        age (str): User's age.
        phone (str): User's phone number.
        pan (str): User's PAN card number.

    Returns:
        dict or None: The response data from Firebase if successful, None otherwise.
    """
    console.print(Panel("Creating your account...", style="cyan")) #Inform user about account creation

    payload = {"email": email, "password": password, "returnSecureToken": True} #Payload for Firebase Auth signup
    response = requests.post(FIREBASE_AUTH_SIGNUP, json=payload) #Make POST request to Firebase Auth signup endpoint
    data = response.json() #Parse JSON response

    if "error" in data: #Check for errors in the response
        console.print(Panel(f"❌ Registration failed: {data['error']['message']}", style="red")) #Display error message
        return None #Return None on failure

    uid = data["localId"] #Extract user ID from response

    #Create user profile in Realtime Database
    profile = {"name": name, "age": age, "phone": phone, "pan": pan, "email": email} #User profile data
    requests.put(f"{DATABASE_URL}/users/{uid}/profile.json", json=profile) #Save profile to database

    console.print(Panel("✔ Account created successfully!", style="green")) #Inform user about successful account creation
    return data #Return response data


def login_user(email, password): #Logs in a user with Firebase Auth and saves the session data locally.
    """
    Authenticates a user with email and password.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        dict or None: The session data if login is successful, None otherwise.
    """
    console.print(Panel("🔐 Logging in...", style="cyan")) #Inform user about login process

    payload = {"email": email, "password": password, "returnSecureToken": True} #Payload for Firebase Auth login
    response = requests.post(FIREBASE_AUTH_LOGIN, json=payload) #Make POST request to Firebase Auth login endpoint
    data = response.json() #Parse JSON response

    if "error" in data: #Check for errors in the response
        console.print(Panel(f"❌ Login failed: {data['error']['message']}", style="red")) #Display error message
        return None #Return None on failure

    save_session(data) #Save session data locally
    console.print(Panel("✔ Logged in successfully!", style="green")) #Inform user about successful login
    return data #Return session data


def logout_user(): #Logs out the current user by clearing the session file.
    """
    Logs out the current user by clearing the session file.
    """
    clear_session() #Clear the local session file
    console.print(Panel("✔ Logged out.", style="green")) #Inform user about successful logout