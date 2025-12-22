import sqlite3
from datetime import datetime

from prettytable import PrettyTable
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator

from helpers.effects import strike

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

def add_project(cursor, conn, initialize=False):
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
    table = PrettyTable()
    table.field_names = headers
    table.add_rows(results)
    print(table)
        
    # If data is desired return the results
    if get_entries:
        return results
    # Otherwise just give the number.
    return total_rows

def display_and_select(cursor, conn, table, condition:str="NULL"):    
    # Define query depending on condition presence
    if condition != "NULL":
        query = f"SELECT * FROM {table} WHERE {condition};"
    else:
        query = f"""SELECT * FROM {table};"""
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

def context_menu(cursor, conn, checks, table):
    if table != "shop":
        # Submenu
        choices = [Choice(value=str(i), name=opt) for i, opt in enumerate(["Mark as completed", "Delete", "Edit", "Return"])]
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
                case "0": # Mark as completed
                    for check in checks:
                        finish_entry(cursor=cursor, table=table, conn=conn, id_num=check)
                case "1": # Delete
                    for check in checks:
                        delete_entry(cursor=cursor, conn=conn, table=table, id_num=check)
                case "2": # Edit
                    edit_entry(cursor=cursor, conn=conn, table=table, id_list=checks)   
                case "3": # Return
                    pass

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

def delete_entry(cursor, conn, table, id_num):
    # Define query
    query = f"DELETE FROM {table} WHERE id = {id_num}"
    # Execute statement
    cursor.execute(query)
    # Commit changes
    conn.commit()
    
    
    
def edit_entry(cursor, conn, table, id_list:list):
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
    
    # Add accents if selected field contains date information
    if "date" in selected_field:
        selected_field = f"'{selected_field}'"
        
    if "cost" in selected_field and table=="shop":
        cost_dict = {"0": 40, "1":80, "2":160}
        new_value = cost_dict[new_value]
        
    if "reward" in selected_field and table == "tasks":
        reward_dict = {0: 5, 1: 10, 2: 30} # {reward_value: coin_amount}
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
    # Define query
    query = f"""UPDATE {table} SET status = 2 WHERE id = {id_num}"""
    cursor.execute(query)
    # Depending on table perform different actions
    if table == "tasks":
        # Dictionary to define reward value
        reward_dict = {0: 5, 1: 10, 2: 30} # {reward_value: coin_amount}
        # Update coins depending on reward
        reward_value = get_reward_value(cursor=cursor, id_num=id_num)
        update_coin_amount(cursor=cursor, conn=conn, reward_value=reward_value)
        # Print message
        print(f"Task completed! You have been rewarded {reward_dict[reward_value]} Coins!")
    else:
        print("Project completed! Well done.")
        
    # Commit changes
    conn.commit()
    
    
        
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

def add_reward(cursor, conn):
    # To build query we need some information
    reward_dict = {"0": 40, "1":80, "2":160}
    reward_description = inquirer.text(message="What is the reward? ").execute()
    reward_cost = inquirer.text(message="How big is the reward? [0; small, 1;medium, 2; big]",
                                validate=NumberValidator()).execute()
    # Calculate cost
    transformed_cost = reward_dict[reward_cost]
    
    # Get id number
    new_id = determine_id(cursor=cursor, table_name="shop")
        
    # Execute statement and save changes
    cursor.execute(
        """INSERT INTO shop(id, reward, cost) VALUES(?,?,?)""", 
        (new_id, reward_description, transformed_cost)
        )
    conn.commit()
    
    
def buy_reward(cursor, conn, checks):   
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
            update_coin_amount(cursor=cursor, conn=conn, reward_value=-cost_total)
            if len(checks) > 1:
                # Show new balance and print congratulatory message
                print(f"Enjoy your rewards! Your new balance is {balance-cost_total} Coins.")
            else:
                # Show new balance and print congratulatory message
                print(f"Enjoy your reward! Your new balance is {balance-cost_total} Coins.")
            
            # TODO: store transaction in history


def get_reward_value(cursor, id_num):
    # Define query
    query = f"""SELECT reward FROM tasks WHERE id = {id_num}"""
    cursor.execute(query)
    reward_value = cursor.fetchone()[0]
    return reward_value

def get_coin_amount(cursor):
    # Define query
    query="""SELECT coins FROM user WHERE id = 1"""
    # Execute statement
    cursor.execute(query)
    # Fetch result
    coins = cursor.fetchone()[0]

    return coins

def update_coin_amount(cursor, conn, reward_value):
    # Dictionary to define reward value
    reward_dict = {0: 5, 1: 10, 2: 30} # {reward_value: coin_amount}
    
    # Get current amount
    current_amount = get_coin_amount(cursor)
    
    # Calculate new amount
    new_amount = current_amount + reward_dict[reward_value]
    
    # Define query
    query = f"""UPDATE user SET coins = {new_amount} where id = 1"""
    # Execute command
    cursor.execute(query)
    # Commit changes
    conn.commit()