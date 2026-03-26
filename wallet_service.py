#========================
#FILE: wallet_service.py
#========================

"""
Wallet Service Module.

This module manages wallet operations including:
- Creating wallets
- Listing and retrieving wallet details
- Processing transactions (Deposit, Withdraw, Transfer)
- Logging transactions to CSV
- Updating wallet balances in Firebase
"""

import uuid, time, csv, os, requests #For UUIDs, time handling, CSV logging, OS operations, and HTTP requests
from rich.progress import Progress #For progress bars
from rich.console import Console #For rich text output
from firebase_config import DATABASE_URL #Firebase configuration constant
from auth_service import get_session #For retrieving user session

console = Console() #Rich console for styled output


def _auth_query(): #Helper function to get the authentication query string for Firebase requests.
    """
    Helper to get the authentication query string for Firebase requests.

    Returns:
        str: Query string with auth token if session exists.
    """
    session = get_session() #Retrieve current user session
    if not session: return "" #Return empty string if no session
    token = session.get("idToken") #Extract the ID token
    return f"?auth={token}" if token else "" #Return auth query string or empty


def _wallet_base(uid):  #Helper function to get the base URL for a user's wallets.
    """Returns the base URL for a user's wallets.""" #Helper function to get the base URL for a user's wallets.
    return f"{DATABASE_URL}/users/{uid}/wallets" #Construct and return the wallet base URL


def _log_csv(uid, wallet_id, tx): #Logs a transaction to a local CSV file for the user.
    """
    Logs a transaction to a local CSV file for the user.

    Args:
        uid (str): User ID.
        wallet_id (str): Wallet ID.
        tx (dict): Transaction details.
    """
    filename = f"transactions_{uid}.csv" #CSV filename based on user ID
    exists = os.path.exists(filename) #Check if file already exists

    with open(filename, "a", newline="") as f: #Open file in append mode
        w = csv.writer(f) #Create CSV writer
        if not exists: #Write header if file is new
            w.writerow(["timestamp", "wallet_id", "type", "amount", "currency", "category", "note", "balance_after", "from_wallet", "to_wallet"]) #CSV header
        w.writerow([ #Write transaction details
            tx.get("timestamp"), wallet_id, tx.get("type"), tx.get("amount"), tx.get("currency"), #Category
            tx.get("category", ""), tx.get("note", ""), tx.get("balance_after", ""), #Balance after transaction
            tx.get("from_wallet", ""), tx.get("to_wallet", "") #From/To wallet IDs
        ])


def create_wallet(uid, name, currency, initial): #Creates a new wallet for the user.
    """
    Creates a new wallet for the user.

    Args:
        uid (str): User ID.
        name (str): Name of the wallet (e.g., "Savings").
        currency (str): Currency code (e.g., "USD").
        initial (float): Initial balance.

    Returns:
        str or None: The new wallet ID if successful, None otherwise.
    """
    wallet_id = uuid.uuid4().hex #Generate unique wallet ID
    wallet = { #Wallet data
        "id": wallet_id, #Wallet ID
        "name": name, #Wallet name
        "currency": currency, #Currency code
        "balance": float(initial), #Initial balance
        "created_at": int(time.time()) #Creation timestamp
    }
    r = requests.put(f"{_wallet_base(uid)}/{wallet_id}.json{_auth_query()}", json=wallet) #Send PUT request to create wallet
    return wallet_id if r.status_code in (200, 204) else None #Return wallet ID if successful


def list_wallets(uid): #Lists all wallets for a user.
    """
    Lists all wallets for a user.

    Args:
        uid (str): User ID.

    Returns:
        list: A list of wallet dictionaries.
    """
    r = requests.get(f"{_wallet_base(uid)}.json{_auth_query()}") #Send GET request to retrieve wallets
    if r.status_code != 200: return [] #Return empty list on failure
    data = r.json() or {} #Parse JSON response or empty dict
    return list(data.values()) #Return list of wallets


def get_wallet(uid, wid): #Retrieves details of a specific wallet.
    """
    Retrieves details of a specific wallet.

    Args:
        uid (str): User ID.
        wid (str): Wallet ID.

    Returns:
        dict or None: Wallet details if found, None otherwise.
    """
    r = requests.get(f"{_wallet_base(uid)}/{wid}.json{_auth_query()}") #Send GET request to retrieve wallet
    return r.json() if r.status_code == 200 else None #Return wallet details if found


def _update_balance(uid, wid, bal): #Updates the balance of a wallet in Firebase.
    """
    Updates the balance of a wallet in Firebase.

    Args:
        uid (str): User ID.
        wid (str): Wallet ID.
        bal (float): New balance.

    Returns:
        bool: True if update was successful.
    """
    r = requests.patch(f"{_wallet_base(uid)}/{wid}.json{_auth_query()}", json={"balance": bal}) #Send PATCH request to update balance
    return r.status_code in (200, 204) #Return True if successful


def _record_tx(uid, wid, tx): #Records a transaction in Firebase under the specific wallet.
    """
    Records a transaction in Firebase under the specific wallet.

    Args:
        uid (str): User ID.
        wid (str): Wallet ID.
        tx (dict): Transaction details.

    Returns:
        str or None: Transaction ID if successful.
    """
    txid = uuid.uuid4().hex #Generate unique transaction ID
    r = requests.put(f"{_wallet_base(uid)}/{wid}/transactions/{txid}.json{_auth_query()}", json=tx) #Send PUT request to record transaction
    return txid if r.status_code in (200, 204) else None #Return transaction ID if successful


