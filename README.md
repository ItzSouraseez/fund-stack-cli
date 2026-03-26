<p align="center">
  <h1 align="center">💰 FundStack CLI</h1>
  <p align="center">
    <strong>A comprehensive personal finance management tool for your terminal</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/fund-stack-cli/">
      <img src="https://img.shields.io/pypi/v/fund-stack-cli?color=brightgreen&label=PyPI" alt="PyPI Version">
    </a>
    <a href="https://pypi.org/project/fund-stack-cli/">
      <img src="https://img.shields.io/pypi/dm/fund-stack-cli?color=blue" alt="Downloads">
    </a>
    <a href="https://github.com/ItzSouraseez/fund-stack-cli/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
    </a>
    <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python 3.8+">
  </p>
</p>

---

## 🌐 Deployed Version

**📦 Install from PyPI:**  
👉 **[https://pypi.org/project/fund-stack-cli/](https://pypi.org/project/fund-stack-cli/)**

```bash
pip install fund-stack-cli
```

---

## 📖 Overview

**FundStack CLI** is a powerful, terminal-based personal finance management application that allows you to manage your finances directly from the command line. Built with Python and integrated with Firebase and Google Gemini AI, it provides a secure, intuitive, and feature-rich experience for tracking your money.

---

## ✨ Features

### 🔐 User Authentication
Secure user authentication powered by **Firebase Auth**.
- **User Registration**: Create accounts with comprehensive profile information (Name, Age, Phone, PAN, Email)
- **Secure Login**: Password-protected authentication with encrypted token management
- **Session Management**: Persistent local sessions for seamless experience
- **Logout**: Clean session termination

**Impact**: Ensures data privacy and personalized finance tracking for each user.

---

### 💳 Wallet Management
Create and manage multiple wallets to organize your finances.
- **Create Wallet**: Set up wallets for different purposes (Savings, Spending, Travel, Emergency, etc.)
- **List Wallets**: View all wallets with their current balances at a glance
- **Wallet Details**: Drill down into specific wallet information
- **Multi-Currency Support**: Track funds in different currencies

**Impact**: Enables organized money management by separating funds for different financial goals.

---

### 💸 Transaction Tracking
Complete transaction history and management.
- **Deposits**: Add money to any wallet with notes and category tags
- **Withdrawals**: Record spending with categorization
- **Transfers**: Move money between your wallets seamlessly
- **Transaction History**: View complete transaction logs
- **CSV Export**: Automatic transaction logging to CSV files for backup

**Impact**: Provides complete visibility and audit trail of all financial activities.

---

### 📊 Budget Management
Set spending limits and track your expenses against them.
- **Monthly Budgets**: Set category-specific spending limits for each month
- **Budget Status**: Real-time comparison of spending vs. limits
- **Overspending Alerts**: Visual indicators when you exceed budget limits
- **Category Tracking**: Monitor spending across categories like Food, Travel, Entertainment, etc.

**Impact**: Helps users stay financially disciplined and avoid overspending.

---

### 🤖 AI-Powered Financial Reports
Generate intelligent monthly financial insights using **Google Gemini AI**.
- **Monthly Reports**: Comprehensive analysis of your financial month
- **Income & Expense Summary**: Automatic calculation of totals
- **Category-wise Analysis**: Breakdown of spending by category
- **Savings Estimation**: Calculate how much you're saving
- **Smart Recommendations**: AI-generated personalized suggestions for next month

**Impact**: Transforms raw transaction data into actionable financial insights and advice.

---

### 🎨 Beautiful Terminal UI
Enhanced user experience with **Rich** library.
- **Colorful Output**: Styled panels, tables, and text
- **Interactive Menus**: Clear navigation with numbered options
- **Input Validation**: Robust validation with helpful error messages
- **Loading Animations**: Smooth spinners during AI report generation

**Impact**: Makes command-line finance management enjoyable and intuitive.

---

## 🏗️ Architecture

```
fund-stack-cli/
├── main.py              # CLI Entry point
├── cli.py               # Command Line Interface & User Interaction
├── api.py               # FastAPI REST API Server
├── api_auth.py          # API Authentication Dependency (Firebase token verification)
├── models.py            # Pydantic Request/Response Models
├── auth_service.py      # Firebase Authentication
├── wallet_service.py    # Wallet & Transaction Logic
├── budget_service.py    # Budget Management
├── report_service.py    # AI Report Generation (Gemini)
├── firebase_config.py   # Firebase Configuration
├── requirements.txt     # Python Dependencies
├── Dockerfile           # Docker Containerization
├── docker-compose.yml   # Docker Compose Configuration
└── docs/                # Documentation
    ├── README.md
    ├── CLI.md
    └── SERVICES.md
```

---

## 🌐 REST API

FundStack exposes all its functionality as REST API endpoints using **FastAPI**. When running as a server, you get interactive API docs at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Starting the API Server

```bash
# Option 1: Run directly
python api.py
# Server starts at http://127.0.0.1:8000

# Option 2: Run with Uvicorn (production)
uvicorn api:app --host 0.0.0.0 --port 8000

# Option 3: Docker
docker-compose up --build
```

### Authentication Flow

1. Call `POST /api/auth/login` with email & password
2. Receive an `idToken` in the response
3. Pass it as `Authorization: Bearer <idToken>` in all subsequent requests

### API Endpoints

| Method | Endpoint | Auth? | Description |
|--------|----------|-------|-------------|
| `GET` | `/` | ❌ | Health check |
| `POST` | `/api/auth/register` | ❌ | Register a new user |
| `POST` | `/api/auth/login` | ❌ | Login, returns session tokens |
| `POST` | `/api/auth/logout` | ✅ | Clears the server-side session |
| `GET` | `/api/auth/session` | ✅ | Returns current session info |
| `POST` | `/api/wallets` | ✅ | Create a new wallet |
| `GET` | `/api/wallets` | ✅ | List all wallets |
| `GET` | `/api/wallets/{wallet_id}` | ✅ | Get wallet details |
| `POST` | `/api/wallets/{wallet_id}/deposit` | ✅ | Deposit into a wallet |
| `POST` | `/api/wallets/{wallet_id}/withdraw` | ✅ | Withdraw from a wallet |
| `POST` | `/api/wallets/transfer` | ✅ | Transfer between wallets |
| `GET` | `/api/transactions` | ✅ | Get all transactions |
| `POST` | `/api/budgets` | ✅ | Set a monthly budget |
| `GET` | `/api/budgets/{year}/{month}` | ✅ | Get budget status |
| `POST` | `/api/reports/{year}/{month}` | ✅ | Generate AI monthly report |

### Example: curl Usage

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User","age":"25","phone":"1234567890","pan":"ABCDE1234F"}'

# Login (save the idToken from the response)
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Create a wallet (use the token from login)
curl -X POST http://127.0.0.1:8000/api/wallets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_ID_TOKEN>" \
  -d '{"name":"Savings","currency":"INR","initial_balance":10000}'

# List wallets
curl -H "Authorization: Bearer <YOUR_ID_TOKEN>" \
  http://127.0.0.1:8000/api/wallets
```

---

## 🚀 Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install fund-stack-cli
```

Then run:
```bash
fund-stack
```

### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/ItzSouraseez/fund-stack-cli.git
cd fund-stack-cli

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 📚 Usage Guide

### Getting Started

1. **Launch the Application**
   ```bash
   fund-stack  # If installed via pip
   # OR
   python main.py  # If running from source
   ```

2. **Register a New Account**
   - Select Option `1` (Register)
   - Enter your details:
     - **Name**: Full name (alphabets only, min 2 characters)
     - **Age**: Between 16-100
     - **Phone**: At least 10 digits
     - **PAN**: Format `ABCDE1234F`
     - **Email**: Valid email address
     - **Password**: Minimum 6 characters

3. **Login**
   - Select Option `2` (Login)
   - Enter your registered email and password

### Menu Options (After Login)

| Option | Action | Description |
|--------|--------|-------------|
| 3 | Logout | End current session |
| 4 | Create Wallet | Create a new wallet (e.g., "Savings", "Travel") |
| 5 | List Wallets | View all wallets with balances |
| 6 | Wallet Details | View specific wallet information |
| 7 | Deposit | Add money to a wallet |
| 8 | Withdraw | Spend money from a wallet |
| 9 | Transfer | Move money between wallets |
| 10 | Set Budget | Set monthly spending limits by category |
| 11 | Budget Status | View spending vs. budget limits |
| 12 | Generate Report | Get AI-powered monthly financial analysis |
| 13 | Exit | Close the application |

### Example Workflow

```bash
# 1. Create wallets for different purposes
→ Option 4: Create Wallet
  Name: Savings
  Currency: INR
  Initial Balance: 10000

→ Option 4: Create Wallet
  Name: Food Expenses
  Currency: INR
  Initial Balance: 5000

# 2. Set a monthly budget
→ Option 10: Set Monthly Budget
  Category: Food
  Limit: 8000

# 3. Record transactions
→ Option 8: Withdraw
  Select wallet: Food Expenses
  Amount: 500
  Note: Dinner with friends
  Category: Food

# 4. Check budget status
→ Option 11: View Budget Status
  Shows: Food - Spent: ₹500 / Limit: ₹8000 | Remaining: ₹7500 ✓

# 5. Generate monthly report
→ Option 12: Generate Monthly Report
  AI generates comprehensive financial analysis with recommendations
```

---

## 🔧 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Firebase Auth** | User authentication and identity management |
| **Firebase Realtime Database** | Cloud data storage for wallets, transactions, budgets |
| **Google Gemini AI** | Intelligent financial report generation |
| **Rich** | Beautiful terminal UI (tables, panels, colors, spinners) |
| **FastAPI** | REST API framework with auto-generated Swagger docs |
| **Uvicorn** | ASGI server for running the FastAPI application |
| **Pydantic** | Data validation and serialization for API request/response models |
| **Requests** | HTTP client for API communication |
| **Docker** | Containerization for easy deployment |

---

## 🔒 Security Features

- **Password Hashing**: Secure password management via Firebase Auth
- **Token-Based Auth**: JWT tokens for authenticated API requests
- **Local Session Encryption**: Secure storage of session data
- **Input Validation**: Comprehensive validation to prevent malformed data

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sourashis Ghosh Roy**  
Built as part of On Job Training Project at Polaris School of Technology

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📫 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/ItzSouraseez/fund-stack-cli/issues) on GitHub.

---

<p align="center">
  Made with ❤️ for the command line enthusiasts
</p>