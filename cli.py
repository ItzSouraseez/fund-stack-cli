from auth_service import (
    register_user,
    login_user,
    logout_user,
    get_session
)


def show_menu():
    print("\n====== Firebase CLI Authentication ======")
    print("1. Register")
    print("2. Login")
    print("3. Logout")
    print("4. Check Current User")
    print("5. Exit")
    print("=========================================")


def handle_user_choice():
    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            print("\n--- Register ---")
            name = input("Full Name: ")
            age = input("Age: ")
            phone = input("Phone: ")
            pan = input("PAN: ")
            email = input("Email: ")
            password = input("Password: ")

            register_user(email, password, name, age, phone, pan)

        elif choice == "2":
            print("\n--- Login ---")
            email = input("Email: ")
            password = input("Password: ")
            login_user(email, password)

        elif choice == "3":
            logout_user()

        elif choice == "4":
            session = get_session()
            if session:
                print("👍 Logged in as:", session["email"])
            else:
                print("⚠ No user logged in.")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("❌ Invalid choice.")
