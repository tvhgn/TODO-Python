from sqlite_python import *

import os
from datetime import datetime

#DB_FILE = os.path.join("database", "todos.db")

def show_menu(conn):
    # Create cursor
    cursor = conn.cursor()
    
    while True:
        # Show menu options
        print("""
        [0] Show Today's Tasks
        [1] Inbox
        [2] Tasks
        [3] Projects
        [4] Users
        [5] Options
        [E]xit
        """)

        # Ask for user input
        selection = input("Select option: \n")

        # Show submenu's based on selection
        match selection:
            # Today
            case "0":
                # Get today's date
                today = datetime.today()
                today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
                # Define condition
                condition = f"end_date = '{today}'"
                # Fetch entries
                _ = list_entries(cursor=cursor, table='tasks', condition=condition)
                # Present options
                print("""
                      [M]ark task as finished
                      [R]eturn
                      """)
                while True:
                    selection = input("\nSelect option: ")
                    match selection.lower():
                        # Mark as finished menu
                        case "m":
                            task_id = input("Enter ID of finished task: ")
                            finish_task(cursor=cursor, conn=conn, id_num=task_id)
                        case 'r':
                            break
                            
            # Inbox
            case "1":
                show_inbox(cursor)
            # Tasks Menu
            case "2":
                print("""
                [0] Add Task
                [1] Delete Task
                [2] Edit Task
                [3] Show High Priority Tasks
                [4] Show Urgent Tasks
                [5] Show All Pending Tasks
                [6] Show Completed Tasks
                [R]eturn
                """)
                
                while True:
                    selection = input("\nSelect option: ")
                    match selection.lower():
                        case "0":
                            # Add task
                            add_task(cursor=cursor, conn=conn)
                        case "2":
                            # Give message
                            print("Edit task...")
                            edit_entry(cursor=cursor, table="tasks")
                        case "r":
                            break
                        case _:
                            raise RuntimeError("Command not yet specified!")
            # Projects Menu
            case "3":
                print("""
                [0] Add Project
                [1] Delete Project
                [2] Edit Project
                [R]eturn
                    """)
                while True:
                    selection = input("\nSelect option: ")
                    match selection.lower():
                        case "0":
                            # Ask user input
                            project_name = input("Enter project description: ")
                            project_end = input("(Optional) When would you like to finish this project? [YYYY-MM-DD]: ")
                            # Check if default value is needed
                            if project_end == "":
                                project_end = "NULL"
                                
                            status = input("(Optional) What is the project's current status? [0; default] Not started [1] In progress [2] Finished: ")
                            # Status validation
                            if status == "":
                                status = 0
                            elif int(status) < 3:
                                status = int(status)
                            else:
                                print("Command was not recognized. Default value will be used.")
                                status = 0
                                
                            # Project begin is today's date
                            today = datetime.today()
                            project_begin = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
                            
                            
                            # Add the project
                            add_project(cursor=cursor,
                                        conn=conn,
                                        project_name=project_name,
                                        project_begin=project_begin,
                                        project_end=project_end,
                                        status=status)
                
                        case "2":
                            print("Edit Project...")
                            edit_entry(cursor=cursor, table="projects")
                        case "r":
                            break
            case "e":
                break
            case _:
                raise RuntimeError("Command not yet specified!")

