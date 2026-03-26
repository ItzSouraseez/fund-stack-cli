#========================
#FILE: api.py
#========================

"""
FundStack REST API Server.

This module provides a FastAPI-based REST API that wraps all existing
FundStack CLI service functions. It enables HTTP access to all features
that were previously only available via the terminal.

Framework: FastAPI + Uvicorn (ASGI server)
Authentication: Firebase idToken as Bearer token
Validation: Pydantic models for all request/response bodies
Docs: Auto-generated Swagger UI at /docs, ReDoc at /redoc
"""

from fastapi import FastAPI, Depends, HTTPException  # Core FastAPI components
from fastapi.middleware.cors import CORSMiddleware  # For cross-origin requests

# Pydantic request/response models
from models import (
    RegisterRequest, LoginRequest,
    CreateWalletRequest, DepositRequest, WithdrawRequest, TransferRequest,
    SetBudgetRequest, SuccessResponse, ErrorResponse
)

# Auth dependency for protected routes
from api_auth import get_current_user

# Existing service functions (unchanged)
from auth_service import register_user, login_user, logout_user, get_session  # Auth operations
from wallet_service import (
    create_wallet, list_wallets, get_wallet,
    deposit, withdraw, transfer, get_all_transactions
)  # Wallet operations
from budget_service import set_budget, compute_budget_status  # Budget operations
from report_service import generate_report  # AI report generation

# ------------------------------------------------------------------
# APP INITIALIZATION
# ------------------------------------------------------------------

app = FastAPI(
    title="FundStack API",
    description="REST API for FundStack — Personal Finance Management. "
                "All wallet, budget, and report features accessible over HTTP.",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
)

# Enable CORS for frontend clients / Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins (configure for production)
    allow_credentials=True,     # Allow cookies/auth headers
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers
)


# ==================================================================
# SECTION 1: AUTHENTICATION ENDPOINTS
# ==================================================================

@app.post("/api/auth/register", tags=["Authentication"], summary="Register a new user")
async def api_register(req: RegisterRequest):
    """
    Creates a new user account with Firebase Auth and stores
    the user profile in the Realtime Database.

    No authentication required.
    """
    try:
        result = register_user(req.email, req.password, req.name, req.age, req.phone, req.pan)  # Call existing service
        if result is None:  # Registration failed (e.g., email already exists)
            raise HTTPException(status_code=400, detail="Registration failed. Email may already be in use.")
        return {  # Return success with user data
            "success": True,
            "message": "Account created successfully",
            "data": {"localId": result.get("localId"), "email": result.get("email")}
        }
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/api/auth/login", tags=["Authentication"], summary="Login and get auth token")
async def api_login(req: LoginRequest):
    """
    Authenticates a user and returns Firebase auth tokens.
    Use the `idToken` from the response as a Bearer token
    for all protected endpoints.

    No authentication required.
    """
    try:
        result = login_user(req.email, req.password)  # Call existing service
        if result is None:  # Login failed (wrong credentials)
            raise HTTPException(status_code=401, detail="Login failed. Invalid email or password.")
        return {  # Return session tokens
            "success": True,
            "message": "Logged in successfully",
            "data": {
                "idToken": result.get("idToken"),       # Use this as Bearer token
                "localId": result.get("localId"),       # User's unique ID
                "email": result.get("email"),           # User's email
                "refreshToken": result.get("refreshToken"),  # For token refresh
                "expiresIn": result.get("expiresIn")    # Token expiry in seconds
            }
        }
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@app.post("/api/auth/logout", tags=["Authentication"], summary="Logout current user")
async def api_logout(user: dict = Depends(get_current_user)):
    """
    Clears the server-side session file.

    Requires Bearer token in Authorization header.
    """
    try:
        logout_user()  # Call existing service to clear session.json
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")


