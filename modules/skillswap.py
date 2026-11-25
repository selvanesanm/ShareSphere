"""SkillSwap menus for finding and offering skills."""

from modules.helper import clear, dict_cursor, line, wait
from modules.my_posts import delete_own_post, update_own_post
from modules.request_helpers import send_request


def skillswap_menu(conn, user):
    """Display the SkillSwap menu."""
    while True:
        clear()
        line()
        print("        SKILLSWAP 📚")
        line()
        print("1. Explore Skill **🔍")
        print("2. Share Skill **🧑‍🏫")

        print("3. Delete My Skill")
        print("4. Update My Skill")
        print("5. Back")

        choice = input("Choose: ").strip()
        if choice == "1":
            find_skill(conn, user)
        elif choice == "2":
            offer_skill(conn, user)
        elif choice == "3":
            delete_own_post(
                conn, user, "skills", "skill_id", "skill_name", "SKILLS"
            )
        elif choice == "4":
            update_own_post(
                conn,
                user,
                "skills",
                "skill_id",
                "skill_name",
                "description",
                "SKILLS",
                min_name_length=2,
            )
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            wait()


def find_skill(conn, user):
    """List available skills in the chosen city and let the user request one."""
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
        SELECT s.skill_id, s.skill_name, s.description, u.name, u.user_id
        FROM skills AS s
        JOIN users AS u ON u.user_id = s.user_id
        WHERE s.status = 'Available'
          AND s.user_id != %s
    """
    parameters = [user["user_id"]]
    if not show_all_cities:
        query += " AND LOWER(u.location) = LOWER(%s)"
        parameters.append(city_input)

    cursor = dict_cursor(conn)
    try:
        cursor.execute(query, tuple(parameters))
        skills = cursor.fetchall()
    finally:
        cursor.close()

    clear()
    line()
    heading = "ALL CITIES" if show_all_cities else city_input.upper()
    print(f"AVAILABLE SKILLS IN {heading}")
    line()
    if not skills:
        place = "any city" if show_all_cities else city_input
        print(f"No skills available in {place} right now.")
        wait()
        return

    for number, skill in enumerate(skills, start=1):
        print(f"{number}. {skill['skill_name']} (by {skill['name']})")

    choice = input("\nSelect skill number (0 to go back): ").strip()
    if not choice.isdigit():
        return

    index = int(choice)
    if index == 0 or index > len(skills):
        return

    selected = skills[index - 1]
    clear()
    line()
    print("SKILL DETAILS")
    line()
    print(f"Skill: {selected['skill_name']}")
    print(f"Offered by: {selected['name']}")
    print(f"Description: {selected['description'] or ''}")
    print("\n1. Send Request")
    print("2. Back")

    if input("Choose: ").strip() == "1":
        result = send_request(
            conn,
            user["user_id"],
            selected["user_id"],
            "SkillSwap",
            selected["skill_id"],
        )
        if result == "sent":
            print("\n✅ Request sent.")
        elif result == "duplicate":
            print("\n⚠️ You have already requested this skill.")
        else:
            print("\n❌ This skill is no longer available.")
        wait()


def offer_skill(conn, user):
    """Create a skill post for the signed-in user."""
    clear()
    line()
    print("OFFER A SKILL")
    line()

    skill_name = input("Skill name: ").strip()
    while len(skill_name) < 2:
        print("Skill name must contain at least 2 characters.")
        skill_name = input("Skill name: ").strip()
    description = input("Description: ").strip()

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO skills (user_id, skill_name, description)
            VALUES (%s, %s, %s)
            """,
            (user["user_id"], skill_name, description),
        )
        conn.commit()
    finally:
        cursor.close()

    print("\nSkill posted successfully.✅📚")
    wait()