def deposit(uid, wid, amt, note, cat): #Processes a deposit into a wallet.
    """
    Processes a deposit into a wallet.

    Args:
        uid (str): User ID.
        wid (str): Wallet ID.
        amt (float): Amount to deposit.
        note (str): Transaction note.
        cat (str): Transaction category.

    Returns:
        bool: True if deposit was successful.
    """
    with Progress() as p: #Show progress bar for deposit processing
        task = p.add_task("[green]Processing deposit...", total=100) #Add progress task
        for _ in range(20): p.update(task, advance=5); time.sleep(0.02) #Simulate progress

    w = get_wallet(uid, wid) #Retrieve wallet details
    new_bal = w["balance"] + amt #Calculate new balance
    _update_balance(uid, wid, new_bal) #Update wallet balance

    tx = {"type": "deposit", "amount": amt, "currency": w["currency"], "note": note,
          "category": cat, "timestamp": int(time.time()), "balance_after": new_bal} #Transaction details

    _record_tx(uid, wid, tx) #Record the transaction
    _log_csv(uid, wid, tx) #Log transaction to CSV
    return True #Return success


def withdraw(uid, wid, amt, note, cat): #Processes a withdrawal from a wallet.
    """
    Processes a withdrawal from a wallet.

    Args:
        uid (str): User ID.
        wid (str): Wallet ID.
        amt (float): Amount to withdraw.
        note (str): Transaction note.
        cat (str): Transaction category.

    Returns:
        bool: True if withdrawal was successful, False if insufficient funds.
    """
    with Progress() as p: #Show progress bar for withdrawal processing
        task = p.add_task("[yellow]Processing withdrawal...", total=100) #Add progress task
        for _ in range(20): p.update(task, advance=5); time.sleep(0.02) #Simulate progress

    w = get_wallet(uid, wid) #Retrieve wallet details
    if amt > w["balance"]: return False #Check for sufficient funds

    new_bal = w["balance"] - amt #Calculate new balance
    _update_balance(uid, wid, new_bal)

    tx = {"type": "withdrawal", "amount": amt, "currency": w["currency"], "note": note,
          "category": cat, "timestamp": int(time.time()), "balance_after": new_bal} #Transaction details

    _record_tx(uid, wid, tx) #Record the transaction
    _log_csv(uid, wid, tx) #Log transaction to CSV
    return True #Return success


def transfer(uid, src, dst, amt, note, cat): #Transfers funds between two wallets.
    """
    Transfers funds between two wallets.

    Args:
        uid (str): User ID.
        src (str): Source Wallet ID.
        dst (str): Destination Wallet ID.
        amt (float): Amount to transfer.
        note (str): Transaction note.
        cat (str): Transaction category.

    Returns:
        bool: True if transfer was successful, False if insufficient funds.
    """
    with Progress() as p: #Show progress bar for transfer processing
        task = p.add_task("[magenta]Processing transfer...", total=100) #Add progress task
        for _ in range(25): p.update(task, advance=4); time.sleep(0.02) #Simulate progress

    s = get_wallet(uid, src) #Retrieve source wallet details
    d = get_wallet(uid, dst) #Retrieve destination wallet details

    if amt > s["balance"]: return False #Check for sufficient funds in source wallet

    new_s = s["balance"] - amt #Calculate new source wallet balance
    new_d = d["balance"] + amt #Calculate new destination wallet balance

    _update_balance(uid, src, new_s) #Update source wallet balance
    _update_balance(uid, dst, new_d) #Update destination wallet balance

    ts = int(time.time()) #Current timestamp

    tx_out = {"type": "transfer_out", "amount": amt, "currency": s["currency"], "note": note,
              "category": cat, "timestamp": ts, "balance_after": new_s, "to_wallet": dst} #Transaction details for source wallet
    tx_in  = {"type": "transfer_in",  "amount": amt, "currency": d["currency"], "note": note,
              "category": cat, "timestamp": ts, "balance_after": new_d, "from_wallet": src} #Transaction details for destination wallet

    _record_tx(uid, src, tx_out) #Record transactions
    _record_tx(uid, dst, tx_in) #Record transactions
    _log_csv(uid, src, tx_out) #Log transactions to CSV
    _log_csv(uid, dst, tx_in) #Log transactions to CSV
    return True #Return success


def get_all_transactions(uid): #Retrieves all transactions across all wallets for a user.
    """
    Retrieves all transactions across all wallets for a user.

    Args:
        uid (str): User ID.

    Returns:
        list: A list of all transaction dictionaries.
    """
    r = requests.get(f"{_wallet_base(uid)}.json{_auth_query()}") #Send GET request to retrieve wallets and transactions
    if r.status_code != 200: return [] #Return empty list on failure

    data = r.json() or {} #Parse JSON response or empty dict
    txs = [] #Initialize transaction list
    for wid, wdata in data.items(): #Iterate through wallets
        for txid, tx in (wdata.get("transactions", {}) or {}).items(): #Iterate through transactions
            tx["_wallet_id"] = wid #Add wallet ID to transaction
            tx["_txid"] = txid #Add transaction ID to transaction
            txs.append(tx) #Add transaction to list
    return txs #Return list of all transactions