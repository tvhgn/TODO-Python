import sqlite3
import os
from datetime import datetime

from db.database import determine_id
from db.display import get_entry
from db.transformations import get_project_id, get_project_name

class Task:
    """
    An object to contain information relating to a task entry. Also has methods to convert values and to update an external SQLite3 database.
    """
    def __init__(self, task_id:int=None):
        # Set path to database file
        self.db = os.path.join("data", "database", "todos.db")
        
        # If the task is new (no task_id given), determine new task id from database file.
        if task_id is None:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                self.id = determine_id(cursor=cursor, table_name="tasks")
            # Get today's date
            today = datetime.today()
            today = today.strftime('%Y-%m-%d')
            # Initialize data values
            self.data = {
                "id":self.id, "name":"new task", "project_id":1, "begin_date":today, 
                "end_date":today, "reward":0, "duration":0, "time_spent":0, 
                "status":0, "priority":0}
            # Get the headers
            self.headers = list(self.data.keys())
        else:
            # Set id attribute
            self.id = task_id
            # Get data from database file
            self.values, self.headers = get_entry(db_file=self.db, table="tasks", id_num=self.id)
            # turn into a dictionary
            self.data = {h:self.values[i] for i, h in enumerate(self.headers)}
        
        
        
        # Mapping of values
        self.priority_dict = {
            0: "low",
            1: "medium",
            2: "high"
        }

        self.reward_dict = {
            0: "low",
            1: "medium",
            2: "high"
        }

        self.status_dict = {
            0: "not started",
            1: "in progress",
            2: "done"
        }
        
        
        # Build separate data attribute with renamed values
        self.data_recoded = self.data.copy()
        for header, value in self.data_recoded.items():
            # print(f"Header: {header}, value:{value}")
            self.data_recoded[header] = self._convert_values(header, value)
        
    def __repr__(self):
        return str(self.data_recoded)
    
    def _convert_values(self, header, original_value):
        """
        Convert values between integer codes and their string representations for specific task fields.
        
        This method handles bidirectional conversion between integer codes stored in the database
        and their human-readable string equivalents for fields that use predefined mappings.
        
        Args:
            header (str): The field name to convert. Supported fields are:
                - "reward": Converts between reward levels (0="low", 1="medium", 2="high")
                - "priority": Converts between priority levels (0="low", 1="medium", 2="high")
                - "status": Converts between status values (0="not started", 1="in progress", 2="done")
                - Any other header: Returns the original value unchanged
            original_value: The value to convert. Can be an integer code or string representation.
        
        Returns:
            The converted value. If original_value is an integer, returns the corresponding string.
            If original_value is a string, returns the corresponding integer key.
            For "status" field, "NULL" is converted to an empty string.
            For unsupported headers, returns the original value unchanged.
        """
        # Correspondence between headers and mapping dictionaries
        mappings = {
                "status":self.status_dict,
                "priority":self.priority_dict,
                "reward":self.reward_dict
            }
        # Get dictionary based on header, if relevant
        if header in mappings:
            value_mapping = mappings[header]
            
            # Recode values using value_mapping dictionary
            if isinstance(original_value, int):
                new_value = value_mapping[original_value]
            elif original_value == "NULL":
                new_value = ""
            elif original_value == "":
                new_value = "NULL"
            else:
                new_value = [key for key, val in value_mapping.items() if val == original_value][0]
        elif header == "project_id":
            if isinstance(original_value, int):
                new_value = get_project_name(self.db, project_id=original_value)
            else:
                new_value = get_project_id(self.db, project_name=original_value)
        else:
            new_value = original_value
            
                
        return new_value
    
    def add_task_to_db(self):
        """
        Add task to the remote SQLite3 database using the objects data attribute.
        """
                
        # Define substrings for sqlite execution statement
        header_string = ", ".join(self.headers)
        values_string = ", ".join(["?"] * len(self.headers))
        data_values = [self.data[k] for k in self.data]
        
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            
            # Add to DB
            cursor.execute(f"""INSERT INTO tasks({header_string}) VALUES({values_string});""",
                           data_values) 
            # Commit changes
            conn.commit()
    
    def update_db(self, header, new_value):
        """
        Update the remote database with the given column header and value. Also updates the objects values.
        """
        # Update objects attributes
        self.data[header] = new_value
        self.data_recoded[header] = self._convert_values(header, new_value)
        # update the database
        with sqlite3.connect(self.db) as conn:
            # create cursor
            cursor = conn.cursor()
            # Define the query
            if "name" in header or "date" in header:
                new_value = f"'{new_value}'"
            query = f"""UPDATE tasks SET {header} = {new_value} WHERE id = {self.id};"""
            # Execute query
            cursor.execute(query)
            # Commit changes
            conn.commit()
           
# class Project:
    
# # # Test code
# # new_task = Task()
# # print(new_task)