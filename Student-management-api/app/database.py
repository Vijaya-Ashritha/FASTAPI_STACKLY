import sqlite3


DATABASE = "students.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY UNIQUE,
            student_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            age INTEGER NOT NULL,
            course TEXT NOT NULL,
            address TEXT
        )
        """
    )

    connection.commit()
    connection.close()