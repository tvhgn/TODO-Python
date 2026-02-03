"""
Context menus for different entity types.
"""
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator

from db.tasks import check_subtasks
from db.subtasks import add_subtask, show_subtasks
from db.projects import show_project_tasks
from db.operations import delete_entry, edit_entry, finish_entry
from db.timers import popup_timer


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