@app.get("/api/auth/session", tags=["Authentication"], summary="Get current session info")
async def api_session(user: dict = Depends(get_current_user)):
    """
    Returns the current authenticated user's session information.

    Requires Bearer token in Authorization header.
    """
    session = get_session()  # Read session from file
    if not session:  # No session found (should not happen if auth dependency passed)
        raise HTTPException(status_code=401, detail="No active session")
    return {
        "success": True,
        "message": "Session active",
        "data": {
            "localId": session.get("localId"),
            "email": session.get("email", "N/A"),
            "idToken": session.get("idToken", "")[:20] + "..."  # Truncate token for security
        }
    }


# ==================================================================
# SECTION 2: WALLET ENDPOINTS
# ==================================================================

@app.post("/api/wallets", tags=["Wallets"], summary="Create a new wallet")
async def api_create_wallet(req: CreateWalletRequest, user: dict = Depends(get_current_user)):
    """
    Creates a new wallet for the authenticated user.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        wid = create_wallet(uid, req.name, req.currency, req.initial_balance)  # Call existing service
        if wid:  # Wallet created successfully
            return {
                "success": True,
                "message": "Wallet created successfully",
                "data": {"wallet_id": wid, "name": req.name, "currency": req.currency, "initial_balance": req.initial_balance}
            }
        else:  # Wallet creation failed
            raise HTTPException(status_code=500, detail="Failed to create wallet")
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Create wallet error: {str(e)}")


@app.get("/api/wallets", tags=["Wallets"], summary="List all wallets")
async def api_list_wallets(user: dict = Depends(get_current_user)):
    """
    Returns all wallets belonging to the authenticated user.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        wallets = list_wallets(uid)  # Call existing service
        return {
            "success": True,
            "message": f"Found {len(wallets)} wallet(s)",
            "data": {"wallets": wallets}
        }
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"List wallets error: {str(e)}")


@app.get("/api/wallets/{wallet_id}", tags=["Wallets"], summary="Get wallet details")
async def api_get_wallet(wallet_id: str, user: dict = Depends(get_current_user)):
    """
    Returns detailed information about a specific wallet.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        wallet = get_wallet(uid, wallet_id)  # Call existing service
        if not wallet:  # Wallet not found
            raise HTTPException(status_code=404, detail="Wallet not found")
        return {
            "success": True,
            "message": "Wallet found",
            "data": {"wallet": wallet}
        }
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Get wallet error: {str(e)}")


@app.post("/api/wallets/{wallet_id}/deposit", tags=["Wallets"], summary="Deposit into a wallet")
async def api_deposit(wallet_id: str, req: DepositRequest, user: dict = Depends(get_current_user)):
    """
    Deposits money into the specified wallet.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        ok = deposit(uid, wallet_id, req.amount, req.note, req.category)  # Call existing service
        if ok:  # Deposit successful
            return {"success": True, "message": f"Deposited {req.amount} successfully"}
        else:  # Deposit failed
            raise HTTPException(status_code=400, detail="Deposit failed")
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Deposit error: {str(e)}")


@app.post("/api/wallets/{wallet_id}/withdraw", tags=["Wallets"], summary="Withdraw from a wallet")
async def api_withdraw(wallet_id: str, req: WithdrawRequest, user: dict = Depends(get_current_user)):
    """
    Withdraws money from the specified wallet.
    Fails if insufficient balance.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        ok = withdraw(uid, wallet_id, req.amount, req.note, req.category)  # Call existing service
        if ok:  # Withdrawal successful
            return {"success": True, "message": f"Withdrew {req.amount} successfully"}
        else:  # Insufficient funds
            raise HTTPException(status_code=400, detail="Withdrawal failed — insufficient balance")
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Withdraw error: {str(e)}")


@app.post("/api/wallets/transfer", tags=["Wallets"], summary="Transfer between wallets")
async def api_transfer(req: TransferRequest, user: dict = Depends(get_current_user)):
    """
    Transfers money from one wallet to another.
    Fails if insufficient balance in the source wallet.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        ok = transfer(uid, req.from_wallet_id, req.to_wallet_id, req.amount, req.note, req.category)  # Call existing service
        if ok:  # Transfer successful
            return {"success": True, "message": f"Transferred {req.amount} successfully"}
        else:  # Transfer failed
            raise HTTPException(status_code=400, detail="Transfer failed — insufficient balance in source wallet")
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Transfer error: {str(e)}")


