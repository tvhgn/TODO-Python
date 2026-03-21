import os
import sqlite3
from datetime import datetime

from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, Input, Static, OptionList
from textual.app import Screen, ComposeResult

from db.display import get_table
from db.objects import Task
from db.database import determine_id
from db.transformations import get_project_id, get_project_name, transform_value

class TaskScreen(Screen):
    BINDINGS = [("r", "app.pop_screen", "Return"),
                ("escape", "exit_input", "Exit Input"),
                ("c", "complete_task", "Complete Selected Task"),
                ("a", "add_task","Add Task"),
                ("d", "delete_task", "Delete Task")]
    CSS_PATH = os.path.join("css_files", "task_screen.css")
    # Reverse flag
    reverse_flag = False
    
    def __init__(self, db_file, condition=None):
        super().__init__()
        self.DB_FILE = db_file
        self.condition = condition
    
    def compose(self) -> ComposeResult:
        # Get projects
        projects, headers = get_table(self.DB_FILE, table="projects")
        
        # Place widgets
        yield DataTable()
        yield Input(placeholder="Enter new value...")
        yield OptionList(*[project[headers.index("name")] for project in projects], id="project_list")
        yield OptionList(
            "low",
            "medium",
            "high",
            id="priority_list"
        )
        yield OptionList(
            "low",
            "medium",
            "high",
            id="reward"
        )
        yield OptionList(
            "not started",
            "in progress",
            "done",
            id="status"
        )
        
        # Development code
        # yield Static("Nothing happening yet...")
        
        yield Footer()
        
    def get_data(self) -> None:
        """
        Retrieves data from the remote database and formats it to make it more readable.
        """
        # get table
        self.results, self.headers = get_table(self.DB_FILE, "tasks", self.condition)
        # Transform values
        project_id_idx = self.headers.index("project_id")
        reward_idx = self.headers.index("reward")
        priority_idx = self.headers.index("priority")
        status_idx = self.headers.index("status")
        for i, result in enumerate(self.results):
            # project name
            self.results[i][project_id_idx] = get_project_name(self.DB_FILE, result[project_id_idx]) # transform to project_name
            # reward
            self.results[i][reward_idx] = transform_value(self.DB_FILE, result[reward_idx], category="reward")
            # priority
            self.results[i][priority_idx] = transform_value(self.DB_FILE, result[priority_idx], category="priority")
            # status
            self.results[i][status_idx] = transform_value(self.DB_FILE, result[status_idx], category="status")    
        
    def on_mount(self) -> None:
        # Get data from the remote database formatted for readability.
        self.get_data()
                    
        # Add columns and rows to the textual table widget
        table = self.query_one(DataTable)
        table.add_columns(*self.headers)
        table.add_rows(self.results)  
        
    def on_data_table_cell_selected(self, event=DataTable.CellSelected):
        """Prompt user to update the selected cell by making the input widget visible. Also remembers the cell coordinate"""
        # Get header label of selected cell
        header_idx = event.coordinate.column
        header_label = self.headers[header_idx]
        # If header is project_id present optionlist instead of input
        if header_label == "project_id":
            option_list = self.query_one("#project_list", OptionList)
            option_list.add_class("prompted")
            option_list.focus()
        elif header_label == "priority":
            option_list = self.query_one("#priority_list", OptionList)
            option_list.add_class("prompted")
            option_list.focus()
        elif header_label == "reward":
            option_list = self.query_one("#reward", OptionList)
            option_list.add_class("prompted")
            option_list.focus()
        elif header_label == "status":
            option_list = self.query_one("#status", OptionList)
            option_list.add_class("prompted")
            option_list.focus()
        else:
            # First make the input visible.
            input_widget = self.query_one(Input)
            if "prompted" not in input_widget.classes:
                input_widget.add_class("prompted")
                input_widget.focus()
        # store current coordinate
        self.current_coordinate = event.coordinate
        
        
    def on_input_submitted(self, event=Input.Submitted):
        """When user submits an input, update the cell corresponding to self.current_coordinate with the new value."""
        new_value = event.value
        # Update the datatable
        datatable = self.query_one(DataTable)
        datatable.update_cell_at(self.current_coordinate, new_value)
        
        # Update the sql database
        coordinate = (self.current_coordinate.row, self.current_coordinate.column)
        self.update_db_at_cell(coordinate, new_value) 
    
        # Upon exit, make widget invisible again
        input_widget = self.query_one(Input)
        input_widget.remove_class("prompted")
        
        # Empty the value
        input_widget.clear()
        
    def on_option_list_option_selected(self, event=OptionList.OptionSelected):
        """When user selects an option from the option list, update the cell corresponding to self.current_coordinate with the new value."""
        selected_option = event.option_list
        new_value = event.option.prompt
        
        # Update the datatable
        datatable = self.query_one(DataTable)
        datatable.update_cell_at(self.current_coordinate, new_value)

        # # Update the sql database
        # Transform new_value to db-appropriate value
        header = self.headers[self.current_coordinate.column]
        if header == "project_id":
            transformed_value = get_project_id(self.DB_FILE, project_name=new_value)
        else:
            transformed_value = transform_value(self.DB_FILE, original_value=new_value, category=header)
        
        # # Development code
        # text = self.query_one(Static)
        # text.update(f"transformed value = {transformed_value}, type = {type(transformed_value)}, header = {header}")
        
        # Then update db
        coordinate = (self.current_coordinate.row, self.current_coordinate.column)
        self.update_db_at_cell(coordinate, transformed_value)

        # Upon exit, make widget invisible again
        selected_option.remove_class("prompted")

        
    def on_data_table_header_selected(self, event=DataTable.HeaderSelected):
        """When header is selected, sort the rows by values in the respective column. Click again to reverse sorting"""
        # Get the label of the clicked header
        header_to_sort = event.column_index
        datatable = self.query_one(DataTable)

        # Attempt to sort numerically if possible
        try:
            # Create a list of tuples with (value, original_row_index)
            sortable_data = []
            for row_index, row in enumerate(datatable.rows):
                cell_value = row[header_to_sort]
                # Try to cast to integer, if it fails, use a placeholder that sorts last
                try:
                    sortable_data.append((int(cell_value), row_index))
                except ValueError:
                    sortable_data.append((float('inf'), row_index)) # Use infinity for non-integer values

            # Sort the data
            sortable_data.sort(key=lambda item: item[0], reverse=self.reverse_flag)

            # Reorder the rows in the DataTable based on the sorted data
            new_rows = [datatable.rows[original_index] for _, original_index in sortable_data]
            datatable.clear()
            datatable.add_rows(new_rows)

        except Exception as e:
            # Handle cases where sorting might fail unexpectedly
            text_widget = self.query_one(Static)
            text_widget.update(f"Could not sort: {e}")

        # Update reverse flag, so that on the next click order is reversed
        self.reverse_flag = not self.reverse_flag
        
    def action_exit_input(self) -> None:
        """Exit input widget if activated"""
        input_widget = self.query_one(Input)
        if "prompted" in input_widget.classes:
            input_widget.remove_class("prompted")
            input_widget.clear()
            self.current_coordinate = None
            
    def action_complete_task(self) -> None:
        """Complete highlighted task if activated"""
        # Get highlighted task from the datatable
        datatable = self.query_one(DataTable)
        highlighted_task_row = datatable.cursor_row
        
        # Update the datatable
        coordinate_to_update = (highlighted_task_row, self.headers.index("status")) # Get coordinate of status column and highlighted row
        datatable.update_cell_at(coordinate_to_update, "done") # finish the task
        
        # Reflect the changes to the db
        self.update_db_at_cell(coordinate_to_update, 2)
        
    def action_add_task(self) -> None:
        """Adds new entry to datatable which user needs to fill in using the input widget"""
        # get table from database to make sure latest changes are included
        # self.results, self.headers = get_table(self.DB_FILE, "tasks", self.condition)
        self.get_data()
        
        # Create task object
        new_task = Task()
        new_row = new_task.data_recoded # Returns dictionary containing task information.
        new_row = [new_row[k] for k in self.headers] # transform to list of values using the order from self.headers
        self.results.insert(0, new_row) # insert empty entry on the top
        
        # Rebuild datatable with empty task at the top
        datatable = self.query_one(DataTable)  
        datatable.clear()
        
        # Add columns and rows to the textual table widget
        # datatable.add_columns(*self.headers)
        datatable.add_rows(self.results)  
        # Set highlighted cell to name column of new task
        datatable.move_cursor(row=0, column=self.headers.index("name"))
        # Set coordinate to name column of new task
        self.current_coordinate = Coordinate(row=0, column=self.headers.index("name"))
        
        # add the new task to the database
        new_task.add_task_to_db()
        
        # Show input widget for user to fill in task information.
        input_widget = self.query_one(Input)
        input_widget.add_class("prompted")
        input_widget.focus()
        
        
    def action_delete_task(self) -> None:
        """
        Deletes the highlighted cell after confirmation.
        """
        # Get the coordinate of the highlighted cell
        datatable = self.query_one(DataTable)
        row_idx = datatable.cursor_row
        # Get the task id
        id_idx = self.headers.index("id")
        task_id = self.results[row_idx][id_idx]
        # show confirmation screen
        
        # Delete the task from the datatable
        with sqlite3.connect(self.DB_FILE) as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM tasks WHERE id={task_id}"
            cursor.execute(query)
            conn.commit()
        # Rebuild the datatable
        self.get_data() # Retrieve up-to-date data
        datatable.clear()
        datatable.add_columns(*self.headers)
        datatable.add_rows(self.results) 
        
        
    
    def update_db_at_cell(self, coordinate: tuple[int, int], new_value: str) -> None:
        """
        Update a cell in the database at the specified coordinate.

        Args:
            coordinate (tuple[int, int]): A tuple containing the row and column indices of the cell to be updated.
            new_value (str): The new value to be written to the cell.

        Notes:
            This method assumes that the coordinate is valid and the data types match.
        """
        # Figure out the header and row id corresponding to the coordinate
        data_row, data_column = coordinate
        header = self.headers[data_column]
        # Create task object from task id
        id_idx = self.headers.index("id")
        task_id = self.results[data_row][id_idx]
        selected_task = Task(task_id=task_id)
        # Update database and task object
        selected_task.update_db(header=header, new_value=new_value)
        
            
    def check_subtasks(self):
        pass
            

    