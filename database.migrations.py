import sqlite3

# Create user table
from constants import database_name

user_table = """
CREATE TABLE IF NOT EXISTS users (
   user_id INTEGER PRIMARY KEY AUTOINCREMENT,
   first_name text NOT NULL,
   last_name text NOT NULL,
   email text NOT NULL UNIQUE,
   password text NOT NULL
);
"""

token_table = """
CREATE TABLE IF NOT EXISTS tokens (
    token_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL UNIQUE,
    token text NOT NULL
)
"""

unique_email = """
CREATE UNIQUE INDEX users_email_uindex ON users (email);
"""

with sqlite3.connect(database_name) as conn:
    cursor = conn.cursor()
    cursor.execute(user_table)
    cursor.execute(token_table)
    conn.commit()
