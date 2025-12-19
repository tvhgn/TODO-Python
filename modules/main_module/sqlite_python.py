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
            status_id INT NOT NULL, 
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


def check_tables(database_file, table:str):
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
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

def get_latest_value(database_file, table_name, column_name):
    try:
        with sqlite3.connect(database_file) as conn:
            # Create cursor
            cursor = conn.cursor()

            # Get last value in specific column
            cursor.execute(f"""
                SELECT {column_name} 
                FROM {table_name} 
                ORDER BY id DESC 
                LIMIT 1
            """)
            last_value = cursor.fetchone()[0] # Get latest id
            return last_value

    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)

def determine_id(database_file, table_name):
    # Check if it has entries
    if check_tables(database_file, table=table_name):
        last_id = get_latest_value(database_file, table_name=table_name, column_name="id")
        new_id = last_id + 1
    else:
        new_id = 1 # in case there are no entries yet

    return new_id

def add_project(database_file, project_name, project_begin="NULL", project_end="NULL", status=0):
    try:
        with sqlite3.connect(database_file) as conn:
            # Create a cursor
            cursor = conn.cursor()
            ## Get input from user that can be passed on to the database
            # project_name = input("What is the project name?: ")
            # project_end = input("When do you expect to finish this project [YYYY-MM-DD]? (Optional): ")
            today = datetime.today()
            project_begin = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
            
            # Determine new id number
            new_id = determine_id(database_file, "projects")

            # Execute statement
            cursor.execute("""
                INSERT INTO projects(id, name, begin_date, end_date, status) VALUES(?, ?, ?, ?, ?)
                """, (new_id, project_name, project_begin, project_end, status))
            # Commit changes
            conn.commit()
            # Print message
            print("Project '{project_name}' has been created!")
            

    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)


def add_user(database_file):
    try:
        with sqlite3.connect(database_file) as conn:
            # Initialize values
            user_name = ""
            coins = 0
            # Create a cursor
            cursor = conn.cursor()
            # Get user input
            while user_name == "":
                user_name = input("What is your name?: ")

            # Determine next id number
            new_id = determine_id(database_file, "user")
            
            # Execute statement
            cursor.execute("""
                INSERT INTO user(id, name, coins) VALUES(?, ?, ?)
                """, (new_id, user_name, 0))
            print("User has been added!")

            # Commit changes
            conn.commit()

    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)

def add_task(database_file):
    try:
        with sqlite3.connect(database_file) as conn:
            # Initialize values
            task_name = ""
            today = datetime.today()
            begin_date = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
            status = 0

            # Create a cursor
            cursor = conn.cursor()
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
            list_entries(database_file, "projects")
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
            new_id = determine_id(database_file, table_name="tasks")
            
            # Execute statement
            cursor.execute("""
                INSERT INTO tasks(id, name, priority, project_id, status_id, begin_date, end_date, reward) 
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_id, task_name, priority, project_id, status, begin_date, end_date, reward))
            print("Task has been added!")

            # Commit changes
            conn.commit()

    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)


def list_entries(database_file, table, get_entries:bool=False):
    try:
        with sqlite3.connect(database_file) as conn:
            # Create cursor
            cursor =  conn.cursor()
            # Execute statement
            query = f"""SELECT * FROM {table}"""
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

    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)

def get_entry(database_file, table, id=None, col=None):
    # Cast id number to integer
    id = int(id)
    try:
        with sqlite3.connect(database_file) as conn:
            # Create cursor
            cursor = conn.cursor()
            # Define query
            if col == None: # When no specific column has been specified
                query = f"""SELECT * FROM {table} WHERE id = {id}"""
            else:
                query = f"""SELECT {col} FROM {table} WHERE id = {id}"""
            # Execute statement
            cursor.execute(query)
            # Fetch results
            result = cursor.fetchone()
            return result
    except sqlite3.OperationalError as e:
        print("Something went wrong!", e)
            
