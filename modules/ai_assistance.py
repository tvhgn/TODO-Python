from ollama import chat
from textual.app import ComposeResult, Screen
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label, Footer, Static, Button

from datetime import datetime
import os

from sqlite_python import get_today, list_entries
from helpers.prompts import continue_and_clear
# from gui.helper_apps import TextDisplayer


class AIResponse(Static):
    """A widget to display the AI response as a text stream."""
    
    response = reactive("")
    
    def watch_response(self, response):
        """Called when response attribute changes"""
        self.update(response)
    
    def summarize_today(self, cursor):
        """
        Retrieves today's entries from the SQLite database. Uses local ollama model for AI generated advice.

        Args:
            cursor (sqlite3.Cursor): The cursor object to interact with the SQLite database.

        Returns:
            Sets the class attribute 'response' as the AI response.
        """
        # Let the user know you are busy
        self.response = "Loading response, please wait..."
        
        # Collect today's tasks
        entries, _ = list_entries(cursor=cursor,
                            table="tasks",
                            condition="NOT status = 2", # Exclude finished entries
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
        
        # Store response
        current_response = ""
        for chunk in stream:
            current_response += chunk['message']['content']
            self.response = current_response

    

class AssistantScreen(Screen):
    BINDINGS = [("r", "app.pop_screen", "Return")]
    CSS_PATH = os.path.join("gui","css_files", "assistant_screen.css")
    
    def __init__(self, cursor):
        super().__init__()
        self._cursor = cursor  # Store cursor for use after mount
        
    
    def compose(self) -> ComposeResult:
        yield AIResponse()
        yield HorizontalGroup(Button(label="Generate Today's Plan", id="summary"))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "summary":
            self.generate_summary()
                               
    def generate_summary(self):
        """Generate a summary of the current day's tasks."""
        self.query_one(AIResponse).summarize_today(self._cursor)
    




