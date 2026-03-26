"""
CLI Interface Module.

This module provides the Command Line Interface for the FundStack application.
It handles:
- User input collection and validation
- Menu display and navigation
- Integration with backend services (Auth, Wallet, Budget, Report)
- Displaying data using Rich tables and panels
"""

from multiprocessing.util import info #Unused import to be ignored
import re #For regular expression validations
import getpass #For hidden password input
from auth_service import register_user, login_user, logout_user, get_session #For authentication operations
from budget_service import compute_budget_status #For budget status computation
from report_service import generate_report #For generating AI reports
from wallet_service import (
    create_wallet, list_wallets, get_wallet,
    deposit, withdraw, transfer, get_all_transactions
) #For wallet operations
from rich.console import Console #For rich text output
from rich.table import Table #For displaying tables in the console
from rich.panel import Panel #For displaying panels in the console
from rich.prompt import Prompt #For prompting user input
from rich import box #For table box styles

console = Console() #Rich console for styled output

# ------------------
# VALIDATION HELPERS
# ------------------

def input_name(): #Helpetr function to input and validate user's full name.
    """
    Prompts user for their full name and validates it.
    
    Returns:
        str: Validated name (only alphabets and spaces, min length 2).
    """
    while True: #Loop until valid input is received
        name = Prompt.ask("[bold cyan]Full Name[/]").strip() #Prompt user for name
        if re.match(r"^[A-Za-z ]{2,}$", name): #Validate name format
            return name #Return valid name
        console.print("[bold red]❌ Invalid name.[/] Use only letters and spaces (min. 2 characters). Try again.") #Error message for invalid input

def input_age(): #Helper function to input and validate user's age.
    """
    Prompts user for their age and validates it.

    Returns:
        str: Validated age (16-100).
    """
    while True: #Loop until valid input is received
        age = Prompt.ask("[bold cyan]Age[/]").strip() #Prompt user for age
        if age.isdigit() and 16 <= int(age) <= 100: #Validate age range
            return age #Return valid age
        console.print("[bold red]❌ Invalid age.[/] Enter a number between 16 and 120.") #Error message for invalid input

def input_phone(): #Helper function to input and validate user's phone number.
    """
    Prompts user for phone number and validates it.

    Returns:
        str: Validated phone number (numeric, >= 10 digits).
    """
    while True: #Loop until valid input is received
        phone = Prompt.ask("[bold cyan]Phone Number[/]").strip() #Prompt user for phone number
        if phone.isdigit() and len(phone) >= 10: #Validate phone number format
            return phone #Return valid phone number
        console.print("[bold red]❌ Invalid phone number.[/] Must be numeric and at least 10 digits.") #Error message for invalid input

def input_pan(): #Helper function to input and validate user's PAN number.
    """
    Prompts user for PAN number and validates format.

    Returns:
        str: Validated PAN (Format: ABCDE1234F).
    """
    while True: #Loop until valid input is received
        pan = Prompt.ask("[bold cyan]PAN[/]").strip().upper() #Prompt user for PAN
        if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan): #Validate PAN format
            return pan #Return valid PAN
        console.print("[bold red]❌ Invalid PAN format.[/] Expected format: [yellow]ABCDE1234F[/]") #Error message for invalid input

def input_email(): #Helper function to input and validate user's email address.
    """
    Prompts user for email and performs basic validation.

    Returns:
        str: Validated email address.
    """
    while True: #Loop until valid input is received
        email = Prompt.ask("[bold cyan]Email[/]").strip() #Prompt user for email
        if "@" in email and "." in email: #Basic email format validation
            return email #Return valid email
        console.print("[bold red]❌ Invalid email format.[/] Try again.") #Error message for invalid input

def input_password(): #Helper function to input and validate user's password.
    """
    Prompts user for password (hidden input).

    Returns:
        str: Validated password (min 6 chars).
    """
    while True: #Loop until valid input is received
        pw = getpass.getpass("🔒 Password (min 6 characters): ").strip() #Prompt user for password
        if len(pw) >= 6: #Validate password length
            return pw #Return valid password
        console.print("[bold red]❌ Password too short.[/] Try again.") #Error message for invalid input
# --------------------------------------------------------------------
# MENU DISPLAY
# --------------------------------------------------------------------

