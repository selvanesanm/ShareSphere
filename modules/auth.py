"""Registration and login functions for users and administrators."""

from pymysql.err import IntegrityError

from modules.helper import (
    check_email,
    check_mobile,
    clear,
    dict_cursor,
    line,
    wait,
)


def register_user(conn):
    """Collect details and create a user account."""
    clear()
    line()
    print("        USER REGISTRATION📝")
    line()

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    if not check_email(email):
        print("Invalid email. Try again.❌")
        wait()
        return

    mobile = input("Mobile: ").strip()
    if not check_mobile(mobile):
        print("Mobile number should be 10 digits.")
        wait()
        return

    password = input("Password: ")
    if len(password) < 4:
        print("Password too short; minimum 4 characters.")
        wait()
        return

    location = input("City: ").strip()
    query = """
        INSERT INTO users (name, email, mobile, password, location)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query, (name, email, mobile, password, location))
        conn.commit()
    except IntegrityError:
        conn.rollback()
        print("That email address or mobile number is already registered. ⚠️👤")
    else:
        print("\nRegistration successful. You can now log in. 🎉✅")
    finally:
        cursor.close()
    wait()


def login_user(conn):
    """Authenticate a user using their mobile number and password."""
    clear()
    line()
    print("        USER LOGIN 🔒")
    line()

    mobile = input("Mobile: ").strip()
    password = input("Password: ")

    cursor = dict_cursor(conn)
    try:
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        user = cursor.fetchone()
    finally:
        cursor.close()

    if user and password == user["password"]:
        print(f"\nWelcome, {user['name']}.🗝️")
        wait()
        return user

    print("\nWrong mobile number or password.❌")
    wait()
    return None


def login_admin(conn):
    """Authenticate an administrator by username and password."""
    clear()
    line()
    print("        ADMIN LOGIN 🔒")
    line()

    username = input("Username: ").strip()
    password = input("Password: ")

    cursor = dict_cursor(conn)
    try:
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
    finally:
        cursor.close()

    if admin and password == admin["password"]:
        print("\nAdmin login successful.🗝️")
        wait()
        return admin

    print("\nWrong admin username or password.❌")
    wait()
    return None
