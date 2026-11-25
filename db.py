"""MySQL connection settings for ShareSphere."""

import os

import pymysql


def connect_db():
    """Connect to the ShareSphere database using environment settings."""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database=os.getenv("MYSQL_DATABASE", "sharesphere"),
        charset="utf8mb4",
    )
