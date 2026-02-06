from ollama import chat
from datetime import datetime
from InquirerPy import inquirer

from sqlite_python import get_today, list_entries
from helpers.prompts import continue_and_clear

def summarize_today(cursor):
    """
    Retrieves and displays today's entries from the SQLite database. Uses local ollama model for AI generated advice.

    Args:
        cursor (sqlite3.Cursor): The cursor object to interact with the SQLite database.

    Returns:
        None
    """
    # Write your function implementation here...
    # Collect today's tasks
    #entries = get_today(cursor=cursor)
    entries, _ = list_entries(cursor=cursor,
                           table="tasks",
                           condition="NOT status = 2",
                           get_entries=True,
                           print_table=False)

    # Get today's date
    today = datetime.now()
    today = today.strftime('%Y-%m-%d %H:%M:%S') # Format to YYYY-mm-dd HH-MM-SS
    
    # Build prompt
    prompt = f"""Help me make a plan for today. The current date and time is: {today}.
    Which tasks should I focus on and what should I start with? 
    What can I actually finish today, and what should I postpone? I can work in the evening, but my energy will be less, so I prefer not to.
    The reward amount is a function of how valuable task completion is and the amount of time it takes.\n
    These are my tasks:\n {entries}.
    \n Note that I cannot reply to you, so don't prompt for further interaction."""
    
    # # Feed prompt to Henk
    stream = chat(
    model='Henk',
    messages=[{'role': 'user', 'content': prompt}],
    stream=True,
    )
    
    # Print response
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        
    # Wait for response
    continue_and_clear()
    


def propose_subtasks(cursor, conn, task_id):
    """
    Proposes subtasks for a given task using the local ollama model and creates them.

    Args:
        cursor (sqlite3.Cursor): The cursor object to interact with the SQLite database.
        conn (sqlite3.Connection): The connection object to interact with the SQLite database.
        task_id (int): The ID of the task for which to propose subtasks.
    """
    # Retrieve the task details
    task = get_entry(cursor=cursor, table="tasks", id_num=task_id)
    if not task:
        print("Task not found.")
        return

    task_name, task_priority, task_project_id, task_status, task_begin_date, task_end_date, task_reward, task_duration, task_time_spent = task[1:]

    # Build the prompt for the ollama model
    prompt = f"""I have a task: "{task_name}". 
    Please break this down into smaller, actionable subtasks. 
    For each subtask, suggest a brief name and an estimated duration in minutes.
    Present the output as a JSON list of objects, where each object has a "name" and "duration" key.
    For example:
    [
        {{"name": "Subtask 1", "duration": 30}},
        {{"name": "Subtask 2", "duration": 60}}
    ]
    """

    # Call the ollama chat model
    stream = chat(
        model='Henk',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )

    # Process the response and extract subtasks
    subtasks_data = ""
    for chunk in stream:
        subtasks_data += chunk['message']['content']

    try:
        import json
        subtasks = json.loads(subtasks_data)
    except json.JSONDecodeError:
        print("Failed to parse subtasks from model response.")
        print(f"Model response: {subtasks_data}")
        return

    # Create subtasks in the database
    if subtasks:
        for subtask_info in subtasks:
            subtask_name = subtask_info.get("name")
            subtask_duration = subtask_info.get("duration")

            if subtask_name and subtask_duration:
                add_subtask(cursor=cursor, conn=conn, task_id=task_id) # This will prompt the user for input, need to modify add_subtask to accept parameters
                # The current add_subtask prompts interactively. To automate, we'd need to modify it or create a new function.
                # For now, let's assume we'll manually create them after the suggestion or modify add_subtask.

                # --- Placeholder for automated subtask creation ---
                # To automate, add_subtask would need to accept name and duration as arguments,
                # and we would call it like:
                # add_subtask_automated(cursor, conn, task_id, subtask_name, subtask_duration)
                # Let's simulate adding here by directly executing SQL for demonstration
                new_subtask_id = determine_id(cursor=cursor, table_name="subtasks")
                end_date = task_end_date # Assuming subtasks inherit end date for simplicity
                status = 0 # Default status
                cursor.execute("""
                    INSERT INTO subtasks(id, name, task_id, status, end_date, duration) 
                    VALUES(?, ?, ?, ?, ?, ?);
                    """, (new_subtask_id, subtask_name, task_id, status, end_date, subtask_duration))
                print(f"Created subtask: '{subtask_name}' with duration {subtask_duration} minutes.")
            else:
                print(f"Skipping invalid subtask entry: {subtask_info}")
        conn.commit()
        print(f"Successfully created {len(subtasks)} subtasks for task '{task_name}'.")
    else:
        print("The model did not propose any subtasks.")

    # Wait for user confirmation to clear screen
    continue_and_clear()