def show_menu(): #Helper function to display the main menu options.
    """
    Displays the main menu options based on the user's login state.
    """
    session = get_session() #Check if user is logged in

    console.print("\n[bold cyan]========================[/]") #Menu header
    console.print("[bold cyan]      FUNDSTACK CLI       [/]") #App title
    console.print("[bold cyan]========================[/]\n") #Menu footer

    if session:
        console.print(f"[green]Logged in as →[/] [bold]{session.get('email')}[/]\n") #Show logged in user email
        console.print("[bold yellow]3.[/] Logout") #Logout option
        console.print("[bold yellow]4.[/] Wallets → Create Wallet") #Create wallet option
        console.print("[bold yellow]5.[/] Wallets → List Wallets") #List wallets option
        console.print("[bold yellow]6.[/] Wallets → Wallet Details") #Wallet details option
        console.print("[bold yellow]7.[/] Wallets → Deposit") #Deposit option
        console.print("[bold yellow]8.[/] Wallets → Withdraw") #Withdraw option
        console.print("[bold yellow]9.[/] Wallets → Transfer") #Transfer option
        console.print("[bold yellow]10.[/] Budget → Set Monthly Budget") #Set monthly budget option
        console.print("[bold yellow]11.[/] Budget → View Budget Status") #View budget status option
        console.print("[bold yellow]12.[/] Reports → Generate Monthly Report (Gemini AI)") #Generate monthly report option
        console.print("[bold yellow]13.[/] Exit\n") #Exit option
    else:
        console.print("[bold yellow]1.[/] Register") #Register option
        console.print("[bold yellow]2.[/] Login") #Login option
        console.print("[bold yellow]3.[/] Exit\n") #Exit option

    console.print("[bold cyan]===================================[/]") #Menu footer


def require_login_session(): #Helper function to ensure user is logged in before accessing wallet features.
    """
    Checks if a user session exists.

    Returns:
        dict or None: Session data if logged in, else None.
    """
    session = get_session() #Retrieve current user session
    if not session: #Check if user is logged in
        console.print("[bold red]⚠ You must login first to access wallet features.[/]") #Warning message
        return None #Return None if not logged in
    return session #Return session data if logged in

# --------------------------------------------------------------------
# MAIN HANDLER
# --------------------------------------------------------------------

