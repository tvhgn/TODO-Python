"""
Project-related database operations.
"""
from datetime import datetime
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

from db.database import determine_id


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


def show_project_tasks(cursor, conn, check):
    """
    Displays all tasks associated with a specific project.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        check (int): The project ID.
    """
    from db.display import display_and_select
    from db.context_menu import context_menu
    
    # Define query
    query = f"""
    SELECT tasks.id, tasks.name, tasks.priority, tasks.status, tasks.end_date, tasks.reward 
    FROM tasks LEFT JOIN projects ON tasks.project_id = projects.id WHERE projects.id = {check};
    """
    
    # Display tasks and offer selection options
    checks = display_and_select(cursor=cursor, table="projects", alt_query=query)
    context_menu(cursor=cursor, conn=conn, checks=checks, table="tasks")
