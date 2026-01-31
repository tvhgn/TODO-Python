import sqlite3
import os
from datetime import datetime, timedelta

from prettytable import PrettyTable
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator
from playsound3 import playsound

from helpers.effects import strike
from helpers.settings import generate_settings_file, read_settings_file
from timers import Timer, TimerWindow

# Global variable declaration
timer_list = []

# ==========================================
# DATABASE INITIALIZATION & LOW-LEVEL HELPERS
# ==========================================

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


# ==========================================
# ENTITY MANAGEMENT (CRUD OPERATIONS)
# ==========================================

def add_project(cursor, conn, initialize=False):
    """
    Adds a new project to the database via user input or initialization.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        initialize (bool): If True, creates a default "Unfiled" project.
    """
    if initialize:
        project_name = "Unfiled"
        project_end = "NULL"
        status = "NULL"
        project_begin = "NULL"
    else:
        # Get input from user
        project_name = inquirer.text(message="Enter project description: ").execute()
        project_end = inquirer.text(message="(Optional) When would you like to finish this project? [YYYY-MM-DD]: ").execute()
        # Check if default value is needed
        if project_end == "":
            project_end = "NULL"
            
        status = inquirer.text(
            message="(Optional) What is the project's current status? [0; default] Not started [1] In progress [2] Finished: ",
            default="0",
            validate=NumberValidator()
            ).execute()
       # Safely convert to int with fallback
        try:
            status = int(status)
        except ValueError:
            status = 0  # Default on invalid input

        # Clamp to valid range
        if status > 2 or status < 0:
            status = 0
        
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
    """
    Prompts for a name and adds a new user to the database.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
    """
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
    """
    Prompts for task details and saves a new task to the database.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
    """
    # Initialize values
    task_name = ""
    today = datetime.today()
    begin_date = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    status = 0 # default status value
    
    # Get settings file
    settings = read_settings_file()
    # Get reward mapping
    reward_map = settings['reward_mapping']

    # Get user input
    while task_name == "":
        task_name = inquirer.text(message="Enter Task Description: ").execute()

    # Priority level
    priority = inquirer.text(message="(Optional) Enter priority [0 (No priority), 1 (low priority), 2 (high priority)]: ").execute()
    if priority == "":
        priority = 0
    else:
        priority = int(priority)

    # Project_id
    # Show projects
    print("\nListing projects...")
    list_entries(cursor=cursor, table="projects")
    # Ask for project id
    project_id = inquirer.text(message="(Optional) Give project ID: ").execute()
    if project_id == "":
        project_id = 1 # Unfiled ID
    else:
        project_id = int(project_id)

    # Due date
    while True:
        raw_end_date = inquirer.text(message="(Optional) When would you like to finish this task? [YYYY-MM-DD]: ").execute()
        # Validate format and actual calendar date
        try:
            end_date = datetime.strptime(raw_end_date, "%Y-%m-%d")  # checks format + validity
            end_date = raw_end_date # use raw_end_date if validated
            break
        except ValueError:
            print("Please enter a valid date in the form YYYY-MM-DD (e.g. 2025-12-31), or leave blank.")

    # Reward
    reward = inquirer.text(message="(Optional) How rewarding will this task be? [0] Not much [1] Quite rewarding [2] Very rewarding!: ").execute()
    if reward == "":
        reward = 0
        
    # Transform to actual value
    reward = reward_map[reward]
    
    # Duration
    duration = inquirer.text(message="(Optional) How many minutes do you estimate this task will take?: ").execute()

    # Determine next id number
    new_id = determine_id(cursor=cursor, table_name="tasks")
    
    # Execute statement
    cursor.execute("""
        INSERT INTO tasks(id, name, priority, project_id, status, begin_date, end_date, reward, duration) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (new_id, task_name, priority, project_id, status, begin_date, end_date, reward, duration))
    print("Task has been added!")

    # Commit changes
    conn.commit()


def add_subtask(cursor, conn, task_id):
    """
    Adds one or more subtasks linked to a specific parent task.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        task_id (int): The ID of the parent task.
    """
    while True:
        # More initializations
        task_name = ""
        status = 0 # default status value
        
        # Get user input
        while task_name == "":
            task_name = inquirer.text(message="Enter Task Description: ").execute()

        # Priority level
        priority = inquirer.text(message="(Optional) Enter priority [0 (No priority), 1 (low priority), 2 (high priority)]: ").execute()
        if priority == "":
            priority = 0
        else:
            priority = int(priority)
        
        # Due date
        while True:
            raw_end_date = inquirer.text(message="(Optional) When would you like to finish this task? [YYYY-MM-DD]: ").execute()
            # Validate format and actual calendar date
            try:
                end_date = datetime.strptime(raw_end_date, "%Y-%m-%d")  # checks format + validity
                end_date = raw_end_date # use raw_end_date if validated
                break
            except ValueError:
                print("Please enter a valid date in the form YYYY-MM-DD (e.g. 2025-12-31), or leave blank.")
        
        # Duration
        duration = inquirer.text(message="(Optional) How many minutes do you estimate this task will take?: ").execute()

        # Determine next id number
        new_id = determine_id(cursor=cursor, table_name="subtasks")
        
        # Execute statement
        cursor.execute("""
            INSERT INTO subtasks(id, name, task_id, status, end_date, duration) 
            VALUES(?, ?, ?, ?, ?, ?);
            """, (new_id, task_name, task_id, status, end_date, duration))
        print("Subtask has been added!")

        # Commit changes
        conn.commit()
        
        # Ask user if they want to add another subtask
        add_another = inquirer.confirm(message="Would you like to add another subtask? ").execute()
        # Break loop if not
        if not add_another:
            break


# ==========================================
# DATA RETRIEVAL & DISPLAY
# ==========================================

def check_subtasks(cursor, task_id):
    """
    Checks if a task has any associated subtasks.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        task_id (int): The task ID to check.
        
    Returns:
        bool: True if subtasks exist, False otherwise.
    """
    # Get subtasks corresponding to task_id
    query = f"""SELECT * FROM subtasks WHERE task_id = {task_id}"""
    cursor.execute(query)
    results = cursor.fetchall() # Get the results and store
    # Check whether there are any subtasks related to task_id and return True if so
    return len(results) > 0


def list_entries(cursor, table, condition: str = "NULL", get_entries: bool = False, print_table: bool = True):
    """
    Lists and optionally returns entries from a database table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        condition (str): SQL WHERE clause condition.
        get_entries (bool): Whether to return the results.
        print_table (bool): Whether to print the table to console.
        
    Returns:
        int or tuple: Row count or (PrettyTable, results) depending on get_entries.
    """
    # Define query depending on condition presence
    if condition != "NULL":
        query = f"SELECT * FROM {table} WHERE {condition};"
    else:
        query = f"""SELECT * FROM {table};"""
    # Execute query
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    total_rows = len(results)
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Using prettytables
    table_obj = PrettyTable()
    table_obj.field_names = headers
    table_obj.add_rows(results)
    
    if print_table:
        print(table_obj)
        
    # If data is desired return the results
    if get_entries:
        return (table_obj, results)
    # Otherwise just give the number.
    return total_rows


def display_and_select(cursor, table, condition: str = "NULL", alt_query: str = None):    
    """
    Displays records in a formatted list and allows user to select them via checkboxes.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        condition (str): Optional filter.
        alt_query (str): Optional full SQL query to override default behavior.
        
    Returns:
        list: Selected IDs or None if no entries exist.
    """
    if alt_query is None:
        # Define query depending on condition presence
        if condition != "NULL":
            query = f"SELECT * FROM {table} WHERE {condition};"
        else:
            query = f"""SELECT * FROM {table};"""
    else:
        query = alt_query
    # Execute query
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Format entries for inquirer
    # First create dictionary
    results_dict_list = [dict(zip(headers, result)) for result in results] # Get structure like {a: 1, b:2, c:3} with letters being columns

    # Compute column widths (consider header and all values)
    col_widths = {}
    columns = zip(headers, *results)
    max_col_lengths = [max(list(map(lambda x:len(str(x)), column))) for column in columns]
    col_widths = dict(zip(headers, max_col_lengths))
    
    # Create headers and adjust for column width
    sep = "  |  "
    header_description = sep.join(h.ljust(col_widths[h]) for h in headers)
    header_description = "    " + header_description
    
    # Create options using Choice object while adjusting column widths
    choices = []
    for row in results_dict_list:
        # Create name string
        choice_description = sep.join(str(row[h]).ljust(col_widths[h]) for h in headers)
        if "status" in headers:
            # If task is finished, strikethrough
            if row['status'] == 2: 
                choice_description = strike(choice_description)
            
        # Build Choice object
        choice = Choice(value=row['id'],
                        name = choice_description,
                        enabled=False)
        # Append to choices
        choices.append(choice)
        
    # Use choices to create checkbox selection menu   
    print(header_description)  # print headers
    if len(choices) != 0:
        checks = inquirer.checkbox(
            message="Select (at least) one:",
            choices=choices,
            mandatory=False
            ).execute()
    else:
        print("No entries available!")
        checks = None
    
    return checks


def get_entry(cursor, table, id_num=None, col=None):
    """
    Fetches a specific row or column value from a table by ID.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        id_num (int/str): The ID of the record.
        col (str): Specific column name to fetch.
        
    Returns:
        tuple or Any: The fetched row or value.
    """
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


def get_today(cursor):
    """
    Retrieves and formats a string of tasks due today or overdue.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        
    Returns:
        str: Formatted text for display.
    """
    # Get today's date as well as tomorrow's
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    tomorrow = tomorrow.strftime('%Y-%m-%d')
    # Define condition
    condition = f"(end_date = {today}) OR (end_date < '{tomorrow}' AND NOT status = 2)" # Get today's tasks, as well as unfinished tasks from before
    # Fetch entries and guide through submenus
    query = f"""SELECT * FROM tasks WHERE {condition}"""
    
    # Execute statement
    cursor.execute(query)
    
    # Fetch results
    results = cursor.fetchall()
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Format entries for inquirer
    # First create dictionary
    results_dict_list = [dict(zip(headers, result)) for result in results] # Get structure like {a: 1, b:2, c:3} with letters being columns

    # Compute column widths (consider header and all values)
    col_widths = {}
    columns = zip(headers, *results)
    max_col_lengths = [max(list(map(lambda x:len(str(x)), column))) for column in columns]
    col_widths = dict(zip(headers, max_col_lengths))
    
    # Create headers and adjust for column width
    sep = "  |  "
    header_description = sep.join(h.ljust(col_widths[h]) for h in headers)
    header_description = "    " + header_description
    
    # Go through each entry and convert to string
    entries = []
    for row in results_dict_list:
        # Create name string
        choice_description = sep.join(str(row[h]).ljust(col_widths[h]) for h in headers)
        # Append to entries
        entries.append(choice_description)
    
    # Build output string
    output_text = header_description + "\n" + "\n".join(entries)
    
    return output_text


def show_inbox(cursor):
    """
    Executes a query to show tasks in the default project (Inbox).
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
    """
    # Define query
    query = """SELECT * FROM tasks WHERE project_id = 1"""
   
    # Execute statement
    cursor.execute(query)


# ==========================================
# INTERACTION & CONTEXT MENUS
# ==========================================

def context_menu(cursor, conn, checks, table):
    """
    Displays a context-specific menu based on the selected items and table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        checks (list): List of selected IDs.
        table (str): The table the IDs belong to.
    """
    if table == "tasks":
        # INitialize
        has_subtasks = False
        # If one task selected, check for subtasks. Try except statement to get around situation where checks == None
        try:
            if len(checks) == 1:
                has_subtasks = check_subtasks(cursor=cursor, task_id=checks[0])
        except TypeError:
            pass
            
        # Submenu
        if has_subtasks:
            choices = [Choice(value=str(i), name=opt) for i, opt in 
                       enumerate(["Mark as completed", "Show Subtasks", "Add Subtask(s)" ,"Delete", "Edit", "Timer", "Return"])]
        else:
            choices = [Choice(value=str(i), name=opt) for i, opt in 
                       enumerate(["Mark as completed", "Add Subtask(s)" ,"Delete", "Edit", "Timer", "Return"])]
        choices.insert(0, Separator()) # add separator
        if checks is not None:
            submenu_select = inquirer.select(
                    message="",
                    choices=choices,
                ).execute()
        else:
            submenu_select = False
        
        # Check input and continue

        if submenu_select:
            if has_subtasks:
                match str(submenu_select):
                    case "0": # Mark as completed
                        for check in checks:
                            finish_entry(cursor=cursor, table=table, conn=conn, id_num=check)
                    case "1": # Show subtasks
                        show_subtasks(cursor=cursor, conn=conn, task_id=checks[0])
                    case "2": # add subtasks
                        add_subtask(cursor=cursor, conn=conn, task_id=checks[0])
                    case "3": # Delete
                        for check in checks:
                            delete_entry(cursor=cursor, conn=conn, table=table, id_num=check)
                    case "4": # Edit
                        edit_entry(cursor=cursor, conn=conn, table=table, id_list=checks)   
                    case "5": # Timer
                        # Popup timer
                        popup_timer(cursor=cursor, conn=conn, checks=checks)
                        #timer_context_menu(cursor=cursor, conn=conn, checks=checks)
                        
                    case "6": # Return
                        pass
            else:
                match str(submenu_select):
                    case "0": # Mark as completed
                        for check in checks:
                            finish_entry(cursor=cursor, table=table, conn=conn, id_num=check)
                    case "1": # add subtasks
                        for check in checks:
                            add_subtask(cursor=cursor, conn=conn, task_id=check)
                    case "2": # Delete
                        for check in checks:
                            delete_entry(cursor=cursor, conn=conn, table=table, id_num=check)
                    case "3": # Edit
                        edit_entry(cursor=cursor, conn=conn, table=table, id_list=checks)
                    case "4": # Timer
                        # Popup timer
                        popup_timer(cursor=cursor, conn=conn, checks=checks)
                        #timer_context_menu(cursor=cursor, conn=conn, checks=checks)
                    case "5": # Return
                        pass
    
    elif table == "subtasks":
        choices = [Choice(value=str(i), name=opt) for i, opt in 
                       enumerate(["Mark as completed", "Delete", "Edit", "Return"])]
        choices.insert(0, Separator()) # add separator
        if checks is not None:
            submenu_select = inquirer.select(
                    message="",
                    choices=choices,
                ).execute()
        else:
            submenu_select = False
        
        # If selection has been made
        if submenu_select:
            match str(submenu_select):
                case "0": # mark as completed
                    for check in checks:
                        finish_entry(cursor=cursor, table=table, conn=conn, id_num=check)
                case "1": # Delete
                        for check in checks:
                            delete_entry(cursor=cursor, conn=conn, table=table, id_num=check)
                case "2": # Edit
                    edit_entry(cursor=cursor, conn=conn, table=table, id_list=checks)   
                case "3": # Return
                    pass    
    
    elif table == "projects":
        # Submenu
        choices = [Choice(value=str(i), name=opt) for i, opt in enumerate(["Show Related Tasks", "Mark as completed", "Delete", "Edit", "Return"])]
        choices.insert(0, Separator()) # add separator
        if checks is not None:
            submenu_select = inquirer.select(
                    message="",
                    choices=choices,
                ).execute()
        else:
            submenu_select = False
        
        # Check input and continue

        if submenu_select:
            match str(submenu_select):
                case "0": # Show related tasks
                    # Show tasks
                    show_project_tasks(cursor=cursor, conn=conn, check=checks[0])
                    # Open 
                case "1": # Mark as completed
                    for check in checks:
                        finish_entry(cursor=cursor, table=table, conn=conn, id_num=check)
                case "2": # Delete
                    for check in checks:
                        delete_entry(cursor=cursor, conn=conn, table=table, id_num=check)
                case "3": # Edit
                    edit_entry(cursor=cursor, conn=conn, table=table, id_list=checks)   
                case "4": # Return
                    pass

def popup_timer(cursor, conn, checks):
    """
    Creates Timer and Timewindow objects, which results in a pop-up timer. 
    """
    # Fetch global timer_list variable
    global timer_list
    # Exit function if no selection made
    if not checks or len(checks) != 1:
        return
    # Get the task_name
    task_id = checks[0]
    cursor.execute(f"SELECT name FROM tasks WHERE id = {task_id}")
    row = cursor.fetchone()
    task_name = row[0] if row else f"Task {task_id}"
    
    # Create Timer object
    task_timer = Timer(task_name=task_name, task_id=task_id)
    # Create Timer Window
    popup_timer = TimerWindow(task_timer=task_timer, cursor=cursor, conn=conn)

def timer_context_menu(cursor, conn, checks):
    """
    Context menu to start or stop a timer for the selected task.
    Requires exactly one task to be selected.
    """
    # Fetch global timer_list variable
    global timer_list
    # Exit function if no selection made
    if not checks or len(checks) != 1:
        return
    # Get the task_name
    task_id = checks[0]
    cursor.execute(f"SELECT name FROM tasks WHERE id = {task_id}")
    row = cursor.fetchone()
    task_name = row[0] if row else f"Task {task_id}"
    # Create menu options
    choices = [Choice(value="0", name="Start timer"), Choice(value="1", name="Stop timer"), Choice(value="2", name="Return")]
    choices.insert(0, Separator())
    choice = inquirer.select(message="Timer", choices=choices).execute()
    if choice is None:
        return

    match choice:
        case "0":  # Start timer
            # Create Timer object only if there is none other yet.
            if len(timer_list)==0:
                task_timer = Timer(task_name=task_name, task_id=task_id)
                # Start timer
                task_timer.start_timer()
                # Append to list
                timer_list.append(task_timer)
            else:
                print("A timer is already running! Please stop that one first.")
            
        case "1":  # Stop timer
            # Stop the timer
            timer_list[0].stop_timer()
            # Update database
            update_time_spent(cursor=cursor, conn=conn, table="tasks", timer_object=timer_list[0])
            # Delete the timer from the list
            del timer_list[0]
                
        case "2":  # Return
            pass
        
def update_time_spent(cursor, conn, table, timer_object):
    """Add elapsed_time (seconds) to the task's time_spent. Uses parameterized queries."""
    # Get timer attributes
    task_id = timer_object.task_id
    elapsed_time = timer_object.elapsed_time
    # Get the time already spent on the given task
    cursor.execute(f"SELECT time_spent FROM tasks WHERE id = {task_id}")
    row = cursor.fetchone()
    prev_time = row[0] if row is not None and row[0] is not None else 0
    # Calculate new amount of time spent and update database
    new_time = prev_time + int(elapsed_time)
    cursor.execute("UPDATE tasks SET time_spent = ? WHERE id = ?", (new_time, task_id))
    conn.commit()


def show_project_tasks(cursor, conn, check):
    """
    Displays all tasks associated with a specific project.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        check (int): The project ID.
    """
    # Define query
    query = f"""
    SELECT tasks.id, tasks.name, tasks.priority, tasks.status, tasks.end_date, tasks.reward 
    FROM tasks LEFT JOIN projects ON tasks.project_id = projects.id WHERE projects.id = {check};
    """
    
    # Display tasks and offer selection options
    checks = display_and_select(cursor=cursor, table="projects", alt_query=query)
    context_menu(cursor=cursor, conn=conn, checks=checks, table="tasks")


def show_subtasks(cursor, conn, task_id):
    """
    Displays all subtasks associated with a specific task.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        task_id (int): The parent task ID.
    """
    condition = f"""task_id = {task_id}"""
    checks = display_and_select(cursor=cursor, table="subtasks", condition=condition)
    context_menu(cursor = cursor, conn=conn, checks=checks, table="subtasks")


# ==========================================
# UPDATE & DELETION LOGIC
# ==========================================

def delete_entry(cursor, conn, table, id_num):
    """
    Deletes a specific record from a table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_num (int): The ID to delete.
    """
    # Define query
    query = f"DELETE FROM {table} WHERE id = {id_num}"
    # Execute statement
    cursor.execute(query)
    # Commit changes
    conn.commit()


def edit_entry(cursor, conn, table, id_list: list):
    """
    Prompts for a field and new value to update multiple records.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_list (list): List of IDs to update.
    """
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Define options
    choices = [Choice(header) for header in headers if header != "id"] # make id not editable
    choices.insert(0, Separator())
    # Present selection menu
    selected_field = inquirer.select(message="Select field to edit:",
                                  choices=choices).execute()
    
    # If selected field is project_id: list all projects
    if selected_field == "project_id":
        list_entries(cursor=cursor, table="projects")
    
    # Ask user for input to get new value for chosen field
    new_value = inquirer.text(message="Enter here: ").execute()
    
    # Add apostrophes if date or description text
    if not new_value.isnumeric():
        new_value = f"'{new_value}'"
    
    # Get appropriate values for cost and reward values
    if "cost" in selected_field and table=="shop":
        # Get cost mapping from settings
        settings = read_settings_file()
        cost_dict = settings['cost_mapping']
        # Set new value using cost dictionary
        new_value = cost_dict[new_value]
    
    if "reward" in selected_field and table == "tasks":
        # Get the reward mapping from the settings
        settings = read_settings_file()
        reward_dict = settings['reward_mapping'] # {reward_value: coin_amount}
        # Set the new value
        new_value = reward_dict[new_value]
           
    # Give all id's in list same updated value
    for id_num in id_list:
        # Define query
        query = f"""UPDATE {table} SET {selected_field}={new_value} WHERE id={id_num}"""
        
        # Execute statement
        cursor.execute(query)
    
    # Commit changes
    conn.commit()


def finish_entry(cursor, conn, table, id_num):
    """
    Marks an entry as completed (status 2) and handles rewards/coins.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_num (int): The ID to mark as finished.
    """
    # Load the settings file
    settings = read_settings_file()
    # Dictionary to define reward value, {reward_value: coin_amount}
    reward_dict = settings['reward_mapping']
    # Define query
    query = f"""UPDATE {table} SET status = 2 WHERE id = {id_num}"""
    cursor.execute(query)
    # Depending on table perform different actions
    if table == "tasks":
        # Update coins depending on reward
        reward_value = str(get_reward_value(cursor=cursor, id_num=id_num))
        update_coin_amount(cursor=cursor, conn=conn, increase_amount=int(reward_value))
        # Print message
        print(f"Task completed! You have been rewarded {reward_value} Coins!")
    elif table == "projects":
        print("Project completed! Well done.")
    elif table == "subtasks":
        print("Subtask completed! Well done.")
        
    # Play coin sound
    playsound(os.path.join("data", "sounds", "coin.mp3"))
        
    # Commit changes
    conn.commit()


# ==========================================
# ECONOMY & REWARDS
# ==========================================

def add_reward(cursor, conn):
    """
    Adds a new purchasable reward to the shop.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
    """
    # To build query we need some information
    # Load the settings file
    settings = read_settings_file()
    # Dictionary to define cost value, {reward_value: coin_amount}
    cost_dict = settings['cost_mapping']
    reward_description = inquirer.text(message="What is the reward? ").execute()
    reward_cost = inquirer.text(message="How big is the reward? [0; small, 1;medium, 2; big]",
                                validate=NumberValidator()).execute()
    # Calculate cost
    transformed_cost = cost_dict[reward_cost]
    
    # Get id number
    new_id = determine_id(cursor=cursor, table_name="shop")
        
    # Execute statement and save changes
    cursor.execute(
        """INSERT INTO shop(id, reward, cost) VALUES(?,?,?)""", 
        (new_id, reward_description, transformed_cost)
        )
    conn.commit()


def buy_reward(cursor, conn, checks):   
    """
    Handles the purchase of shop rewards using user coins.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        checks (list): List of reward IDs to purchase.
    """
    # Calculate cost based on selection
    cost_total = 0
    for check in checks:
        query = f"""SELECT cost FROM shop WHERE id = {check}"""
        cursor.execute(query)
        cost_total += cursor.fetchone()[0]
    # Get coin balance
    balance = get_coin_amount(cursor=cursor)
    
    # Check if balance is sufficient and act accordingly
    if balance < cost_total:
        print(f"Your balance ({balance} Coins) is not sufficient. Complete more tasks!")
    else:
        # Ask for confirmation
        confirm = inquirer.confirm(message=f"This reward costs {cost_total} Coins. Please confirm your purchase [Y/N]:").execute()
        if confirm:
            # Deduct balance
            update_coin_amount(cursor=cursor, conn=conn, increase_amount=-cost_total)
            if len(checks) > 1:
                # Show new balance and print congratulatory message
                print(f"Enjoy your rewards! Your new balance is {balance-cost_total} Coins.")
            else:
                # Show new balance and print congratulatory message
                print(f"Enjoy your reward! Your new balance is {balance-cost_total} Coins.")
            
            # TODO: store transaction in history


def get_reward_value(cursor, id_num):
    """
    Retrieves the reward coin value for a specific task.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        id_num (int): The task ID.
        
    Returns:
        int: The reward value.
    """
    # Define query
    query = f"""SELECT reward FROM tasks WHERE id = {id_num}"""
    cursor.execute(query)
    reward_value = cursor.fetchone()[0]
    return reward_value


def get_coin_amount(cursor):
    """
    Retrieves the current coin balance for the user.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        
    Returns:
        int: Total coins.
    """
    # Define query
    query="""SELECT coins FROM user WHERE id = 1"""
    # Execute statement
    cursor.execute(query)
    # Fetch result
    coins = cursor.fetchone()[0]

    return coins


def update_coin_amount(cursor, conn, increase_amount: int):
    """
    Updates the user's coin balance.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        increase_amount (int): Amount to add (use negative for deduction).
    """
    # Get current amount
    current_amount = get_coin_amount(cursor)
    
    # Calculate new amount
    new_amount = current_amount + increase_amount
    
    # Define query
    query = f"""UPDATE user SET coins = {new_amount} where id = 1"""
    # Execute command
    cursor.execute(query)
    # Commit changes
    conn.commit()
