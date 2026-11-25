"""Profile editing and password changes."""

from modules.helper import check_email, clear, line, wait


def profile_menu(conn, user):
    """Show the profile menu for the signed-in user."""
    while True:
        clear()
        line()
        print("MY PROFILE👤🪪")
        line()
        print(f"Name: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"Mobile: {user['mobile']}")
        print(f"Location: {user['location'] or ''}")
        print()
        print("1. Edit Profile")
        print("2. Change Password")
        print("3. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            edit_profile(conn, user)
        elif choice == "2":
            change_password(conn, user)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
            wait()


def edit_profile(conn, user):
    """Update the user's name, email, or city."""
    clear()
    line()
    print("EDIT PROFILE")
    line()
    print("Leave a field blank to keep its current value.")

    name = input(f"Name ({user['name']}): ").strip() or user["name"]
    email = input(f"Email ({user['email']}): ").strip() or user["email"]
    if not check_email(email):
        print("Invalid email. Changes were not saved.")
        wait()
        return

    current_location = user.get("location") or ""
    location = input(f"City ({current_location}): ").strip() or user.get("location")

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET name = %s, email = %s, location = %s
            WHERE user_id = %s
            """,
            (name, email, location, user["user_id"]),
        )
        conn.commit()
    finally:
        cursor.close()

    user["name"] = name
    user["email"] = email
    user["location"] = location
    print("\nProfile updated.")
    wait()


def change_password(conn, user):
    """Change the user's password after checking the current one."""
    clear()
    line()
    print("CHANGE PASSWORD")
    line()

    old_password = input("Current password: ")
    if old_password != user["password"]:
        print("Current password is incorrect.")
        wait()
        return

    new_password = input("New password: ")
    if len(new_password) < 4:
        print("Password must contain at least 4 characters.")
        wait()
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE user_id = %s",
            (new_password, user["user_id"]),
        )
        conn.commit()
    finally:
        cursor.close()

    user["password"] = new_password
    print("\nPassword changed.")
    wait()
