from sqlite_python import *

DB_FILE = os.path.join("database", "todos.db")

def show_menu():
    # Show menu options
    print("""
    [0] Show Today's Tasks
    [1] Inbox
    [2] Tasks
    [3] Projects
    [4] Users
    [5] Options
    """)

    # Ask for user input
    selection = input("Select option: \n")

    # Show submenu's based on selection
    match selection:
        case "0":
            pass
        case "1":
            pass
        case "2":
            print("""
            [0] Add Tasks
            [1] Delete Tasks
            [2] Show High Priority Tasks
            [3] Show Urgent Tasks
            [4] Show All Pending Tasks
            [5] Show Completed Tasks
            """)
            selection = input("Select option: \n")
            match selection:
                case "0":
                    # Add task
                    add_task()
                case _:
                    raise RuntimeError("Command not yet specified!")
        case _:
            raise RuntimeError("Command not yet specified!")

