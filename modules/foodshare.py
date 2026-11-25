"""FoodShare menus for finding and sharing food."""

from modules.helper import clear, dict_cursor, line, wait
from modules.my_posts import delete_own_post, update_own_post
from modules.request_helpers import send_request


def foodshare_menu(conn, user):
    """Display the FoodShare menu."""
    while True:
        clear()
        line()
        print("        FOODHUB 🍱")
        line()
        print("1. Get Food **🍽️")
        print("2. Share Food **🍕")

        print("3. Delete My Food")
        print("4. Update My Food")
        print("5. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            find_food(conn, user)
        elif choice == "2":
            share_food(conn, user)
        elif choice == "3":
            delete_own_post(
                conn,
                user,
                "food_items",
                "food_id",
                "food_name",
                "FOOD POSTS",
            )
        elif choice == "4":
            update_own_post(
                conn,
                user,
                "food_items",
                "food_id",
                "food_name",
                "description",
                "FOOD POSTS",
                "quantity",
                min_name_length=2,
            )
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            wait()


def find_food(conn, user):
    """List available food in the chosen city and let the user request it."""
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
        SELECT f.food_id, f.food_name, f.description, f.quantity,
               COALESCE((
                   SELECT SUM(COALESCE(r.quantity, f.quantity))
                   FROM requests AS r
                   WHERE r.food_id = f.food_id AND r.status = 'Pending'
               ), 0) AS pending_quantity,
               u.name, u.user_id
        FROM food_items AS f
        JOIN users AS u ON u.user_id = f.user_id
        WHERE f.status = 'Available'
          AND f.user_id != %s
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

    items = [
        item
        for item in items
        if item["quantity"] > item["pending_quantity"]
    ]

    clear()
    line()
    heading = "ALL CITIES" if show_all_cities else city_input.upper()
    print(f"AVAILABLE FOOD IN {heading}")
    line()
    if not items:
        place = "any city" if show_all_cities else city_input
        print(f"No food available in {place} right now.")
        wait()
        return

    for number, item in enumerate(items, start=1):
        available_quantity = max(
            item["quantity"] - item["pending_quantity"], 0
        )
        print(
            f"{number}. {item['food_name']} "
            f"({available_quantity} available for new requests, "
            f"by {item['name']})"
        )

    choice = input("\nSelect food number (0 to go back): ").strip()
    if not choice.isdigit():
        return

    index = int(choice)
    if index == 0 or index > len(items):
        return

    selected = items[index - 1]
    requestable_quantity = max(
        selected["quantity"] - selected["pending_quantity"], 0
    )
    clear()
    line()
    print("FOOD DETAILS 📋")
    line()
    print(f"Food: {selected['food_name']}")
    print(f"Shared by: {selected['name']}")
    print(f"Quantity on post: {selected['quantity']}")
    print(f"Quantity available: {requestable_quantity}")
    print(f"Description: {selected['description'] or ''}")
    print("\n1. Send Request")
    print("2. Back")

    if input("Choose: ").strip() == "1":
        if requestable_quantity == 0:
            print("\nAll remaining food is already requested.")
            wait()
            return
        requested_quantity = input("Quantity to request: ").strip()
        while (
            not requested_quantity.isdecimal()
            or int(requested_quantity) < 1
            or int(requested_quantity) > requestable_quantity
        ):
            print(
                f"Enter a whole number from 1 to {requestable_quantity}."
            )
            requested_quantity = input("Quantity to request: ").strip()

        result = send_request(
            conn,
            user["user_id"],
            selected["user_id"],
            "FoodShare",
            selected["food_id"],
            int(requested_quantity),
        )
        if result == "sent":
            print("\n✅ Request sent.")
        elif result == "duplicate":
            print("\n⚠️ You have already requested this food.")
        elif result == "insufficient_quantity":
            print("\n🍱 There is not enough food available for that request.")
        else:
            print("\n❌ This food is no longer available.")
        wait()


def share_food(conn, user):
    """Create a food post for the signed-in user."""
    clear()
    line()
    print("SHARE FOOD")
    line()

    food_name = input("Food name: ").strip()
    while len(food_name) < 2:
        print("Food name must contain at least 2 characters.")
        food_name = input("Food name: ").strip()
    quantity = input("Quantity (whole number): ").strip()
    while not quantity.isdecimal() or int(quantity) < 1:
        print("Enter a whole number greater than 0.")
        quantity = input("Quantity (whole number): ").strip()
    description = input("Description: ").strip()

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO food_items (user_id, food_name, quantity, description)
            VALUES (%s, %s, %s, %s)
            """,
            (user["user_id"], food_name, int(quantity), description),
        )
        conn.commit()
    finally:
        cursor.close()

    print("\nFood posted successfully.✅🍱")
    wait()
