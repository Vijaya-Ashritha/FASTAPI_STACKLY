
import sqlite3

database_name = "employee.db"

def get_connection():
    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()

