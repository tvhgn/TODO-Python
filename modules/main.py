import sqlite3
import os
import logging

from db.database import *
from db.users import *
from db.projects import *
from gui import *
from helpers.settings import generate_settings_file

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":

    # initial values
    DB_FILE = os.path.join("data", "database", "todos.db")

    logging.info("Application started.") # Log application start

    # Create database folder if not there yet
    if not os.path.exists(os.path.dirname(DB_FILE)):
        os.mkdir(os.path.dirname(DB_FILE))

    # Create or open database to make sure the file exists
    try:
        with sqlite3.connect(DB_FILE) as conn:
            logging.info(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.") # Log database opened
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            # Create cursor
            cursor = conn.cursor()
            # Create Tables if database does not have any. First check, then create.
            # Check for tables
            table_check = check_tables(cursor, "user")

    except sqlite3.OperationalError as e:
        logging.error(f"Failed to open database: {e}") # Log database error
        print("Failed to open database:", e)
        # Exit if database cannot be opened
        exit()

    # If not there, create tables, and start initial setup
    if not table_check:
        logging.info("Database tables not found. Creating new tables...") # Log table creation process start
        print("\nCreating new tables...")
        create_tables(DB_FILE)
        with sqlite3.connect(DB_FILE) as conn:
            # Create cursor
            cursor = conn.cursor()
            # Create Tables if database does not have any. First check, then create.
            # Check for tables
            try:
                # Re-check if tables were created successfully
                table_check = check_tables(cursor, "user")
                if table_check: # only proceed if tables were actually created
                    logging.info("Database tables created successfully.") # Log table creation success
                    # Start setup: Create user, create unfiled project.
                    add_user(cursor=cursor, conn=conn)
                    logging.info("Initial user added.") # Log user addition
                    add_project(cursor=cursor, conn=conn, initialize=True)
                    logging.info("Initial project added.") # Log project addition
                    # Generate settings file
                    generate_settings_file()
                    logging.info("Settings file generated.") # Log settings file generation
                else:
                    logging.error("Failed to create database tables.") # Log table creation failure
                    print("Error: Failed to create database tables.")
                    exit()
            except Exception as e:
                logging.error(f"An error occurred during initial setup after table creation: {e}")
                print(f"An error occurred during initial setup: {e}")
                exit()

    # Start DB connection and application
    try:
        with sqlite3.connect(DB_FILE) as conn:
            logging.info("Application CLI is starting.") # Log GUI start
            # Open GUI
            show_menu(conn)
    except Exception as e:
        logging.error(f"An error occurred when starting the CLI: {e}")
        print(f"An error occurred when starting the CLI: {e}")

    logging.info("Application finished.") # Log application exit
