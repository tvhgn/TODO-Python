import os
from datetime import datetime, timedelta
import logging  # Import the logging module

from InquirerPy import inquirer
from InquirerPy.base import Choice

from helpers.backup import create_backup
from helpers.settings import *
from ai_assistance import *
from db.users import *
from db.tasks import *
from db.projects import *
from db.timers import *
from db.display import *
from db.context_menu import *
from db.shop import *

# Configure logging for gui module if needed, or rely on main.py's configuration
# If you want separate log files or formats for GUI, configure here.
# For now, we'll assume it uses the app.log configured in main.py

def show_log_gui(conn):
    """Displays the contents of the application log file."""
    os.system("clear")
    print("--- Application Log ---")
    try:
        with open("app.log", "r") as f:
            log_content = f.read()
            if not log_content:
                print("Log file is empty.")
            else:
                print(log_content)
    except FileNotFoundError:
        print("Log file 'app.log' not found.")
    except Exception as e:
        print(f"An error occurred while reading the log file: {e}")

    # Add a way to return to the main menu
    input("\nPress Enter to return to the main menu...")

def show_menu(conn):
    # Create cursor
    cursor = conn.cursor()
    
    # CLear the screen
    os.system("clear")
    
    # Read settings file
    settings_file = read_settings_file()
    
    while True:
        # Get coin amount
        coins = get_coin_amount(cursor)
        
        # Create a backup of the database
        #dest_filename = "todos" + datetime.now().strftime("%Y_%m_%d_") + ".db"
        try:
            create_backup(src_file_name="todos.db",
                          src_dir=os.path.join("data", "database"),
                          dst_dir=settings_file['backup_directory'])
        except Exception as e:
            logging.error(f"Error during backup: {e}") # Log backup error

        # Show menu options and get selection
        main_select = inquirer.select(
            message=f"\nMain Menu\nBalance: {coins} Coins",
            choices=["Assistant", "Today's Tasks", "Inbox", "Tasks", "Projects", "Users", "Shop", "View Log", "Exit"], # Added "View Log"
        ).execute()

        logging.info(f"User selected: {main_select}") # Log menu selection

        # Show submenu's based on selection
        match main_select:
            case "Assistant":
                # Create options
                choices = [Choice(value=str(i), name=opt) for i,opt in enumerate(["Advice for Today", "Task Breakdown"])]
                assistant_select = inquirer.select(
                    message=f"Select option",
                    choices=choices
                ).execute()

                if assistant_select:
                    logging.info(f"Assistant submenu selected: {assistant_select}") # Log assistant submenu selection
                    match assistant_select:
                        case "0":
                            # Advice for today
                            summarize_today(cursor)
                        case "1":
                            pass
                        
            # Today
            case "Today's Tasks":
                logging.info("Navigated to Today's Tasks.") # Log navigation
                # Get today's date as well as tomorrow's
                today = datetime.today()
                tomorrow = today + timedelta(days=1)
                today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
                tomorrow = tomorrow.strftime('%Y-%m-%d')
                # Define condition
                condition = f"(end_date = {today}) OR (end_date < '{tomorrow}' AND NOT status = 2)" # Get today's tasks, as well as unfinished tasks from before
                # Fetch entries and guide through submenus
                checks = display_and_select(cursor=cursor, table="tasks", condition=condition)
                # Offer selection based on checked entries
                context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                            
            # Inbox
            case "Inbox":
                logging.info("Navigated to Inbox.") # Log navigation
                #show_inbox(cursor)
                # Define condition
                condition = "project_id = 1"
                # Fetch entries and guide through submenus
                checks = display_and_select(cursor=cursor, table="tasks", condition=condition)
                context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                
            # Tasks Menu
            case "Tasks":                
                logging.info("Navigated to Tasks menu.") # Log navigation
                # Present submenu
                choices = [Choice(value=str(i), name=opt) for i,opt in enumerate(["Add Task", "Show Pending Tasks", "Show Completed Tasks", "Return"])]
                task_menu_select = inquirer.select(message="Select action: ",
                                                   choices=choices).execute()
                logging.info(f"Tasks menu selection: {task_menu_select}") # Log task menu selection
                # Actions for each option
                if task_menu_select:
                    match str(task_menu_select):
                        case "0": # Add task
                            add_task(cursor=cursor, conn=conn)
                        case "1": # Show all pending tasks
                            # Condition
                            condition = "NOT status = 2"
                            # Fetch entries and guide through submenus
                            checks = display_and_select(cursor=cursor, table="tasks", condition =condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                        case "2": # Show completed tasks
                            condition = "status = 2"
                            checks = display_and_select(cursor=cursor, table="tasks", condition=condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "tasks")
                        case "3": # Return
                            pass
                

            # Projects Menu
            case "Projects":
                logging.info("Navigated to Projects menu.") # Log navigation
                # Present submenu
                choices = [Choice(value=str(i), name=opt) for i, opt in 
                           enumerate(["Add Project", "Show All Projects", "Show Completed Projects", "Return"])]
                project_menu_select = inquirer.select(message="Select action: ",
                                                      choices=choices).execute()
                logging.info(f"Projects menu selection: {project_menu_select}") # Log project menu selection
                # Actions for each option
                if project_menu_select:
                    match project_menu_select:
                        case "0": # Add project
                            add_project(cursor=cursor, conn=conn, initialize=False)
                        case "1": # Show all projects
                            checks = display_and_select(cursor=cursor, table="projects") # Show entries, format, and offer checkbox selection
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "projects") # Offer options based on checked entries
                        case "2": # Show completed
                            condition = "status = 2"
                            checks = display_and_select(cursor=cursor, table="projects", condition=condition)
                            context_menu(cursor=cursor, conn=conn, checks=checks, table = "projects")
                        case "3": # Return
                            pass
            
            case "Users":
                logging.info("Navigated to Users menu.") # Log navigation
                pass
            case "Shop":
                logging.info("Navigated to Shop menu.") # Log navigation
                # Define options for shop menu
                choices = [Choice(value=str(i), name=opt) for i, opt in
                           enumerate(["Add Reward", "Buy Reward", "Edit Reward", "See Available Rewards", "Return"])]
                # Present menu
                shop_menu_select = inquirer.select(message="Select action: ",
                                                   choices=choices).execute()
                logging.info(f"Shop menu selection: {shop_menu_select}") # Log shop menu selection
                # Actions for each option
                if shop_menu_select:
                    match shop_menu_select:
                        case "0": # Add reward
                            add_reward(cursor=cursor, conn=conn)
                        case "1": # Buy reward
                            checks = display_and_select(cursor=cursor, table="shop")
                            buy_reward(cursor=cursor, checks=checks, conn=conn)
                        case "2": # Edit reward
                            checks = display_and_select(cursor=cursor, table="shop")
                            edit_entry(cursor=cursor, conn=conn, table="shop", id_list=checks)
                        case "3":
                            list_entries(cursor=cursor, table="shop")
                        case "4": # Return (changed from 3 to 4 to match the addition of "View Log")
                            pass
                            

            # New case for viewing the log
            case "View Log":
                logging.info("User requested to view the log.") # Log log view request
                show_log_gui(conn)

            case "Exit":
                logging.info("User selected Exit. Shutting down.") # Log exit
                break
            case _:
                logging.warning(f"Unrecognized menu selection: {main_select}") # Log unrecognized input
                raise RuntimeError("Command not yet specified!")

# Note: In gui.py, we're relying on the logging configuration from main.py.
# If gui.py were to be run as a standalone script, it would need its own logging configuration.
