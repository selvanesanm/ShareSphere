# ShareSphere – Community Sharing Platform

ShareSphere is a Python and MySQL console-based project that helps people in a community share skills, food, and local help with each other. Users can post what they can offer or what they need and connect with other users through requests.

## Features

* User registration and login
* Separate admin login
* **SkillSwap** – Share skills and find people who can teach or help with different skills.
* **FoodShare** – Share available food with others and request the required quantity.
* **LocalHelper** – Offer or request help for local activities and tasks.
* Create, view, update, and delete your own posts.
* Send, accept, and reject requests.
* View sent and received requests.
* Manage connections with other users.
* Edit profile and change password.
* Admin can manage users, posts, requests, and view reports.
* Mobile numbers are hidden until a request is accepted.

## Technologies Used

* Python
* MySQL
* PyMySQL

## Project Structure

```text
ShareSphere/
│
├── main.py
├── db.py
├── schema.sql
├── requirements.txt
├── README.md
│
└── modules/
    ├── __init__.py
    ├── helper.py
    ├── auth.py
    ├── skillswap.py
    ├── foodshare.py
    ├── localhelper.py
    ├── myrequests.py
    ├── connections.py
    ├── profile.py
    └── admin.py
```

## How to Run

1. Install Python and MySQL on your computer.
2. Open MySQL Workbench and execute `schema.sql` to create the database and tables.
3. Configure your MySQL connection details using environment variables.
4. Install the required package:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
python main.py
```

## Database

The project uses MySQL to store user details, posts, requests, connections, and other application data.

## What I Learned

Through this project, I learned how to connect Python with MySQL, organize a Python project using modules, perform CRUD operations, handle user requests, and work with database relationships.

---

**Developed as a Python and MySQL project.**
