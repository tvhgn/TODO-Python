from sqlite_python import *

import os
from datetime import datetime

from InquirerPy import inquirer

#DB_FILE = os.path.join("database", "todos.db")

def show_menu(conn):
    # Create cursor
    cursor = conn.cursor()
    
    while True:
        # Show menu options and get selection
        main_select = inquirer.select(
            message="Main Menu",
            choices=["Today's Tasks", "Inbox", "Tasks", "Projects", "Users", "Exit"],
        ).execute()

        # Show submenu's based on selection
        match main_select:
            # Today
            case "Today's Tasks":
                # Get today's date
                today = datetime.today()
                today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
                # Define condition
                condition = f"end_date = '{today}'"
                # Fetch entries and guide through submenus
                display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                            
            # Inbox
            case "Inbox":
                #show_inbox(cursor)
                # Define condition
                condition = "project_id = 1"
                # Fetch entries and guide through submenus
                display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                
            # Tasks Menu
            case "Tasks":
                # Present submenu
                choices = [Choice(value=i, name=opt) for i,opt in enumerate(["Add Task", "Show All Tasks", "Show Completed Tasks", "Return"])]
                task_menu_select = inquirer.select(message="Select action: ",
                                                   choices=choices).execute()
                # Actions for each option
                if task_menu_select:
                    match task_menu_select:
                        case 0: # Add task
                            add_task(cursor=cursor, conn=conn)
                        case 1: # Show all tasks
                            # Fetch entries and guide through submenus
                            display_and_select(cursor=cursor, conn=conn, table="tasks")
                        case 2: # Show completed tasks
                            condition = "status = 2"
                            display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                        case 3: # Return
                            pass
                            
                
            # Projects Menu
            case "Projects":
                # Present submenu
                choices = [Choice(value=i, name=opt) for i, opt in 
                           enumerate(["Add Project", "Show All Projects", "Show Completed Projects", "Return"])]
                project_menu_select = inquirer.select(message="Select action: ",
                                                      choices=choices).execute()
                # Actions for each option
                if project_menu_select:
                    match project_menu_select:
                        case 0:
                            add_project(cursor=cursor, conn=conn)
                        case 1:
                            display_and_select(cursor=cursor, conn=conn, table="projects")
                        case 2:
                            condition = "status = 2"
                            display_and_select(cursor=cursor, conn=conn, table="projects", condition=condition)
                        case 3:
                            pass
            
            case "Users":
                pass
            case "Exit":
                break
            case _:
                raise RuntimeError("Command not yet specified!")

