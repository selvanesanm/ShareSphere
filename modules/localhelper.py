"""LocalHelper menus for finding and offering help."""

from modules.helper import clear, dict_cursor, line, wait
from modules.my_posts import delete_own_post, update_own_post
from modules.request_helpers import send_request


def localhelper_menu(conn, user):
    """Display the LocalHelper menu."""
    while True:
        clear()
        line()
        print("        HELPMATE 🦸")
        line()
        print("1. Get Help **🙋")
        print("2. Provide Help **🫴")

        print("3. Delete My Help")
        print("4. Update My Help")
        print("5. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            find_help(conn, user)
        elif choice == "2":
            offer_help(conn, user)
        elif choice == "3":
            delete_own_post(
                conn, user, "help_items", "help_id", "help_type", "HELP POSTS"
            )
        elif choice == "4":
            update_own_post(
                conn,
                user,
                "help_items",
                "help_id",
                "help_type",
                "description",
                "HELP POSTS",
                min_name_length=2,
            )
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            wait()


def find_help(conn, user):
    """List available help in the chosen city and let the user request it."""
    city_input = input(
        "Enter city to filter (or type 'all' for every city): "
    ).strip()
    while not city_input:
        print("Enter a city name or type 'all'.")
        city_input = input(
            "Enter city to filter (or type 'all' for every city): "
        ).strip()

    show_all_cities = city_input.lower() == "all"

    query = """
        SELECT h.help_id, h.help_type, h.description, u.name, u.user_id
        FROM help_items AS h
        JOIN users AS u ON u.user_id = h.user_id
        WHERE h.status = 'Available'
          AND h.user_id != %s
    """
    parameters = [user["user_id"]]
    if not show_all_cities:
        query += " AND LOWER(u.location) = LOWER(%s)"
        parameters.append(city_input)

    cursor = dict_cursor(conn)
    try:
        cursor.execute(query, tuple(parameters))
        items = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    heading = "ALL CITIES" if show_all_cities else city_input.upper()
    print(f"AVAILABLE HELP IN {heading}")
    line()
    if not items:
        place = "any city" if show_all_cities else city_input
        print(f"No help available in {place} right now.")
        wait()
        return

    for number, item in enumerate(items, start=1):
        print(f"{number}. {item['help_type']} (by {item['name']})")

    choice = input("\nSelect help number (0 to go back): ").strip()
    if not choice.isdigit():
        return

    index = int(choice)
    if index == 0 or index > len(items):
        return

    selected = items[index - 1]
    clear()
    line()
    print("HELP DETAILS")
    line()
    print(f"Help type: {selected['help_type']}")
    print(f"Offered by: {selected['name']}")
    print(f"Description: {selected['description'] or ''}")
    print("\n1. Send Request")
    print("2. Back")

    if input("Choose: ").strip() == "1":
        result = send_request(
            conn,
            user["user_id"],
            selected["user_id"],
            "LocalHelper",
            selected["help_id"],
        )
        if result == "sent":
            print("\n✅ Request sent.")
        elif result == "duplicate":
            print("\n⚠️ You have already requested this help.")
        else:
            print("\n❌ This help offer is no longer available.")
        wait()


def offer_help(conn, user):
    """Create a help offer for the signed-in user."""
    clear()
    line()
    print("OFFER HELP")
    line()

    help_type = input("Help type: ").strip()
    while len(help_type) < 2:
        print("Help type must contain at least 2 characters.")
        help_type = input("Help type: ").strip()
    description = input("Description: ").strip()

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO help_items (user_id, help_type, description)
            VALUES (%s, %s, %s)
            """,
            (user["user_id"], help_type, description),
        )
        conn.commit()
    finally:
        cursor.close()

    print("\nHelp offer posted successfully.✅🦸")
    wait()
