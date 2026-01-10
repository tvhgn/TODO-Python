from ollama import chat
from datetime import datetime
from InquirerPy import inquirer

from sqlite_python import get_today
from helpers.prompts import continue_prompt

def summarize_today(cursor):
    # Collect today's tasks
    entries = get_today(cursor=cursor)
    # Get today's date
    today = datetime.now()
    today = today.strftime('%Y-%m-%d %H:%M:%S') # Format to YYYY-mm-dd HH-MM-SS
    
    # Build prompt
    prompt = f"""Help me make a plan for today. The current date and time is: {today}.
    Which tasks should I focus on and what should I start with? 
    What can I actually finish today, and what should I postpone? I can work in the evening, but my energy will be less.
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
    continue_prompt()
    

