drop database if  exists sharesphere;

CREATE DATABASE IF NOT EXISTS sharesphere;
USE sharesphere;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Demo admin login: admin / admin123
INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    skill_name VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE food_items (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    food_name VARCHAR(100),
    quantity INT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE help_items (
    help_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    help_type VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    service_type VARCHAR(20) NOT NULL,
    skill_id INT NULL,
    food_id INT NULL,
    help_id INT NULL,
    quantity INT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_request_sender
        FOREIGN KEY (sender_id) REFERENCES users(user_id),
    CONSTRAINT fk_request_receiver
        FOREIGN KEY (receiver_id) REFERENCES users(user_id),
    CONSTRAINT fk_request_skill
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE RESTRICT,
    CONSTRAINT fk_request_food
        FOREIGN KEY (food_id) REFERENCES food_items(food_id) ON DELETE RESTRICT,
    CONSTRAINT fk_request_help
        FOREIGN KEY (help_id) REFERENCES help_items(help_id) ON DELETE RESTRICT,
    CONSTRAINT chk_request_item_matches_service CHECK (
        (service_type = 'SkillSwap' AND skill_id IS NOT NULL
            AND food_id IS NULL AND help_id IS NULL)
        OR (service_type = 'FoodShare' AND food_id IS NOT NULL
            AND skill_id IS NULL AND help_id IS NULL)
        OR (service_type = 'LocalHelper' AND help_id IS NOT NULL
            AND skill_id IS NULL AND food_id IS NULL)
    ),
    CONSTRAINT chk_request_users_differ CHECK (sender_id <> receiver_id)
);

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

