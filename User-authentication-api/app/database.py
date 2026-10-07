import sqlite3


DATABASE_NAME = "users.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_date TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()