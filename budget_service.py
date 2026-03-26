#========================
#FILE: budget_service.py
#========================

"""
Budget Service Module.

This module handles budget-related operations including:
- Setting monthly budgets for specific categories
- Retrieving budget information
- Computing budget status (spent vs limit)
"""

import requests, time #For making HTTP requests and handling time
from firebase_config import DATABASE_URL #Firebase configuration constant
from auth_service import get_session #For retrieving user session
from wallet_service import get_all_transactions #For retrieving user transactions
from rich.console import Console #For rich text output
console = Console() #Rich console for styled output

def _auth(): #Helper function to retrieve the authentication token for Firebase requests.
    """
    Helper function to retrieve the authentication token for Firebase requests.

    Returns:
        str: query string with auth token if session exists, else empty string.
    """
    session = get_session() #Retrieve current user session
    if not session: return "" #Return empty string if no session
    token = session.get("idToken") #Extract the ID token
    return f"?auth={token}" if token else "" #Return auth query string or empty

def _budget_path(uid, year, month): #Helper function to construct the database path for a specific month's budget.
    """
    Helper function to construct the database path for a specific month's budget.

    Args:
        uid (str): User ID.
        year (int): Year of the budget.
        month (int): Month of the budget.

    Returns:
        str: The database URL path.
    """
    return f"{DATABASE_URL}/users/{uid}/budgets/{year}/{month}" #Construct and return the budget path

def set_budget(uid, year, month, category, limit): #Sets a budget limit for a specific category in a given month.
    """
    Sets a budget limit for a specific category in a given month.

    Args:
        uid (str): User ID.
        year (int): Year.
        month (int): Month.
        category (str): Budget category (e.g., 'Food').
        limit (float): The maximum amount allowed for this category.

    Returns:
        bool: True if the budget was successfully set, False otherwise.
    """
    data = {"category": category, "limit": limit, "updated_at": int(time.time())} #Prepare budget data
    r = requests.put(f"{_budget_path(uid,year,month)}/{category}.json{_auth()}", json=data) #Send PUT request to set budget
    return r.status_code in (200,204) #Return True if successful

def get_budgets(uid, year, month): #Retrieves all budgets set for a specific month.
    """
    Retrieves all budgets set for a specific month.

    Args:
        uid (str): User ID.
        year (int): Year.
        month (int): Month.

    Returns:
        dict: A dictionary of budgets where keys are categories.
    """
    r = requests.get(f"{_budget_path(uid,year,month)}.json{_auth()}") #Send GET request to retrieve budgets
    if r.status_code != 200: return {} #Return empty dict on failure
    return r.json() or {} #Return budgets or empty dict

def compute_budget_status(uid, year, month): #Computes the current status of budgets by comparing limits against actual spending.
    """
    Computes the current status of budgets by comparing limits against actual spending.

    Args:
        uid (str): User ID.
        year (int): Year.
        month (int): Month.

    Returns:
        dict: A dictionary containing budget status for each category.
              Each entry includes limit, spent amount, remaining amount, and status (OK/OVERSPENT).
    """
    budgets = get_budgets(uid, year, month) #Retrieve budgets for the month
    txs = get_all_transactions(uid) #Retrieve all transactions for the user

    spending = {} #Initialize spending dictionary
    for tx in txs: #Iterate through transactions
        t = tx.get("type")
        # Only consider outgoing transactions
        if t not in ["withdrawal","expense","transfer_out"]: continue #Skip non-expense transactions
        cat = tx.get("category","General") #Get transaction category or default to General
        amt = float(tx.get("amount",0)) #Get transaction amount or default to 0
        spending[cat] = spending.get(cat,0) + amt #Accumulate spending per category

    result = {} #Initialize result dictionary
    for cat, b in budgets.items(): #Iterate through budget categories
        limit = b["limit"] #Get budget limit
        spent = spending.get(cat,0) #Get amount spent in this category
        result[cat] = { #Set budget status for the category
            "limit": limit, #Budget limit
            "spent": spent, #Amount spent
            "remaining": limit - spent, #Remaining budget
            "status": "OK" if limit-spent >= 0 else "OVERSPENT" #Budget status
        }
    return result #Return the computed budget status