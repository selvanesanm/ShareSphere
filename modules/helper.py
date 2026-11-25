"""Small helpers shared by the console menus."""

import os

from pymysql.cursors import DictCursor


def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def line():
    """Print a divider used in menu screens."""
    print("=" * 40)


def check_email(email):
    """Return whether an email contains the basic expected characters."""
    return "@" in email and "." in email


def check_mobile(mobile):
    """Return whether a mobile number contains exactly ten digits."""
    return mobile.isdigit() and len(mobile) == 10


def wait():
    """Pause until the user presses Enter."""
    input("\nPress Enter to continue...")


def dict_cursor(conn):
    """Create a PyMySQL cursor that returns rows as dictionaries."""
    return conn.cursor(DictCursor)
