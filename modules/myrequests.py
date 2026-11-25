"""Menus for viewing and responding to requests."""

from modules.helper import clear, dict_cursor, line, wait
from modules.request_helpers import respond_to_request


def requests_menu(conn, user):
    """Show sent and received requests."""
    while True:
        clear()
        line()
        print("MY REQUESTS ⏳")
        line()
        print("1. Sent Requests 🚀")
        print("2. Received Requests 📩")
        print("3. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            sent_requests(conn, user)
        elif choice == "2":
            received_requests(conn, user)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
            wait()


def sent_requests(conn, user):
    """List requests sent by the signed-in user."""
    query = """
        SELECT r.service_type, r.status, r.quantity, u.name,
               CASE
                   WHEN hidden_number.user_id IS NULL THEN u.mobile
                   ELSE NULL
               END AS mobile
        FROM requests AS r
        JOIN users AS u ON u.user_id = r.receiver_id
        LEFT JOIN removed_connections AS hidden_number
          ON hidden_number.user_id = u.user_id
         AND hidden_number.other_user_id = r.sender_id
        WHERE r.sender_id = %s
    """
    cursor = dict_cursor(conn)
    try:
        cursor.execute(query, (user["user_id"],))
        rows = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    print("SENT REQUESTS 🚀")
    line()
    if not rows:
        print("You have not sent any requests yet.")
    else:
        for number, request in enumerate(rows, start=1):
            quantity = (
                f" - Quantity: {request['quantity']}"
                if request["service_type"] == "FoodShare"
                and request["quantity"] is not None
                else ""
            )
            if request["status"] != "Accepted":
                mobile = " - Mobile: hidden until accepted"
            elif request["mobile"]:
                mobile = f" - Mobile: {request['mobile']}"
            else:
                mobile = " - Mobile: hidden by the other user"
            print(
                f"{number}. [{request['service_type']}] To: {request['name']} "
                f"- Status: {request['status']}{quantity}{mobile}"
            )
    wait()


def received_requests(conn, user):
    """List received requests and update a selected request's status."""
    query = """
        SELECT r.request_id, r.service_type, r.status, r.quantity, u.name,
               CASE
                   WHEN hidden_number.user_id IS NULL THEN u.mobile
                   ELSE NULL
               END AS mobile
        FROM requests AS r
        JOIN users AS u ON u.user_id = r.sender_id
        LEFT JOIN removed_connections AS hidden_number
          ON hidden_number.user_id = u.user_id
         AND hidden_number.other_user_id = r.receiver_id
        WHERE r.receiver_id = %s
    """
    cursor = dict_cursor(conn)
    try:
        cursor.execute(query, (user["user_id"],))
        rows = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    print("RECEIVED REQUESTS 📩")
    line()
    if not rows:
        print("No requests received.")
        wait()
        return

    for number, request in enumerate(rows, start=1):
        quantity = (
            f" - Quantity requested: {request['quantity']}"
            if request["service_type"] == "FoodShare"
            and request["quantity"] is not None
            else ""
        )
        if request["status"] != "Accepted":
            mobile = " - Mobile: hidden until accepted"
        elif request["mobile"]:
            mobile = f" - Mobile: {request['mobile']}"
        else:
            mobile = " - Mobile: hidden by the other user"
        print(
            f"{number}. [{request['service_type']}] From: {request['name']} "
            f"- Status: {request['status']}{quantity}{mobile}"
        )

    choice = input("\nSelect a request to respond to (0 to go back): ").strip()
    if not choice.isdigit():
        return

    index = int(choice)
    if index == 0 or index > len(rows):
        return

    selected = rows[index - 1]
    if selected["status"] != "Pending":
        print("\nThis request has already been answered.")
        wait()
        return

    print("\n1. Accept 🟢")
    print("2. Reject 🔴")
    action = input("Choose: ").strip()
    new_status = {"1": "Accepted", "2": "Rejected"}.get(action)
    if new_status is None:
        return

    result = respond_to_request(
        conn,
        selected["request_id"],
        user["user_id"],
        new_status,
    )
    if result == "accepted":
        mobile = selected["mobile"] or "hidden"
        if selected["service_type"] == "FoodShare":
            print(
                f"\nFood request accepted. Mobile: {mobile}. "
                "The post remains available for the remaining quantity."
            )
        else:
            print(
                f"\nRequest accepted. Mobile: {mobile}. "
                "The post is now unavailable."
            )
            print("No other pending requests existed for this post.")
    elif result == "accepted_with_rejections":
        mobile = selected["mobile"] or "hidden"
        if selected["service_type"] == "FoodShare":
            print(
                f"\nFood request accepted. Mobile: {mobile}. "
                "The post closes automatically when its remaining quantity "
                "reaches 0."
            )
        else:
            print(
                f"\nRequest accepted. Mobile: {mobile}. "
                "The post is now unavailable."
            )
        print("Other pending requests for this post were rejected.")
    elif result == "rejected":
        print("\nRequest rejected.")
    elif result == "post_unavailable":
        print("\nThis post is no longer available.")
    elif result == "insufficient_quantity":
        print(
            "\nNot enough food remains for this request. "
            "The request was rejected."
        )
    else:
        print("\nThis request has already been handled.")
    wait()
