"""
create_admin.py - creates (or resets the password of) an admin account.

Usage:
    python create_admin.py                      (asks for username and password)
    python create_admin.py admin MyPassword123  (no questions)

The password is saved as a hash, so nobody can read it from the database.
"""
import getpass
import sqlite3
import sys

from werkzeug.security import generate_password_hash

import config
import db


def main():
    db.create_tables()  # make sure tables exist

    if len(sys.argv) == 3:
        username, password = sys.argv[1], sys.argv[2]
    else:
        username = input("Admin username: ").strip()
        password = getpass.getpass("Admin password (min 8 characters): ")

    if not username or len(password) < 8:
        print("Username is required and password must be at least 8 characters.")
        sys.exit(1)

    conn = sqlite3.connect(config.DB_PATH)
    hashed = generate_password_hash(password)
    exists = conn.execute("SELECT id FROM admins WHERE username = ?", (username,)).fetchone()
    if exists:
        conn.execute("UPDATE admins SET password_hash = ? WHERE username = ?", (hashed, username))
        print(f"Password updated for admin '{username}'.")
    else:
        conn.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", (username, hashed))
        print(f"Admin '{username}' created.")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
