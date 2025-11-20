# Purpose: Handles registering users, logging in, logging out, saving session data locally, and storing user profile details in Firebase Database.

from firebase_config import auth, db
# Import the previously created Firebase auth and database objects, from firebase_config.py.

import json # json helps us save the session to a file.
import os # os helps check if the session file exists.

# Name of the file where we store the login session locally
SESSION_FILE = "session.json"

# Saving a user session locally
def save_session(user):
    with open(SESSION_FILE, "w") as f: # Opens file with write permission
        json.dump(user, f) # Saves the user data as JSON into the file


# Explanation:
# user contains token + user ID from Firebase.
# We save it into a file so the user stays logged in between operations.

# Getting the current session
def get_session():
    if not os.path.exists(SESSION_FILE): # Checks if the session file exists
        return None # If the session file doesn't exist, no one is logged in

    # If it exists, read and return the session data
    with open(SESSION_FILE, "r") as f: # Opens file with read permission
        return json.load(f) # Reads and returns the stored session data


# Clearing (logging out)
def clear_session():
    if os.path.exists(SESSION_FILE): # Checks if the session file exists
        os.remove(SESSION_FILE) # Removes the session file, effectively logging the user out


# Save user data into database
def save_user_profile(uid, name, age, phone, pan, email):
    data = {
        "name": name,
        "age": age,
        "phone": phone,
        "pan": pan,
        "email": email
    } # Create a structured dictionary with the user's profile info.

    db.child("users").child(uid).set(data) # Writes the user data under: users/<uid>/ {name, age, ...}

    print("✔ User profile saved to database.") # Confirmation message

# Register a new user
def register_user(email, password, name, age, phone, pan):
    try: # Try to register the user
        user = auth.create_user_with_email_and_password(email, password) # Firebase creates the user.

        print("✔ User registered successfully.") # Confirmation message

        uid = user["localId"] # Get the unique user ID assigned by Firebase.

        save_user_profile(uid, name, age, phone, pan, email) # Save additional profile info to the database.

        return user # Return the created user object

    except Exception as e: # If an error occurs during registration
        print("❌ Registration failed:", e) # Show the error message
        return None # Return None if registration fails

# Login user
def login_user(email, password):
    try: # Try to log in the user
        user = auth.sign_in_with_email_and_password(email, password) # Firebase checks credentials and returns a token

        save_session(user) # Store session in a JSON file

        print("✔ Logged in successfully.") # Confirmation message

        return user # Return the logged-in user object

    except Exception as e: # If an error occurs during login
        print("❌ Login failed:", e) # Show the error message
        return None # Return None if login fails

# Logout user
def logout_user(): 
    clear_session() # Remove the session file
    print("✔ Logged out successfully.") # Confirmation message

# Removing session file logs the user out.