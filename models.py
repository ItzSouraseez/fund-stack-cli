#========================
#FILE: models.py
#========================

"""
Pydantic Models for FundStack API.

This module defines request and response models for all API endpoints.
Pydantic provides automatic validation and serialization of data.
"""

from pydantic import BaseModel, Field, EmailStr  # For data validation and serialization
from typing import Optional  # For optional fields


# ------------------
# AUTH MODELS
# ------------------

class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: str = Field(..., description="User's email address")  # Required email
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")  # Required password
    name: str = Field(..., min_length=2, description="Full name (letters and spaces only)")  # Required name
    age: str = Field(..., description="Age (16-100)")  # Required age as string
    phone: str = Field(..., min_length=10, description="Phone number (min 10 digits)")  # Required phone
    pan: str = Field(..., description="PAN card number (format: ABCDE1234F)")  # Required PAN


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: str = Field(..., description="User's email address")  # Required email
    password: str = Field(..., min_length=6, description="Password")  # Required password


# ------------------
# WALLET MODELS
# ------------------

class CreateWalletRequest(BaseModel):
    """Request body for creating a new wallet."""
    name: str = Field(..., description="Wallet name (e.g., Savings, Travel)")  # Required wallet name
    currency: str = Field(default="INR", description="Currency code (INR/USD/EUR)")  # Currency with default
    initial_balance: float = Field(default=0.0, ge=0, description="Initial balance (>= 0)")  # Initial balance


class DepositRequest(BaseModel):
    """Request body for depositing into a wallet."""
    amount: float = Field(..., gt=0, description="Amount to deposit (must be > 0)")  # Required positive amount
    note: str = Field(default="", description="Transaction note")  # Optional note
    category: str = Field(default="General", description="Transaction category")  # Category with default


class WithdrawRequest(BaseModel):
    """Request body for withdrawing from a wallet."""
    amount: float = Field(..., gt=0, description="Amount to withdraw (must be > 0)")  # Required positive amount
    note: str = Field(default="", description="Transaction note")  # Optional note
    category: str = Field(default="General", description="Transaction category")  # Category with default


class TransferRequest(BaseModel):
    """Request body for transferring between wallets."""
    from_wallet_id: str = Field(..., description="Source wallet ID")  # Required source wallet
    to_wallet_id: str = Field(..., description="Destination wallet ID")  # Required destination wallet
    amount: float = Field(..., gt=0, description="Amount to transfer (must be > 0)")  # Required positive amount
    note: str = Field(default="", description="Transaction note")  # Optional note
    category: str = Field(default="General", description="Transaction category")  # Category with default


# ------------------
# BUDGET MODELS
# ------------------

class SetBudgetRequest(BaseModel):
    """Request body for setting a monthly budget."""
    year: int = Field(..., description="Budget year (e.g., 2026)")  # Required year
    month: int = Field(..., ge=1, le=12, description="Budget month (1-12)")  # Required month
    category: str = Field(..., description="Budget category (e.g., Food, Travel)")  # Required category
    limit: float = Field(..., gt=0, description="Monthly spending limit")  # Required positive limit


# ------------------
# GENERIC RESPONSE MODELS
# ------------------

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True  # Always True for success responses
    message: str = Field(..., description="Success message")  # Descriptive message
    data: Optional[dict] = Field(default=None, description="Optional response data")  # Optional payload


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False  # Always False for error responses
    message: str = Field(..., description="Error message")  # Descriptive error message
