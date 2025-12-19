import sqlite3
import os

from sqlite_python import *

# initial values
DB_FILE = os.path.join("database", "todos.db")

# Create database folder if not there yet
if not os.path.exists(os.path.dirname(DB_FILE)):
    os.mkdir(os.path.dirname(DB_FILE))
# Create or open database to make sure the file exists
try:
    with sqlite3.connect(DB_FILE) as conn:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

except sqlite3.OperationalError as e:
    print("Failed to open database:", e)

# Create Tables if database does not have any. First check, then create.
# Check for tables
table_check = check_tables(DB_FILE, "user")

# If not there, create tables, and start initial setup
if not table_check:
    print("\nCreating new tables...")
    create_tables(DB_FILE)
    # Start setup: Create user, create unfiled project.
    add_user(DB_FILE)
    add_project(DB_FILE, project_name="Unfiled", status="NULL")

# Show menu