def handle_user_choice(): #Main application loop.
    """
    Main application loop.
    Handles user input and routes to appropriate service functions.
    """
    while True: #Main loop
        show_menu() #Display the main menu
        session = get_session() #Check user session

        # --------------------------------------------------
        # NOT LOGGED IN MODE
        # --------------------------------------------------
        if not session: #If user is not logged in
            choice = Prompt.ask("[bold cyan]Select an option (1-3)[/]").strip() #Prompt for menu choice

            if choice == "1": #Register
                console.print(Panel.fit("📝 SECURE REGISTRATION", style="bold green"))
                name = input_name() #Input and validate name
                age = input_age() #Input and validate age
                phone = input_phone() #Input and validate phone number
                pan = input_pan() #Input and validate PAN
                email = input_email() #Input and validate email
                pw = input_password() #Input and validate password

                register_user(email, pw, name, age, phone, pan) #Call registration service

            elif choice == "2": #Login
                console.print(Panel.fit("🔐 LOGIN", style="bold blue")) 
                email = Prompt.ask("[bold cyan]Email[/]").strip() #Input email
                pw = getpass.getpass("🔒 Password: ").strip() #Input password
                login_user(email, pw) #Call login service

            elif choice == "3": #Exit
                console.print("[bold magenta]👋 Goodbye![/]")
                break

            else: #Invalid option
                console.print("[bold red]❌ Invalid option. Try again.[/]")
                continue

        # --------------------------------------------------
        # LOGGED IN MODE
        # --------------------------------------------------
        else: #If user is logged in
            choice = Prompt.ask("[bold cyan]Select an option (3-13)[/]").strip() #Prompt for menu choice
            uid = session["localId"] #Get user ID from session

            # Logout
            if choice == "3": #Logout
                logout_user() #Call logout service

            # Create wallet
            elif choice == "4": #Create wallet
                console.print(Panel.fit("💼 CREATE WALLET", style="bold green"))
                name = Prompt.ask("Wallet name (e.g., Savings)").strip() #Input wallet name
                currency = Prompt.ask("Currency (INR/USD/EUR)", default="INR").strip().upper() or "INR" #Input currency with default
                initial = Prompt.ask("Initial balance (optional)", default="").strip() #Input initial balance
                try: #Convert initial balance to float
                    initial_val = float(initial) if initial else 0.0 #Default to 0.0 if empty
                except: #Invalid input handling
                    console.print("[bold red]❌ Invalid initial balance.[/]") #Error message
                    continue #Skip to next iteration

                wid = create_wallet(uid, name, currency, initial_val) #Call create wallet service
                if wid: #If wallet creation successful
                    console.print(f"[bold green]✔ Wallet created:[/] [yellow]{wid}[/]") #Success message
                else: #If wallet creation failed
                    console.print("[bold red]❌ Failed to create wallet.[/]")

            # List wallets
            elif choice == "5": #List wallets
                console.print(Panel.fit("💰 YOUR WALLETS", style="bold cyan"))
                wallets = list_wallets(uid) #Call list wallets service
                if not wallets: #No wallets found
                    console.print("[bold red]⚠ No wallets found.[/]") #Warning message
                else: #Display wallets in a table
                    table = Table(title="Your Wallets", box=box.ROUNDED) #Create table
                    table.add_column("Name", style="cyan", no_wrap=True) #Name column
                    table.add_column("Currency", style="magenta") #Currency column
                    table.add_column("Balance", style="green") #Balance column
                    table.add_column("Wallet ID", style="yellow") #Wallet ID column

                    for w in wallets: #Iterate through wallets
                        table.add_row( #Add wallet details to table
                            str(w.get("name", "")), #Wallet name
                            str(w.get("currency", "")), #Wallet currency
                            str(w.get("balance", 0)), #Wallet balance
                            str(w.get("id", "")) #Wallet ID
                        )

                    console.print(table) #Display the table

            # Wallet details
            elif choice == "6": #Wallet details
                console.print(Panel.fit("💼 WALLET DETAILS", style="bold cyan"))
                wid = Prompt.ask("Enter wallet ID").strip() #Input wallet ID
                w = get_wallet(uid, wid) #Call get wallet service
                if not w: #Wallet not found
                    console.print("[bold red]❌ Wallet not found.[/]") #Error message
                else: #Display wallet details
                    console.print(Panel.fit("📄 WALLET DETAILS", style="bold cyan")) #Display wallet details panel
                    for k, v in w.items(): #Iterate through wallet details
                        console.print(f"[bold]{k}[/]: {v}") #Display each detail

            # Deposit
            elif choice == "7": #Deposit
                console.print(Panel.fit("💰 DEPOSIT", style="bold green"))
                wid = Prompt.ask("Wallet ID").strip() #Input wallet ID
                amt = Prompt.ask("Amount").strip() #Input amount
                cat = Prompt.ask("Category (e.g., Salary, Refund)").strip() #Input category
                note = Prompt.ask("Note").strip() #Input note

                try: #Convert amount to float
                    amt_val = float(amt) #Convert to float
                except: #Invalid input handling
                    console.print("[bold red]❌ Invalid amount.[/]") #Error message
                    continue #Skip to next iteration

                ok = deposit(uid, wid, amt_val, note, cat) #Call deposit service
                console.print("[bold green]✔ Deposit successful.[/]" if ok else "[bold red]❌ Deposit failed.[/]") #Display result

            # Withdraw
            elif choice == "8": #Withdraw
                console.print(Panel.fit("🧾 WITHDRAW", style="bold yellow"))
                wid = Prompt.ask("Wallet ID").strip() #Input wallet ID
                amt = Prompt.ask("Amount").strip() #Input amount
                cat = Prompt.ask("Category (e.g., Food, Shopping)").strip() #Input category
                note = Prompt.ask("Note").strip() #Input note

                try: #Convert amount to float
                    amt_val = float(amt) #Convert to float
                except: #Invalid input handling
                    console.print("[bold red]❌ Invalid amount.[/]") #Error message
                    continue #Skip to next iteration

                ok = withdraw(uid, wid, amt_val, note, cat) #Call withdraw service
                console.print("[bold green]✔ Withdrawal successful.[/]" if ok else "[bold red]❌ Withdrawal failed.[/]") #Display result

            # Transfer
            elif choice == "9":
                console.print(Panel.fit("🔁 TRANSFER", style="bold magenta"))
                src = Prompt.ask("From wallet ID").strip() #Input source wallet ID
                dst = Prompt.ask("To wallet ID").strip() #Input destination wallet ID
                amt = Prompt.ask("Amount").strip() #Input amount
                cat = Prompt.ask("Category (Optional)").strip() #Input category
                note = Prompt.ask("Note").strip() #Input note

                try: #Convert amount to float
                    amt_val = float(amt)
                except: #Invalid input handling
                    console.print("[bold red]❌ Invalid amount.[/]") #Error message
                    continue #Skip to next iteration
                ok = transfer(uid, src, dst, amt_val, note, cat) #Call transfer service
                console.print("[bold green]✔ Transfer complete.[/]" if ok else "[bold red]❌ Transfer failed.[/]") #Display result

            # Set Monthly Budget
            elif choice == "10": #Set monthly budget
                from budget_service import set_budget #Import set_budget function
                console.print(Panel.fit("📊 SET MONTHLY BUDGET", style="bold blue")) #Display header
                year = int(Prompt.ask("Year (YYYY)")) #Input year
                month = int(Prompt.ask("Month (1-12)")) #Input month
                category = Prompt.ask("Category").strip() #Input category
                limit = float(Prompt.ask("Monthly limit")) #Input monthly limit
                ok = set_budget(uid, year, month, category, limit) #Call set_budget service
                console.print("[bold green]✔ Budget saved.[/]" if ok else "[bold red]❌ Failed to save budget.[/]") #Display result

            # View Budget Status
            elif choice == "11": #View budget status
                from budget_service import compute_budget_status #Import compute_budget_status function
                console.print(Panel.fit("📊 BUDGET STATUS", style="bold blue")) #Display header
                year = int(Prompt.ask("Year")) #Input year
                month = int(Prompt.ask("Month (1-12)")) #Input month
                status = compute_budget_status(uid, year, month) #Call compute_budget_status service
                if not status: #No budgets found
                    console.print("[bold yellow]No budgets set for this period.[/]") #Warning message
                else: #Display budget status in a table
                    table = Table(title=f"Budget Status {year}-{str(month).zfill(2)}", box=box.SIMPLE_HEAVY) #Create table
                    table.add_column("Category", style="cyan") #Category column
                    table.add_column("Limit", style="magenta") #Limit column
                    table.add_column("Spent", style="yellow") #Spent column
                    table.add_column("Remaining", style="green") #Remaining column
                    table.add_column("Status", style="red") #Status column
                    for cat, info in status.items(): #Iterate through budget status
                        table.add_row( #Add budget details to table
                            cat, #Category
                            str(info["limit"]), #Limit
                            str(info["spent"]), #Spent
                            str(info["remaining"]), #Remaining
                            info["status"] #Status
                        )

                    console.print(table) #Display the table

            # Generate Monthly Report (Gemini AI)
            elif choice == "12": #Generate monthly report
                from report_service import generate_report #Import generate_report function
                from budget_service import compute_budget_status #Import compute_budget_status function

                console.print(Panel.fit("🤖 GEMINI AI MONTHLY REPORT", style="bold magenta"))
                year = int(Prompt.ask("Year")) #Input year
                month = int(Prompt.ask("Month (1-12)")) #Input month
                txs = get_all_transactions(uid) #Get all transactions
                budget = compute_budget_status(uid, year, month) #Compute budget status
                console.print("\n[bold cyan]Generating report via Gemini AI...[/]\n") #Inform user of report generation
                result = generate_report(txs, budget, year, month) #Call generate_report service
                safe_text = result if isinstance(result, str) else str(result) #Ensure result is string
                console.print(Panel.fit(safe_text, style="bold green")) #Display the report

            # Exit
            elif choice == "13": #Exit
                console.print("[bold magenta]👋 Goodbye![/]") #Display goodbye message
                break #Exit the loop

            else: #Invalid option
                console.print("[bold red]❌ Invalid option.[/]") #Error message
                continue #Skip to next iteration
