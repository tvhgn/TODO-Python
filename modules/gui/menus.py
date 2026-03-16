from ai_assistance import AssistantScreen
from gui.task_screens import TaskScreen
from gui.project_screens import ProjectScreen

import os
import sqlite3
from datetime import datetime, timedelta

from textual import on
from textual.app import App, Screen, ComposeResult
from textual.widgets import Footer, ListView, ListItem, Label, Static
from textual.containers import Vertical

from db.display import get_table

class ToDoApp(App):
    """Contains ListView widgets for the main menu.

    Args:
        App (_type_): _description_
    """
    
    CSS_PATH = os.path.join("css_files", "main_menu.css")
    DB_FILE = os.path.join("data", "database", "todos.db")
    BINDINGS = [("q", "quick_add_task", "Quick Add Task")]
    
    def compose(self) -> ComposeResult:
        """Compose the app's layout."""
  
        with ListView():
            yield ListItem(Label("Assistant"), id="assistant")
            yield ListItem(Label("Today"), id="today")
            yield ListItem(Label("Inbox"), id="inbox")
            yield ListItem(Label("Tasks"), id="tasks")
            yield ListItem(Label("Projects"), id="projects")
            yield ListItem(Label("Shops"), id="shops")
            yield ListItem(Label("Settings"), id="settings")
       
        
        yield Footer()
     
    def on_list_view_selected(self, event=ListView.Selected)-> None:
        """Handle menu selection logic"""
        selected_item = event.item.id
        match selected_item:
            case "assistant":
                with sqlite3.connect(self.DB_FILE) as conn:
                    cursor = conn.cursor()
                    # install and push assistant screen
                    # First check whether screen is already installed, uninstall if so
                    if self.app.is_screen_installed("Assistant"):
                        self.uninstall_screen("Assistant")
                    self.install_screen(AssistantScreen(cursor=cursor), name="Assistant")
                    self.push_screen("Assistant")
            case "today":
                # Get today's date as well as tomorrow's
                today = datetime.today()
                tomorrow = today + timedelta(days=1)
                today = today.strftime('%Y-%m-%d') # Format to YYYY-mm-dd
                tomorrow = tomorrow.strftime('%Y-%m-%d')
                # Define condition
                condition = f"(end_date = {today}) OR (end_date < '{tomorrow}' AND NOT status = 2)" # Get today's tasks, as well as unfinished tasks from before
                # Install screen, but first uninstall if already there.
                if self.app.is_screen_installed("Today"):
                    self.uninstall_screen("Today")
                self.install_screen(TaskScreen(self.DB_FILE, condition), name="Today")
                self.push_screen("Today")
                
            case "tasks":
                # Check if screen is already installed, if so, delete it.
                if self.app.is_screen_installed("Tasks"):
                    self.uninstall_screen("Tasks")
                # Create tasks screen and push to screen
                self.install_screen(TasksMenu(), name="Tasks")
                self.push_screen("Tasks")
            
            case "projects":
                if self.app.is_screen_installed("Projects"):
                    self.uninstall_screen("Projects")
                self.install_screen(ProjectsMenu(), name="Projects")
                self.push_screen("Projects")
                
                
class TasksMenu(Screen):
    CSS_PATH = os.path.join("css_files", "tasks_menu.css")
    DB_FILE = os.path.join("data", "database", "todos.db")
    BINDINGS = [("r", "app.pop_screen", "Return")
            ]
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Tasks")
            with ListView():
                yield ListItem(Label("Pending Tasks"),  id="pending")
                yield ListItem(Label("Completed Tasks"), id="completed")
                yield ListItem(Label("All Tasks"), id="all")
        
        
    def on_list_view_selected(self, event=ListView.Selected)-> None:
        """Handle item selection"""
        selected_item = event.item.id
        
        match selected_item:
            case "pending":
                # Define condition such that only pending tasks are displayed
                condition = "NOT status = 2"
                # install and push screen
                if self.app.is_screen_installed("Pending_Tasks"):
                    self.app.uninstall_screen("Pending_Tasks")
                self.app.install_screen(TaskScreen(self.DB_FILE, condition), name="Pending_Tasks")
                self.app.push_screen("Pending_Tasks")
                
            case "completed":
                # Define condition such that only completed tasks are displayed
                condition = "status = 2"
                # install and push screen
                if self.app.is_screen_installed("Completed_Tasks"):
                    self.app.uninstall_screen("Completed_Tasks")
                self.app.install_screen(TaskScreen(self.DB_FILE, condition), name="Completed_Tasks")
                self.app.push_screen("Completed_Tasks")
                
            case "all":
                # No condition is necessary
                condition = "NULL"
                # Install and push screen
                if self.app.is_screen_installed("All_Tasks"):
                    self.app.uninstall_screen("All_Tasks")
                self.app.install_screen(TaskScreen(self.DB_FILE, condition), name="All_Tasks")
                self.app.push_screen("All_Tasks")
                
                
                
class ProjectsMenu(Screen):
    CSS_PATH = os.path.join("css_files", "tasks_menu.css")
    DB_FILE = os.path.join("data", "database", "todos.db")
    BINDINGS = [("r", "app.pop_screen", "Return")
            ]
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Projects")
            with ListView():
                yield ListItem(Label("Show Pending"),  id="pending")
                yield ListItem(Label("Show Completed"), id="completed")
                yield ListItem(Label("Show All"), id="all")
        
        
    def on_list_view_selected(self, event=ListView.Selected)-> None:
        """Handle item selection"""
        selected_item = event.item.id
        
        match selected_item:
            case "pending":
                # Define condition such that only pending tasks are displayed
                condition = "NOT status = 2"
                # install and push screen
                if self.app.is_screen_installed("Pending_Projects"):
                    self.app.uninstall_screen("Pending_Projects")
                self.app.install_screen(ProjectScreen(self.DB_FILE, condition), name="Pending_Projects")
                self.app.push_screen("Pending_Projects")
                
            case "completed":
                # Define condition such that only completed tasks are displayed
                condition = "status = 2"
                # install and push screen
                if self.app.is_screen_installed("Completed_Projects"):
                    self.app.uninstall_screen("Completed_Projects")
                self.app.install_screen(ProjectScreen(self.DB_FILE, condition), name="Completed_Projects")
                self.app.push_screen("Completed_Projects")
                
            case "all":
                # No condition is necessary
                condition = "NULL"
                # Install and push screen
                if self.app.is_screen_installed("All_Projects"):
                    self.app.uninstall_screen("All_Projects")
                self.app.install_screen(ProjectScreen(self.DB_FILE, condition), name="All_Projects")
                self.app.push_screen("All_Projects")