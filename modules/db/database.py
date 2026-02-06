"""
Database initialization and low-level helper functions.
"""
import sqlite3


def create_tables(database_file):
    """
    Initializes the database schema by creating necessary tables if they do not exist.
    
    Args:
        database_file (str): The path to the SQLite database file.
    """
    sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY, 
            name text NOT NULL, 
            begin_date DATE, 
            end_date DATE,
            status INTEGER
        );""",

    """CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY, 
            name TEXT NOT NULL, 
            priority INTEGER, 
            project_id INT NOT NULL, 
            status INTEGER NOT NULL, 
            begin_date DATE NOT NULL, 
            end_date DATE NOT NULL, 
            reward INTEGER NOT NULL,
            duration INTEGER, 
            time_spent INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );""",
    """CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY, 
            name TEXT NOT NULL, 
            coins INTEGER NOT NULL
        );""",
    """CREATE TABLE IF NOT EXISTS shop (
            id INTEGER PRIMARY KEY, 
            reward TEXT NOT NULL, 
            cost INT NOT NULL
        );""",
    """CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL, 
            task_id INT NOT NULL, 
            status INTEGER NOT NULL, 
            end_date DATE NOT NULL, 
            duration INTEGER,
            time_spent INTEGER,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        );"""
    ]

    # create a database connection
    try:
        with sqlite3.connect(database_file) as conn:
            # create a cursor
            cursor = conn.cursor()

            # execute statements
            for statement in sql_statements:
                cursor.execute(statement)

            # commit the changes
            conn.commit()

            print("Tables created successfully.")
    except sqlite3.OperationalError as e:
        print("Failed to create tables:", e)


def check_tables(cursor, table: str):
    """
    Checks if a specific table contains any data.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): The name of the table to check.
        
    Returns:
        bool: True if the table has data, False otherwise.
    """
    try:
        cursor.execute(f"""
            SELECT EXISTS(SELECT * FROM {table})
        """)
        result = cursor.fetchone()[0]
        if result == 0:
            print(f"No data yet in table: {table}")
    except sqlite3.OperationalError as e:
        print("Database/table seems empty...", e)
        result = 0

    return bool(result)


def get_latest_value(cursor, table_name, column_name):
    """
    Retrieves the most recent value from a specific column based on the ID.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table_name (str): Name of the table.
        column_name (str): Name of the column.
        
    Returns:
        Any: The value found in the latest row.
    """
    # Get last value in specific column
    cursor.execute(f"""
        SELECT {column_name} 
        FROM {table_name} 
        ORDER BY id DESC 
        LIMIT 1
    """)
    last_value = cursor.fetchone()[0] # Get latest id
    return last_value


def determine_id(cursor, table_name):
    """
    Calculates the next available ID for a new entry in a table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table_name (str): Name of the table.
        
    Returns:
        int: The next ID number.
    """
    # Check if it has entries
    if check_tables(cursor=cursor, table=table_name):
        last_id = get_latest_value(cursor=cursor, table_name=table_name, column_name="id")
        new_id = last_id + 1
    else:
        new_id = 1 # in case there are no entries yet

    return new_id
