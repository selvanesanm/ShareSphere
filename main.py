"""Entry point and top-level menus for ShareSphere."""

from db import connect_db
from modules.admin import admin_menu
from modules.auth import login_admin, login_user, register_user
from modules.connections import connections_menu
from modules.foodshare import foodshare_menu
from modules.helper import clear, line, wait
from modules.localhelper import localhelper_menu
from modules.myrequests import requests_menu
from modules.profile import profile_menu
from modules.skillswap import skillswap_menu


def user_dashboard(conn, user):
    """Show the signed-in user's feature menu."""
    while True:
        clear()
        line()
        print(f"        USER DASHBOARD - {user['name']} ")
        line()
        print("1. SKILLSWAP 📚")
        print("2. FOODHUB 🍱")
        print("3. HELPMATE 🦸")
        print("4. My Requests")
        print("5. My Connections")
        print("6. My Profile")
        print("7. Logout 🚪")

        choice = input("Choose: ").strip()
        if choice == "1":
            skillswap_menu(conn, user)
        elif choice == "2":
            foodshare_menu(conn, user)
        elif choice == "3":
            localhelper_menu(conn, user)
        elif choice == "4":
            requests_menu(conn, user)
        elif choice == "5":
            connections_menu(conn, user)
        elif choice == "6":
            profile_menu(conn, user)
        elif choice == "7":
            print("\nLogged out.")
            wait()
            break
        else:
            print("Invalid choice.")
            wait()


def main():
    """Start the application and close its database connection on exit."""
    conn = connect_db()
    try:
        while True:
            clear()
            line()
            print("        💚🌍SHARESPHERE🌍💚        ")
            line()
            print("1. User Registration")
            print("2. User Login")
            print("3. Admin Login")
            print("4. Exit 🔚")

            choice = input("Choose: ").strip()
            if choice == "1":
                register_user(conn)
            elif choice == "2":
                user = login_user(conn)
                if user:
                    user_dashboard(conn, user)
            elif choice == "3":
                admin = login_admin(conn)
                if admin:
                    admin_menu(conn)
            elif choice == "4":
                print("\nThank you for using ShareSphere. Goodbye!")
                break
            else:
                print("Invalid choice.")
                wait()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
