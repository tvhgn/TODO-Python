import sqlite3
import os

from sqlite_python import *
from gui import *
from helpers.settings import generate_settings_file

# initial values
DB_FILE = os.path.join("data", "database", "todos.db")

# Create database folder if not there yet
if not os.path.exists(os.path.dirname(DB_FILE)):
    os.mkdir(os.path.dirname(DB_FILE))
# Create or open database to make sure the file exists
try:
    with sqlite3.connect(DB_FILE) as conn:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
        # Create cursor
        cursor = conn.cursor()
        # Create Tables if database does not have any. First check, then create.
        # Check for tables
        table_check = check_tables(cursor, "user")

except sqlite3.OperationalError as e:
    print("Failed to open database:", e)

# If not there, create tables, and start initial setup
if not table_check:
    print("\nCreating new tables...")
    create_tables(DB_FILE)
    with sqlite3.connect(DB_FILE) as conn:
        # Create cursor
        cursor = conn.cursor()
        # Start setup: Create user, create unfiled project.
        add_user(cursor=cursor, conn=conn)
        add_project(cursor=cursor, conn=conn, initialize=True)
        # Generate settings file
        generate_settings_file()

# Show menu
with sqlite3.connect(DB_FILE) as conn:
    # Open GUI
    show_menu(conn)


