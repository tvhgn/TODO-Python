import sqlite3

from helpers.settings import read_settings_file


def get_project_name(DB_FILE:str, project_id:int) -> str:
    """
    Retrieves the name of a project given its ID from the database.

    Args:
        DB_FILE (str): Path to database file.
        project_id (int): ID given to the project as registered in the projects table.

    Returns:
        str: The name of the project corresponding to the project_id.
    """
    # Establish a connection
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        query = f"""SELECT name FROM projects WHERE id = {project_id}"""
        cursor.execute(query)
        try:
            project_name = cursor.fetchone()[0]
            return project_name
        except TypeError as e:
            print("None type detected, list is probably empty.")
            return "Unfiled"
        

def get_project_id(DB_FILE: str, project_name: str) -> int:
    """
    Retrieves the ID of a project given its name from the database.

    Args:
        DB_FILE (str): Path to database file.
        project_name (str): Name of the project as registered in the projects table.

    Returns:
        int: The ID of the project corresponding to the project_name.
    """
    # Establish a connection
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        query = f"""SELECT id FROM projects WHERE name = '{project_name}'"""
        cursor.execute(query)
        project_id = cursor.fetchone()[0]
        return project_id
    
def transform_value(DB_FILE: str, original_value: str | int, category:str) -> str:
    """
    Transforms reward, status or priority values to their counterparts.

    Args:
        DB_FILE (str): Path to database file
        original_value (str | int): The original value to be transformed.
    Returns:
        The transformed value.
    """
    # Mapping of values
    priority_dict = {
        0: "low",
        1: "medium",
        2: "high"
    }
    
    reward_dict = {
        0: "low",
        1: "medium",
        2: "high"
    }
    
    status_dict = {
        0: "not started",
        1: "in progress",
        2: "done"
    }
    
    # new value becomes the counterpart value
    if category == "reward":
        if type(original_value) is int:
            new_value = reward_dict[original_value]
        else:
            key_label = [key for key, val in reward_dict.items() if val == original_value][0]
            new_value = key_label
    elif category == "priority":
        if type(original_value) is int:
            new_value = priority_dict[original_value]
        else:
            key_label = [key for key, val in priority_dict.items() if val == original_value][0]
            new_value = key_label
    elif category == "status":
        if type(original_value) is int:
            new_value = status_dict[original_value]
        elif original_value == "NULL":
            new_value = ""
        else:
            key_label = [key for key, val in status_dict.items() if val == original_value][0]
            new_value = key_label
    else:
        raise ValueError("category parameter was not recognized. Enter 'reward', 'priority', or 'status'.")
            
    return new_value

