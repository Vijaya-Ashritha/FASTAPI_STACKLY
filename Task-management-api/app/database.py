import sqlite3


DATABASE_NAME = "tasks.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY,
            task_title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            due_date TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            created_date TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()