import sqlite3
from datetime import datetime

def create_tables(database_file):
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
            priority INT, 
            project_id INT NOT NULL, 
            status INT NOT NULL, 
            begin_date DATE NOT NULL, 
            end_date DATE NOT NULL, 
            reward INTEGER NOT NULL,
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


def check_tables(cursor, table:str):
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
    # Check if it has entries
    if check_tables(cursor=cursor, table=table_name):
        last_id = get_latest_value(cursor=cursor, table_name=table_name, column_name="id")
        new_id = last_id + 1
    else:
        new_id = 1 # in case there are no entries yet

    return new_id

def add_project(cursor, conn, project_name, project_begin="NULL", project_end="NULL", status=0):
    
    # Determine today's date
    today = datetime.today()
    project_begin = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    
    # Determine new id number
    new_id = determine_id(cursor=cursor, table_name="projects")

    # Execute statement
    cursor.execute("""
        INSERT INTO projects(id, name, begin_date, end_date, status) VALUES(?, ?, ?, ?, ?)
        """, (new_id, project_name, project_begin, project_end, status))
    # Commit changes
    conn.commit()
    # Print message
    print(f"Project '{project_name}' has been created!")
            


def add_user(cursor, conn):
    
    # Initialize values
    user_name = ""
    coins = 0
    # Create a cursor
    cursor = conn.cursor()
    # Get user input
    while user_name == "":
        user_name = input("What is your name?: ")

    # Determine next id number
    new_id = determine_id(cursor=cursor, table_name="user")
    
    # Execute statement
    cursor.execute("""
        INSERT INTO user(id, name, coins) VALUES(?, ?, ?)
        """, (new_id, user_name, 0))
    print("User has been added!")

    # Commit changes
    conn.commit()

    
def add_task(cursor, conn):
    
    # Initialize values
    task_name = ""
    today = datetime.today()
    begin_date = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    status = 0

    # Get user input
    while task_name == "":
        task_name = input("Task Description: ")

    # Priority level
    priority = input("(Optional) Enter priority [0 (No priority), 1 (low priority), 2 (high priority)]: ")
    if priority == "":
        priority = 0
    else:
        priority = int(priority)

    # Project_id
    # Show projects
    list_entries(cursor=cursor, table="projects")
    print("\n")
    # Ask for project id
    project_id = input("(Optional) Give project ID: ")
    if project_id == "":
        project_id = 1
    else:
        project_id = int(project_id)

    # Due date
    while True:
        raw_end_date = input("(Optional) When would you like to finish this task? [YYYY-MM-DD]: ")
        # Validate format and actual calendar date
        try:
            end_date = datetime.strptime(raw_end_date, "%Y-%m-%d")  # checks format + validity
            end_date = raw_end_date # use raw_end_date if validated
            break
        except ValueError:
            print("Please enter a valid date in the form YYYY-MM-DD (e.g. 2025-12-31), or leave blank.")

    # Reward
    reward = input("(Optional) How rewarding will this task be? [0] Not much [1] Quite rewarding [2] Very rewarding!: ")
    if reward == "":
        reward = 0
    else:
        reward = int(reward)

    # Determine next id number
    new_id = determine_id(cursor=cursor, table_name="tasks")
    
    # Execute statement
    cursor.execute("""
        INSERT INTO tasks(id, name, priority, project_id, status, begin_date, end_date, reward) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, task_name, priority, project_id, status, begin_date, end_date, reward))
    print("Task has been added!")

    # Commit changes
    conn.commit()


def list_entries(cursor, table, condition:str="NULL", get_entries:bool=False):
    
    # Execute statement
    table_info = f"""PRAGMA table_info({table});""" # a query for showing table column names
    if condition != "NULL":
        query = f"SELECT * FROM {table} WHERE {condition};"
    else:
        query = f"""SELECT * FROM {table};"""
    cursor.execute(table_info)
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    total_rows = len(results)
    # Print results
    if total_rows != 0:
        for result in results:
            print(result)
    else:
        print(f"No entries yet in table: {table}")
        
    # If data is desired return the results
    if get_entries:
        return results
    # Otherwise just give the number.
    return total_rows

    

def get_entry(cursor, table, id_num=None, col=None):
    # Cast id number to integer
    id_num = int(id_num)
        
    # Define query
    if col is None: # When no specific column has been specified
        query = f"""SELECT * FROM {table} WHERE id = {id_num}"""
    else:
        query = f"""SELECT {col} FROM {table} WHERE id = {id_num}"""
    # Execute statement
    cursor.execute(query)
    # Fetch results
    result = cursor.fetchone()
    return result
    
    
def edit_entry(cursor, table):
    # List entries
    list_entries(cursor=cursor, table=table)
    # Ask user input
    while True:
        id_num = input("Select the ID of the entry that you want to change: ")
        try:
            id_num = int(id_num)
            break
        except ValueError:
            print("Make sure to give a valid integer number!")
        
    field = input("Which field do you want to edit?: ")
    new_value = input("What is the new value?: ")
    
    # Define query
    query = f"""UPDATE {table} SET {field}={new_value} WHERE id={id_num}"""
    
    # Execute statement
    cursor.execute(query)
            
        
def finish_task(cursor, conn, id_num):
    # Define query
    query = f"""UPDATE tasks SET status = 2 WHERE id = {id_num}"""
    cursor.execute(query)
    # Commit changes
    conn.commit()
    print("Task has been marked as finished! Well done.")
        
def show_inbox(cursor):
    # Define query
    query = """SELECT * FROM tasks WHERE project_id = 1"""
   
    # Execute statement
    cursor.execute(query)

        
def show_today(cursor):
    # Get today's date
    today = datetime.today()
    today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    
    # Define query
    query = f"""SELECT * FROM tasks WHERE end_date = {today}"""
    
    # Execute statement
    cursor.execute(query)
            
    