import sqlite3


DATABASE_NAME = "expenses.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY,
            employee_name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
        """
    )

    connection.commit()
    connection.close()