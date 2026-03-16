"""
Data retrieval and display functions.
"""
from datetime import datetime, timedelta
import sqlite3

from prettytable import PrettyTable
from InquirerPy import inquirer
from InquirerPy.base import Choice

from helpers.effects import strike


def list_entries(cursor, table, condition: str = "NULL", get_entries: bool = False, print_table: bool = True):
    """
    Lists and optionally returns entries from a database table.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        condition (str): SQL WHERE clause condition.
        get_entries (bool): Whether to return the results.
        print_table (bool): Whether to print the table to console.
        
    Returns:
        int or tuple: Row count or (PrettyTable, results) depending on get_entries.
    """
    # Define query depending on condition presence
    if condition != "NULL":
        query = f"SELECT * FROM {table} WHERE {condition};"
    else:
        query = f"""SELECT * FROM {table};"""
    # Execute query
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    total_rows = len(results)
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Using prettytables
    table_obj = PrettyTable()
    table_obj.field_names = headers
    table_obj.add_rows(results)
    
    if print_table:
        print(table_obj)
        
    # If data is desired return the results
    if get_entries:
        return (table_obj, results)
    # Otherwise just give the number.
    return total_rows

def get_table(db_file, table, condition:str = "NULL", alt_query:str = None):
    """
    Returns a table retrieved from SQL database, optionally filtered by a condition.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        condition (str): Optional filter.
        alt_query (str): Optional full SQL query to override default behavior.
        
    Returns:
        tuple: Table with results from SQL query (list), and headers (list).
    """
    if alt_query is None:
        # Define query depending on condition presence
        if condition != "NULL":
            query = f"SELECT * FROM {table} WHERE {condition};"
        else:
            query = f"""SELECT * FROM {table};"""
    else:
        query = alt_query
        
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        # Execute query
        cursor.execute(query)
        # Fetch results
        results = cursor.fetchall()
        results = [list(row) for row in results]
        # Get headers
        headers = [col[0] for col in cursor.description]
    
    return (results, headers)


def display_and_select(cursor, table, condition: str = "NULL", alt_query: str = None):    
    """
    Displays records in a formatted list and allows user to select them via checkboxes.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        condition (str): Optional filter.
        alt_query (str): Optional full SQL query to override default behavior.
        
    Returns:
        list: Selected IDs or None if no entries exist.
    """
    if alt_query is None:
        # Define query depending on condition presence
        if condition != "NULL":
            query = f"SELECT * FROM {table} WHERE {condition};"
        else:
            query = f"""SELECT * FROM {table};"""
    else:
        query = alt_query
    # Execute query
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Format entries for inquirer
    # First create dictionary
    results_dict_list = [dict(zip(headers, result)) for result in results] # Get structure like {a: 1, b:2, c:3} with letters being columns
    
    # Transform values
    # Transform time_spent to minutes instead of seconds
    for result in results_dict_list:
        if 'time_spent' in result and result['time_spent'] is not None:
            result['time_spent'] = int(result['time_spent'])//60 #Convert from seconds to minutes

    # Compute column widths (consider header and all values)
    col_widths = {}
    columns = zip(headers, *results)
    max_col_lengths = [max(list(map(lambda x:len(str(x)), column))) for column in columns]
    col_widths = dict(zip(headers, max_col_lengths))
    
    # Create headers and adjust for column width
    sep = "  |  "
    header_description = sep.join(h.ljust(col_widths[h]) for h in headers)
    header_description = "    " + header_description
    
    # Create options using Choice object while adjusting column widths
    choices = []
    for row in results_dict_list:
        # Create name string
        choice_description = sep.join(str(row[h]).ljust(col_widths[h]) for h in headers)
        if "status" in headers:
            # If task is finished, strikethrough
            if row['status'] == 2: 
                choice_description = strike(choice_description)
            
        # Build Choice object
        choice = Choice(value=row['id'],
                        name = choice_description,
                        enabled=False)
        # Append to choices
        choices.append(choice)
        
    # Use choices to create checkbox selection menu   
    print(header_description)  # print headers
    if len(choices) != 0:
        checks = inquirer.checkbox(
            message="Select (at least) one:",
            choices=choices,
            mandatory=False
            ).execute()
    else:
        print("No entries available!")
        checks = None
    
    return checks


def get_entry(cursor, table, id_num=None, col=None):
    """
    Fetches a specific row or column value from a table by ID.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        table (str): Table name.
        id_num (int/str): The ID of the record.
        col (str): Specific column name to fetch.
        
    Returns:
        tuple or Any: The fetched row or value.
    """
    # Cast id number to integer
    id_num = int(id_num)
        
    # Define query
    if col is None: # When no specific column has been specified
        query = f"""SELECT * FROM {table} WHERE id = {id_num}"""
    else:
        query = f"""SELECT {col} FROM {table} WHERE id = {id_num}"""
    # Execute statement
    cursor.execute(query)
    # Fetch results
    result = cursor.fetchone()
    return result


def get_today(cursor):
    """
    Retrieves and formats a string of tasks due today or overdue.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        
    Returns:
        str: Formatted text for display.
    """
    # Get today's date as well as tomorrow's
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
    tomorrow = tomorrow.strftime('%Y-%m-%d')
    # Define condition
    condition = f"(end_date = {today}) OR (end_date < '{tomorrow}' AND NOT status = 2)" # Get today's tasks, as well as unfinished tasks from before
    # Fetch entries and guide through submenus
    query = f"""SELECT * FROM tasks WHERE {condition}"""
    
    # Execute statement
    cursor.execute(query)
    
    # Fetch results
    results = cursor.fetchall()
    
    # Get headers
    headers = [col[0] for col in cursor.description]
    
    # Format entries for inquirer
    # First create dictionary
    results_dict_list = [dict(zip(headers, result)) for result in results] # Get structure like {a: 1, b:2, c:3} with letters being columns

    # Compute column widths (consider header and all values)
    col_widths = {}
    columns = zip(headers, *results)
    max_col_lengths = [max(list(map(lambda x:len(str(x)), column))) for column in columns]
    col_widths = dict(zip(headers, max_col_lengths))
    
    # Create headers and adjust for column width
    sep = "  |  "
    header_description = sep.join(h.ljust(col_widths[h]) for h in headers)
    header_description = "    " + header_description
    
    # Go through each entry and convert to string
    entries = []
    for row in results_dict_list:
        # Create name string
        choice_description = sep.join(str(row[h]).ljust(col_widths[h]) for h in headers)
        # Append to entries
        entries.append(choice_description)
    
    # Build output string
    output_text = header_description + "\n" + "\n".join(entries)
    
    return output_text


def show_inbox(cursor):
    """
    Executes a query to show tasks in the default project (Inbox).
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
    """
    # Define query
    query = """SELECT * FROM tasks WHERE project_id = 1"""
   
    # Execute statement
    cursor.execute(query)
