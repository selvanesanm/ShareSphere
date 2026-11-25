"""Administrator menus for managing ShareSphere data and reports."""

from pymysql.err import IntegrityError

from modules.helper import clear, dict_cursor, line, wait


POST_TABLES = {
    "2": ("skills", "skill_id", "skill_name", "SKILLSWAP"),
    "3": ("food_items", "food_id", "food_name", "FOODSHARE"),
    "4": ("help_items", "help_id", "help_type", "LOCALHELPER"),
}


def admin_menu(conn):
    """Display the administrator dashboard."""
    while True:
        clear()
        line()
        print("ADMIN DASHBOARD")
        line()
        print("1. Manage Users")
        print("2. Manage SkillSwap")
        print("3. Manage FoodShare")
        print("4. Manage LocalHelper")
        print("5. Manage Requests")
        print("6. Reports")
        print("7. Logout")

        choice = input("Choose: ").strip()
        if choice == "1":
            manage_users(conn)
        elif choice in POST_TABLES:
            manage_posts(conn, *POST_TABLES[choice])
        elif choice == "5":
            manage_requests(conn)
        elif choice == "6":
            reports(conn)
        elif choice == "7":
            break
        else:
            print("Invalid choice.")
            wait()


def manage_users(conn):
    """View, search, or delete user accounts."""
    while True:
        clear()
        line()
        print("MANAGE USERS")
        line()
        print("1. View Users")
        print("2. Search User")
        print("3. Delete User")
        print("4. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            query = """
                SELECT user_id, name, email, mobile, location
                FROM users
            """
            cursor = dict_cursor(conn)
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
            finally:
                cursor.close()
            show_rows(rows)
            wait()
        elif choice == "2":
            search_term = input("Search name, email, or mobile: ").strip()
            query = """
                SELECT user_id, name, email, mobile, location
                FROM users
                WHERE name LIKE %s OR email LIKE %s OR mobile LIKE %s
            """
            pattern = f"%{search_term}%"
            cursor = dict_cursor(conn)
            try:
                cursor.execute(query, (pattern, pattern, pattern))
                rows = cursor.fetchall()
            finally:
                cursor.close()
            show_rows(rows)
            wait()
        elif choice == "3":
            user_id = input("Enter user ID to delete: ").strip()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
            except IntegrityError:
                conn.rollback()
                print(
                    "This user cannot be deleted while posts or requests "
                    "are linked to their account."
                )
            else:
                if cursor.rowcount:
                    print("User deleted.")
                else:
                    print("No user found with that ID.")
            finally:
                cursor.close()
            wait()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            wait()


def manage_posts(conn, table, id_column, name_column, title):
    """View, search, or delete posts from a configured service table."""
    while True:
        clear()
        line()
        print(f"MANAGE {title}")
        line()
        print("1. View Posts")
        print("2. Search Post")
        print("3. Delete Post")
        print("4. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            rows = _get_posts(conn, table, id_column, name_column)
            show_rows(rows)
            wait()
        elif choice == "2":
            search_term = input("Search by name: ").strip()
            rows = _get_posts(conn, table, id_column, name_column, search_term)
            show_rows(rows)
            wait()
        elif choice == "3":
            post_id = input("Enter post ID to delete: ").strip()
            query = f"DELETE FROM {table} WHERE {id_column} = %s"
            cursor = conn.cursor()
            try:
                cursor.execute(query, (post_id,))
                conn.commit()
                if cursor.rowcount:
                    print("Post deleted.")
                else:
                    print("No post found with that ID.")
            except IntegrityError:
                conn.rollback()
                print("This post has request history and cannot be deleted.")
            finally:
                cursor.close()
            wait()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            wait()


def _get_posts(conn, table, id_column, name_column, search_term=None):
    """Fetch posts and their owners from a service table."""
    query = f"""
        SELECT post.{id_column} AS id,
               post.{name_column} AS name,
               post.status,
               users.name AS owner
        FROM {table} AS post
        JOIN users ON users.user_id = post.user_id
    """
    parameters = ()
    if search_term is not None:
        query += f" WHERE post.{name_column} LIKE %s"
        parameters = (f"%{search_term}%",)

    cursor = dict_cursor(conn)
    try:
        cursor.execute(query, parameters)
        return cursor.fetchall()
    finally:
        cursor.close()


def manage_requests(conn):
    """View all requests or filter them by status."""
    query = """
        SELECT r.request_id, r.service_type, r.status,
               sender.name AS sender, receiver.name AS receiver
        FROM requests AS r
        JOIN users AS sender ON sender.user_id = r.sender_id
        JOIN users AS receiver ON receiver.user_id = r.receiver_id
    """
    status_by_choice = {
        "2": "Pending",
        "3": "Accepted",
        "4": "Rejected",
    }

    while True:
        clear()
        line()
        print("MANAGE REQUESTS")
        line()
        print("1. View All Requests")
        print("2. View Pending Requests")
        print("3. View Accepted Requests")
        print("4. View Rejected Requests")
        print("5. Back")

        choice = input("Choose: ").strip()
        if choice == "5":
            break
        if choice not in {"1", *status_by_choice}:
            print("Invalid choice.")
            wait()
            continue

        filtered_query = query
        parameters = ()
        if choice in status_by_choice:
            filtered_query += " WHERE r.status = %s"
            parameters = (status_by_choice[choice],)

        cursor = dict_cursor(conn)
        try:
            cursor.execute(filtered_query, parameters)
            rows = cursor.fetchall()
        finally:
            cursor.close()
        show_rows(rows)
        wait()


def reports(conn):
    """Display live user, service, and request counts."""
    while True:
        clear()
        line()
        print("REPORTS")
        line()
        print("1. User Statistics")
        print("2. Service Statistics")
        print("3. Request Statistics")
        print("4. Back")

        choice = input("Choose: ").strip()
        if choice == "4":
            break
        if choice not in {"1", "2", "3"}:
            print("Invalid choice.")
            wait()
            continue

        cursor = conn.cursor()
        try:
            if choice == "1":
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                clear()
                line()
                print("USER STATISTICS")
                line()
                print(f"Total users: {total_users}")
            elif choice == "2":
                service_counts = {}
                for table, label in (
                    ("skills", "Skills"),
                    ("food_items", "Food posts"),
                    ("help_items", "Help posts"),
                ):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    service_counts[label] = cursor.fetchone()[0]

                clear()
                line()
                print("SERVICE STATISTICS")
                line()
                for label, count in service_counts.items():
                    print(f"Total {label.lower()}: {count}")
            else:
                cursor.execute(
                    "SELECT status, COUNT(*) FROM requests GROUP BY status"
                )
                rows = cursor.fetchall()
                clear()
                line()
                print("REQUEST STATISTICS")
                line()
                total_requests = sum(count for _, count in rows)
                print(f"Total Requests: {total_requests}")
                if not rows:
                    print("No requests yet.")
                for status, count in rows:
                    print(f"{status}: {count}")
        finally:
            cursor.close()
        wait()


def show_rows(rows):
    """Print database result rows in a readable console format."""
    if not rows:
        print("No records found.")
        return

    for row in rows:
        details = "  ".join(f"{key}: {value}" for key, value in row.items())
        print(details)
