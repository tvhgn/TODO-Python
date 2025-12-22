from sqlite_python import *

import os
from datetime import datetime

from InquirerPy import inquirer

#DB_FILE = os.path.join("database", "todos.db")

def show_menu(conn):
    # Create cursor
    cursor = conn.cursor()
    
    while True:
        # Get coin amount
        coins = get_coin_amount(cursor)
        # Show menu options and get selection
        main_select = inquirer.select(
            message=f"\nMain Menu\nBalance: {coins} Coins",
            choices=["Today's Tasks", "Inbox", "Tasks", "Projects", "Users", "Shop","Exit"],
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
                checks = display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                # Offer selection based on checked entries
                context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                            
            # Inbox
            case "Inbox":
                #show_inbox(cursor)
                # Define condition
                condition = "project_id = 1"
                # Fetch entries and guide through submenus
                checks = display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                
            # Tasks Menu
            case "Tasks":
                # Present submenu
                choices = [Choice(value=str(i), name=opt) for i,opt in enumerate(["Add Task", "Show Pending Tasks", "Show Completed Tasks", "Return"])]
                task_menu_select = inquirer.select(message="Select action: ",
                                                   choices=choices).execute()
                # Actions for each option
                if task_menu_select:
                    match str(task_menu_select):
                        case "0": # Add task
                            add_task(cursor=cursor, conn=conn)
                        case "1": # Show all pending tasks
                            # Condition
                            condition = "NOT status = 2"
                            # Fetch entries and guide through submenus
                            checks = display_and_select(cursor=cursor, conn=conn, table="tasks", condition =condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                        case "2": # Show completed tasks
                            condition = "status = 2"
                            checks = display_and_select(cursor=cursor, conn=conn, table="tasks", condition=condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                        case "3": # Return
                            pass
                            
                
            # Projects Menu
            case "Projects":
                # Present submenu
                choices = [Choice(value=str(i), name=opt) for i, opt in 
                           enumerate(["Add Project", "Show All Projects", "Show Completed Projects", "Return"])]
                project_menu_select = inquirer.select(message="Select action: ",
                                                      choices=choices).execute()
                # Actions for each option
                if project_menu_select:
                    match project_menu_select:
                        case "0":
                            add_project(cursor=cursor, conn=conn, initialize=False)
                        case "1":
                            checks = display_and_select(cursor=cursor, conn=conn, table="projects") # Show entries, format, and offer checkbox selection
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "projects") # Offer options based on checked entries
                        case "2":
                            condition = "status = 2"
                            checks = display_and_select(cursor=cursor, conn=conn, table="projects", condition=condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "projects")
                        case "3":
                            pass
            
            case "Users":
                pass
            case "Shop":
                # Define options for shop menu
                choices = [Choice(value=str(i), name=opt) for i, opt in
                           enumerate(["Add Reward", "Buy Reward", "Edit Reward", "See Available Rewards", "Return"])]
                # Present menu
                shop_menu_select = inquirer.select(message="Select action: ",
                                                   choices=choices).execute()
                # Actions for each option
                if shop_menu_select:
                    match shop_menu_select:
                        case "0": # Add reward
                            add_reward(cursor=cursor, conn=conn)
                        case "1": # Buy reward
                            checks = display_and_select(cursor=cursor, conn=conn, table="shop")
                            buy_reward(cursor=cursor, checks=checks, conn=conn)
                        case "2": # Edit reward
                            checks = display_and_select(cursor=cursor, conn=conn, table="shop")
                            edit_entry(cursor=cursor, conn=conn, table="shop", id_list=checks)
                        case "3":
                            list_entries(cursor=cursor, table="shop")
                        case "3": # Return
                            pass
                    
                            
            case "Exit":
                break
            case _:
                raise RuntimeError("Command not yet specified!")

