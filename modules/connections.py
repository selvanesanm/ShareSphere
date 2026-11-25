"""Display people connected through sent or received requests."""

from modules.helper import clear, dict_cursor, line, wait


def connections_menu(conn, user):
    """Show each connected person once, regardless of how many requests exist."""
    query = """
        SELECT
            u.user_id,
            u.name,
            CASE
                WHEN hidden_number.user_id IS NULL THEN u.mobile
                ELSE NULL
            END AS mobile,
            u.location,
            GROUP_CONCAT(DISTINCT r.service_type ORDER BY r.service_type SEPARATOR ', ') AS services,
            CASE
                WHEN SUM(CASE WHEN r.status = 'Accepted' THEN 1 ELSE 0 END) > 0 THEN 'Accepted'
                ELSE 'Pending'
            END AS connection_status
        FROM requests AS r
        JOIN users AS u
          ON u.user_id = CASE
              WHEN r.sender_id = %s THEN r.receiver_id
              ELSE r.sender_id
          END
        LEFT JOIN removed_connections AS hidden_number
          ON hidden_number.user_id = u.user_id
         AND hidden_number.other_user_id = %s
        LEFT JOIN removed_connections AS removed_by_me
          ON removed_by_me.user_id = %s
         AND removed_by_me.other_user_id = u.user_id
        WHERE (r.sender_id = %s OR r.receiver_id = %s)
          AND removed_by_me.user_id IS NULL
        GROUP BY u.user_id, u.name, u.mobile, u.location,
                 hidden_number.user_id, removed_by_me.user_id
        ORDER BY u.name
    """
    cursor = dict_cursor(conn)
    try:
        user_id = user["user_id"]
        cursor.execute(query, (user_id, user_id, user_id, user_id, user_id))
        rows = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    print("MY CONNECTIONS 🤝")
    line()
    if not rows:
        print("No connections yet.")
        wait()
        return

    for number, connection in enumerate(rows, start=1):
        print(f"{number}. {connection['name']}")
        print(f"   Services: {connection['services']}")
        print(f"   Location: {connection['location'] or ''}")
        if (
            connection["connection_status"] == "Accepted"
            and connection["mobile"]
        ):
            print(f"   Mobile: {connection['mobile']}")
        elif connection["connection_status"] == "Accepted":
            print("   Mobile: hidden by the other user")
        else:
            print("   Mobile: hidden until the request is accepted")
        print()

    choice = input(
        "Enter a connection number to remove (or press Enter to go back): "
    ).strip()
    if not choice:
        return
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(rows):
        print("Invalid connection number.")
        wait()
        return

    selected = rows[int(choice) - 1]
    confirmation = input(
        f"Remove {selected['name']} from your connections and hide your "
        "mobile number from them? Request history will be kept (y/N): "
    ).strip().lower()
    if confirmation != "y":
        print("\nRemoval cancelled.")
        wait()
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO removed_connections (user_id, other_user_id)
            VALUES (%s, %s)
            """,
            (user["user_id"], selected["user_id"]),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()

    print(
        f"\n{selected['name']} was removed from your connections. "
        "Your mobile number is hidden from them; request history was kept."
    )
    wait()
