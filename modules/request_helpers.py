"""Shared request creation and response logic."""

REQUEST_TARGETS = {
    "SkillSwap": ("skills", "skill_id"),
    "FoodShare": ("food_items", "food_id"),
    "LocalHelper": ("help_items", "help_id"),
}


def send_request(
    conn, sender_id, receiver_id, service_type, item_id, quantity=None
):
    """Create a request for an available post if duplicate rules allow it."""
    table, item_column = REQUEST_TARGETS[service_type]
    if service_type == "FoodShare" and (
        not isinstance(quantity, int) or quantity < 1
    ):
        raise ValueError(
            "Food requests must have a positive whole-number quantity."
        )

    cursor = conn.cursor()
    try:
        selected_columns = (
            "user_id, quantity"
            if service_type == "FoodShare"
            else "user_id"
        )
        cursor.execute(
            f"""
            SELECT {selected_columns}
            FROM {table}
            WHERE {item_column} = %s AND status = 'Available'
            FOR UPDATE
            """,
            (item_id,),
        )
        post = cursor.fetchone()
        if post is None or post[0] != receiver_id:
            conn.rollback()
            return "unavailable"
        if service_type == "FoodShare":
            cursor.execute(
                """
                SELECT COALESCE(SUM(COALESCE(quantity, %s)), 0)
                FROM requests
                WHERE food_id = %s AND status = 'Pending'
                """,
                (post[1], item_id),
            )
            pending_quantity = cursor.fetchone()[0]
            if pending_quantity + quantity > post[1]:
                conn.rollback()
                return "insufficient_quantity"

        if service_type != "FoodShare":
            cursor.execute(
                f"""
                SELECT request_id
                FROM requests
                WHERE sender_id = %s
                  AND {item_column} = %s
                  AND status IN ('Pending', 'Accepted')
                LIMIT 1
                FOR UPDATE
                """,
                (sender_id, item_id),
            )
            if cursor.fetchone() is not None:
                conn.rollback()
                return "duplicate"

        request_columns = f"sender_id, receiver_id, service_type, {item_column}"
        request_values = [sender_id, receiver_id, service_type, item_id]
        placeholders = "%s, %s, %s, %s"
        if service_type == "FoodShare":
            request_columns += ", quantity"
            placeholders += ", %s"
            request_values.append(quantity)
        cursor.execute(
            f"INSERT INTO requests ({request_columns}) VALUES ({placeholders})",
            tuple(request_values),
        )
        conn.commit()
        return "sent"
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def respond_to_request(conn, request_id, receiver_id, response):
    """Accept or reject a pending request while protecting the post lifecycle."""
    if response not in {"Accepted", "Rejected"}:
        raise ValueError("Response must be either 'Accepted' or 'Rejected'.")

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT service_type, skill_id, food_id, help_id, quantity
            FROM requests
            WHERE request_id = %s
              AND receiver_id = %s
              AND status = 'Pending'
            FOR UPDATE
            """,
            (request_id, receiver_id),
        )
        request = cursor.fetchone()
        if request is None:
            conn.rollback()
            return "already_handled"

        if response == "Rejected":
            cursor.execute(
                """
                UPDATE requests
                SET status = 'Rejected'
                WHERE request_id = %s
                  AND receiver_id = %s
                  AND status = 'Pending'
                """,
                (request_id, receiver_id),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return "already_handled"
            conn.commit()
            return "rejected"

        service_type, skill_id, food_id, help_id, requested_quantity = request
        table, item_column = REQUEST_TARGETS[service_type]
        item_id = {
            "SkillSwap": skill_id,
            "FoodShare": food_id,
            "LocalHelper": help_id,
        }[service_type]

        selected_columns = (
            "user_id, status, quantity"
            if service_type == "FoodShare"
            else "user_id, status"
        )
        cursor.execute(
            f"""
            SELECT {selected_columns}
            FROM {table}
            WHERE {item_column} = %s
            FOR UPDATE
            """,
            (item_id,),
        )
        post = cursor.fetchone()
        if post is None or post[0] != receiver_id or post[1] != "Available":
            conn.rollback()
            return "post_unavailable"

        if service_type == "FoodShare":
            quantity_to_deduct = (
                requested_quantity
                if requested_quantity is not None
                else post[2]
            )
            remaining_quantity = post[2] - quantity_to_deduct
            if remaining_quantity < 0:
                cursor.execute(
                    """
                    UPDATE requests
                    SET status = 'Rejected'
                    WHERE request_id = %s
                    """,
                    (request_id,),
                )
                conn.commit()
                return "insufficient_quantity"

        cursor.execute(
            """
            UPDATE requests
            SET status = 'Accepted'
            WHERE request_id = %s
              AND receiver_id = %s
              AND status = 'Pending'
            """,
            (request_id, receiver_id),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            return "already_handled"

        rejected_count = 0
        if service_type == "FoodShare":
            cursor.execute(
                """
                UPDATE food_items
                SET quantity = %s,
                    status = CASE WHEN %s = 0 THEN 'Unavailable' ELSE 'Available' END
                WHERE food_id = %s
                """,
                (remaining_quantity, remaining_quantity, item_id),
            )
            if remaining_quantity == 0:
                cursor.execute(
                    """
                    UPDATE requests
                    SET status = 'Rejected'
                    WHERE food_id = %s
                      AND request_id != %s
                      AND status = 'Pending'
                    """,
                    (item_id, request_id),
                )
                rejected_count = cursor.rowcount
        else:
            cursor.execute(
                f"""
                UPDATE {table}
                SET status = 'Unavailable'
                WHERE {item_column} = %s
                """,
                (item_id,),
            )
            cursor.execute(
                f"""
                UPDATE requests
                SET status = 'Rejected'
                WHERE {item_column} = %s
                  AND request_id != %s
                  AND status = 'Pending'
                """,
                (item_id, request_id),
            )
            rejected_count = cursor.rowcount
        conn.commit()
        return "accepted_with_rejections" if rejected_count > 0 else "accepted"
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
