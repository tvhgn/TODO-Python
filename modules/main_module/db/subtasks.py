"""
Subtask-related database operations.
"""
from datetime import datetime
from InquirerPy import inquirer

from db.database import determine_id


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


def show_subtasks(cursor, conn, task_id):
    """
    Displays all subtasks associated with a specific task.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        task_id (int): The parent task ID.
    """
    from db.display import display_and_select
    from db.context_menu import context_menu
    
    condition = f"""task_id = {task_id}"""
    checks = display_and_select(cursor=cursor, table="subtasks", condition=condition)
    context_menu(cursor = cursor, conn=conn, checks=checks, table="subtasks")
