"""Owner-only post management helpers."""

from pymysql.err import IntegrityError

from modules.helper import clear, dict_cursor, line, wait


def delete_own_post(conn, user, table, id_column, name_column, title):
    """Delete one of the signed-in user's posts if it has no request history."""
    cursor = dict_cursor(conn)
    try:
        cursor.execute(
            f"""
            SELECT {id_column} AS id, {name_column} AS name, status
            FROM {table}
            WHERE user_id = %s
            ORDER BY {id_column}
            """,
            (user["user_id"],),
        )
        posts = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    print(f"DELETE MY {title}")
    line()
    if not posts:
        print(f"You have no {title.lower()} posts.")
        wait()
        return

    for number, post in enumerate(posts, start=1):
        print(
            f"{number}. {post['name']} "
            f"({post['status']}, ID: {post['id']})"
        )

    choice = input("\nSelect a post to delete (0 to go back): ").strip()
    if not choice.isdigit():
        return
    index = int(choice)
    if index == 0 or index > len(posts):
        return

    selected = posts[index - 1]
    confirmation = input(
        f"Delete '{selected['name']}'? This cannot be undone (y/N): "
    ).strip().lower()
    if confirmation != "y":
        print("\nDeletion cancelled.")
        wait()
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            DELETE FROM {table}
            WHERE {id_column} = %s AND user_id = %s
            """,
            (selected["id"], user["user_id"]),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            print("\nThis post could not be found.")
        else:
            conn.commit()
            print("\nPost deleted.")
    except IntegrityError:
        conn.rollback()
        print(
            "\nThis post cannot be deleted because it has request history."
        )
    finally:
        cursor.close()
    wait()


def update_own_post(
    conn,
    user,
    table,
    id_column,
    name_column,
    description_column,
    title,
    quantity_column=None,
    min_name_length=None,
):
    """Update one of the signed-in user's existing posts."""
    columns = (
        f"{id_column} AS id, {name_column} AS name, "
        f"{description_column} AS description"
    )
    if quantity_column:
        columns += f", {quantity_column} AS quantity"

    cursor = dict_cursor(conn)
    try:
        cursor.execute(
            f"""
            SELECT {columns}, status
            FROM {table}
            WHERE user_id = %s
            ORDER BY {id_column}
            """,
            (user["user_id"],),
        )
        posts = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    print(f"UPDATE MY {title}")
    line()
    if not posts:
        print(f"You have no {title.lower()} posts.")
        wait()
        return

    for number, post in enumerate(posts, start=1):
        print(
            f"{number}. {post['name']} "
            f"({post['status']}, ID: {post['id']})"
        )

    choice = input("\nSelect a post to update (0 to go back): ").strip()
    if not choice.isdigit():
        return
    index = int(choice)
    if index == 0 or index > len(posts):
        return

    selected = posts[index - 1]
    print("\nPress Enter to keep each current value.")
    name = input(f"Name [{selected['name']}]: ").strip()
    while len(name or selected["name"]) < (min_name_length or 0):
        print(f"Name must contain at least {min_name_length} characters.")
        name = input(f"Name [{selected['name']}]: ").strip()
    if not name:
        name = selected["name"]
    description = input(
        f"Description [{selected['description'] or ''}]: "
    ).strip()
    if not description:
        description = selected["description"]

    update_columns = [f"{name_column} = %s", f"{description_column} = %s"]
    values = [name, description]
    if quantity_column:
        quantity = input(
            f"Quantity [{selected['quantity']}]: "
        ).strip()
        if quantity:
            while not quantity.isdecimal() or int(quantity) < 1:
                print("Enter a whole number greater than 0.")
                quantity = input(
                    f"Quantity [{selected['quantity']}]: "
                ).strip()
            selected_quantity = int(quantity)
        else:
            selected_quantity = selected["quantity"]
        update_columns.append(f"{quantity_column} = %s")
        values.append(selected_quantity)

    values.extend((selected["id"], user["user_id"]))
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            UPDATE {table}
            SET {", ".join(update_columns)}
            WHERE {id_column} = %s AND user_id = %s
            """,
            tuple(values),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()

    print("\nPost updated successfully.")
    wait()
