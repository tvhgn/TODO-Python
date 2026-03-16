"""
Task-related database operations.
"""
from datetime import datetime
from InquirerPy import inquirer

from db.database import determine_id
from db.display import list_entries
from helpers.settings import read_settings_file


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

