# ShareSphere

A simple python + mysql console project for sharing skills, food and help with neighbours.

## What it does
- User can register and login
- Admin can login separately
- Users can post/find Skills, Food, Help
- Skill, food, and help names must contain at least 2 characters when creating or updating a post
- Users can update their own skill, food, and help posts
- Users can delete their own skill, food, and help posts if no request history is linked to them
- Food listings and details show the quantity available for new requests after pending requests are reserved, separately from the quantity currently on the post. Requesters choose an amount, and accepting a food request subtracts it from the post. The post closes automatically when its quantity reaches zero.
- Users can send requests and accept/reject them
- Accepting a SkillSwap or LocalHelper request makes its post unavailable and rejects other pending requests for that post
- Users cannot send another request for a SkillSwap or LocalHelper post while an earlier request is pending or accepted
- FoodShare requesters can send multiple requests for the same post, but pending request quantities reserve food so total pending requests cannot exceed the remaining quantity; accepting requests deducts their quantity, and pending requests are rejected when the post runs out
- Mobile numbers are hidden in request lists and Connections until accepted, unless the number owner has hidden it from the viewer
- Users can remove a connection; this hides the removing user's mobile number from the other person in request lists and Connections while keeping request history
- Users can edit profile and change password
- Admin can manage users, posts, requests and see reports

## How to run
1. Start MySQL and execute `schema.sql` in MySQL Workbench. This script drops and recreates `sharesphere`, so it deletes any existing data in that database.

2. Set the MySQL connection settings in your terminal. In PowerShell:
   ```powershell
   $env:MYSQL_USER = "root"
   $env:MYSQL_PASSWORD = "your_mysql_password"
   $env:MYSQL_DATABASE = "sharesphere"
   ```

3. Install the dependency (PyMySQL):
   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:
   ```bash
   python main.py
   ```

### Existing database migration for FoodShare quantities

For an existing database, back it up and make sure every `food_items.quantity`
value contains only a whole number before running these statements. Do not run
`schema.sql` to migrate an existing database; that script drops and recreates
the database.

```sql
ALTER TABLE food_items MODIFY quantity INT NOT NULL;
ALTER TABLE requests ADD COLUMN quantity INT NULL;
```

Older pending food requests have no requested amount recorded. If accepted
after migration, they consume all of that post's remaining quantity, matching
the previous all-or-nothing behavior.

### Existing database migration for removed connections

For an existing database, create the table used to hide a user's mobile number
from a removed connection:

```sql
CREATE TABLE removed_connections (
    user_id INT NOT NULL,
    other_user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, other_user_id),
    CONSTRAINT fk_removed_connection_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_removed_connection_other
        FOREIGN KEY (other_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_removed_connection_users_differ
        CHECK (user_id <> other_user_id)
);
```

## Admin login
username: admin
password: admin123

## Files
- `main.py` - application entry point and main menus
- `db.py` - MySQL connection settings
- `schema.sql` - database and table definitions
- `modules/helper.py` - shared input and terminal helpers
- `modules/auth.py` - registration and login
- `modules/skillswap.py`, `modules/foodshare.py`, `modules/localhelper.py` - service features
- `modules/myrequests.py` - sent and received requests
- `modules/connections.py` - accepted and pending connections
- `modules/profile.py` - profile and password changes
- `modules/admin.py` - administration and reports

## Security
- Passwords are currently stored as plain text, as configured for this project version. This is unsafe for a real deployment.
- All database queries use parameterized placeholders (%s), so user input can't break out of the query and run extra SQL.
- Mobile numbers stay hidden in Connections until a request is accepted.

## Known limitations
- A user with existing posts or requests cannot be deleted.
