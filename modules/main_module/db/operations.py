"""
Common database operations (update, delete, edit).
"""
import os
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from playsound3 import playsound

from db.display import list_entries
from db.tasks import get_reward_value
from db.users import update_coin_amount
from helpers.settings import read_settings_file


def delete_entry(cursor, conn, table, id_num):
    """
    Deletes a specific record from a table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_num (int): The ID to delete.
    """
    # Define query
    query = f"DELETE FROM {table} WHERE id = {id_num}"
    # Execute statement
    cursor.execute(query)
    # Commit changes
    conn.commit()


def edit_entry(cursor, conn, table, id_list: list):
    """
    Prompts for a field and new value to update multiple records.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_list (list): List of IDs to update.
    """
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Define options
    choices = [Choice(header) for header in headers if header != "id"] # make id not editable
    choices.insert(0, Separator())
    # Present selection menu
    selected_field = inquirer.select(message="Select field to edit:",
                                  choices=choices).execute()
    
    # If selected field is project_id: list all projects
    if selected_field == "project_id":
        list_entries(cursor=cursor, table="projects")
    
    # Ask user for input to get new value for chosen field
    new_value = inquirer.text(message="Enter here: ").execute()
    
    # Add apostrophes if date or description text
    if not new_value.isnumeric():
        new_value = f"'{new_value}'"
    
    # Get appropriate values for cost and reward values
    if "cost" in selected_field and table=="shop":
        # Get cost mapping from settings
        settings = read_settings_file()
        cost_dict = settings['cost_mapping']
        # Set new value using cost dictionary
        new_value = cost_dict[new_value]
    
    if "reward" in selected_field and table == "tasks":
        # Get the reward mapping from the settings
        settings = read_settings_file()
        reward_dict = settings['reward_mapping'] # {reward_value: coin_amount}
        # Set the new value
        new_value = reward_dict[new_value]
           
    # Give all id's in list same updated value
    for id_num in id_list:
        # Define query
        query = f"""UPDATE {table} SET {selected_field}={new_value} WHERE id={id_num}"""
        
        # Execute statement
        cursor.execute(query)
    
    # Commit changes
    conn.commit()


def finish_entry(cursor, conn, table, id_num):
    """
    Marks an entry as completed (status 2) and handles rewards/coins.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        table (str): Table name.
        id_num (int): The ID to mark as finished.
    """
    # Load the settings file
    settings = read_settings_file()
    # Dictionary to define reward value, {reward_value: coin_amount}
    reward_dict = settings['reward_mapping']
    # Define query
    query = f"""UPDATE {table} SET status = 2 WHERE id = {id_num}"""
    cursor.execute(query)
    # Depending on table perform different actions
    if table == "tasks":
        # Update coins depending on reward
        reward_value = str(get_reward_value(cursor=cursor, id_num=id_num))
        update_coin_amount(cursor=cursor, conn=conn, increase_amount=int(reward_value))
        # Print message
        print(f"Task completed! You have been rewarded {reward_value} Coins!")
    elif table == "projects":
        print("Project completed! Well done.")
    elif table == "subtasks":
        print("Subtask completed! Well done.")
        
    # Play coin sound
    playsound(os.path.join("data", "sounds", "coin.mp3"))
        
    # Commit changes
    conn.commit()