# ==================================================================
# SECTION 3: TRANSACTION ENDPOINTS
# ==================================================================

@app.get("/api/transactions", tags=["Transactions"], summary="Get all transactions")
async def api_get_transactions(user: dict = Depends(get_current_user)):
    """
    Returns all transactions across all wallets for the authenticated user.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        txs = get_all_transactions(uid)  # Call existing service
        return {
            "success": True,
            "message": f"Found {len(txs)} transaction(s)",
            "data": {"transactions": txs}
        }
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Get transactions error: {str(e)}")


# ==================================================================
# SECTION 4: BUDGET ENDPOINTS
# ==================================================================

@app.post("/api/budgets", tags=["Budgets"], summary="Set a monthly budget")
async def api_set_budget(req: SetBudgetRequest, user: dict = Depends(get_current_user)):
    """
    Sets a spending limit for a specific category in a given month.

    Requires Bearer token in Authorization header.
    """
    try:
        uid = user["uid"]  # Get user ID from auth dependency
        ok = set_budget(uid, req.year, req.month, req.category, req.limit)  # Call existing service
        if ok:  # Budget set successfully
            return {
                "success": True,
                "message": f"Budget set: {req.category} = {req.limit} for {req.year}-{str(req.month).zfill(2)}"
            }
        else:  # Budget save failed
            raise HTTPException(status_code=500, detail="Failed to save budget")
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Set budget error: {str(e)}")


@app.get("/api/budgets/{year}/{month}", tags=["Budgets"], summary="Get budget status")
async def api_budget_status(year: int, month: int, user: dict = Depends(get_current_user)):
    """
    Returns the budget status for the specified month, showing
    spending vs. limits for each category.

    Requires Bearer token in Authorization header.
    """
    if month < 1 or month > 12:  # Validate month range
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    try:
        uid = user["uid"]  # Get user ID from auth dependency
        status = compute_budget_status(uid, year, month)  # Call existing service
        return {
            "success": True,
            "message": f"Budget status for {year}-{str(month).zfill(2)}",
            "data": {"budget_status": status if status else {}}
        }
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Budget status error: {str(e)}")


# ==================================================================
# SECTION 5: REPORT ENDPOINTS
# ==================================================================

@app.post("/api/reports/{year}/{month}", tags=["Reports"], summary="Generate AI monthly report")
async def api_generate_report(year: int, month: int, user: dict = Depends(get_current_user)):
    """
    Generates an AI-powered monthly financial report using Google Gemini.
    Analyzes transactions and budget data to provide insights and recommendations.

    This may take a few seconds as it calls the Gemini AI API.

    Requires Bearer token in Authorization header.
    """
    if month < 1 or month > 12:  # Validate month range
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    try:
        uid = user["uid"]  # Get user ID from auth dependency
        txs = get_all_transactions(uid)  # Get all transactions
        budget = compute_budget_status(uid, year, month)  # Compute budget status
        report = generate_report(txs, budget, year, month)  # Generate AI report

        return {
            "success": True,
            "message": f"Monthly report for {year}-{str(month).zfill(2)}",
            "data": {"report": report}
        }
    except Exception as e:  # Catch unexpected errors
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


# ------------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------------

@app.get("/", tags=["Health"], summary="Health check")
async def health_check():
    """
    Simple health check endpoint to verify the API server is running.
    """
    return {
        "status": "healthy",
        "app": "FundStack API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ------------------------------------------------------------------
# RUN SERVER
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn  # ASGI server
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)  # Start server with hot-reload
