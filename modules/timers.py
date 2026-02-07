import time
import threading
from datetime import timedelta

from tkinter import Tk
from tkinter.ttk import Label, Button, Frame
import tkinter.font as tkFont


class Timer:
    def __init__(self, task_name, task_id):
        self.start_time = None
        self.task_name = task_name
        self.task_id = task_id
        self.stop_flag = threading.Event()
        self.elapsed_time = 0
        self.formatted_time = "00:00:00"
        # Threading
        self.timer_thread = threading.Thread(
            target=self._timer_loop
        )
        
    
    def _format_time(self, seconds):
        """Convert seconds to HH:MM:SS format using timedelta"""
        td = timedelta(seconds=int(seconds))
        # Extract hours, minutes, seconds from timedelta
        hours, remainder = divmod(int(td.total_seconds()), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"    
        
    def _timer_loop(self):
        # Start time
        self.start_time = time.time()
        # Continue looping until stop flag is set
        while not self.stop_flag.is_set():
            # Calculate passed time
            self.elapsed_time = time.time() - self.start_time
            # Format it as HH:MM:SS
            self.formatted_time = self._format_time(self.elapsed_time)
            #print(f"\r{self.task_name} - elapsed: {self.formatted_time}", end="", flush=True)
            time.sleep(1)
        
    def start_timer(self):
        """Start a background timer"""
        # start thread if not already running
        if self.timer_thread.is_alive():
            print("Timer is already running!")
        else:
            self.stop_flag.clear() # Reset flag just to be sure
            self.timer_thread.start() # Start thread
        
        
    def stop_timer(self):
        """Stops the background timer. Checks if thread is running and acts accordingly."""
        if self.timer_thread.is_alive():
            self.stop_flag.set() # Set flag to True
            self.timer_thread.join()  # Wait for thread to finish
        else:
            print("Timer was not yet running!")
        
class TimerWindow:
    def __init__(self, task_timer:Timer, cursor, conn):
        self.task_timer = task_timer
        self.cursor = cursor
        self.conn = conn
        self.root = Tk()
        self.dimensions = "400x100"
        
        # Create window and set attributes
        self.root.geometry(self.dimensions) # Set dimensions
        self.root.title(f"Timer: {task_timer.task_name}") #Add title
        # Create custom font
        custom_font = tkFont.Font(family="Arial", size=20)
        
        # Add central label - expand to center vertically
        self.lbl_elapsed = Label(self.root, text="00:00:00", font=custom_font)
        self.lbl_elapsed.pack(expand=True)
        
        # Create a frame for buttons to keep them together
        button_frame = Frame(self.root)
        button_frame.pack(expand=True)
        
        # Add buttons horizontally in the frame
        self.btn_start = Button(button_frame, text="Start", command=self.start_timer)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = Button(button_frame, text="Stop", command=self.stop_timer)
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_close = Button(button_frame, text="Exit", command=self.destroy_timer)
        self.btn_close.pack(side="left", padx=5)
        
        # Update label initially
        self.update_label()
        
        # Execute tkinter window 
        self.root.mainloop()
        
    def start_timer(self):
        """Start the internal timer and return the elapsed time"""
        self.task_timer.start_timer()
    
    def stop_timer(self):
        """Stop the internal timer and update the database with elapsed time for the given task if timer thread was running."""
        self.task_timer.stop_timer()
        # Update the database
        self.update_db()
        
    def update_label(self):
        """Periodically update the label with current elapsed time"""
        # Update label text from timer's formatted_time
        self.lbl_elapsed.config(text=self.task_timer.formatted_time)
        # Schedule this method to run again after 1000ms
        self.root.after(200, self.update_label)
        
    def destroy_timer(self):
        """Stops the timer if running, closes the window and destroys Window object"""
        # Stop the timer but check if thread was running
        if self.task_timer.timer_thread.is_alive():
            self.task_timer.stop_timer()
        # Close the window
        self.root.destroy()
    
    
    def update_db(self):
        """Add elapsed_time (seconds) to the task's time_spent. Uses parameterized queries."""
        # Get timer attributes
        task_id = self.task_timer.task_id
        elapsed_time = self.task_timer.elapsed_time
        # Get the time already spent on the given task
        self.cursor.execute(f"SELECT time_spent FROM tasks WHERE id = {task_id}")
        row = self.cursor.fetchone()
        prev_time = row[0] if row is not None and row[0] is not None else 0
        # Calculate new amount of time spent and update database
        new_time = prev_time + int(elapsed_time)
        self.cursor.execute("UPDATE tasks SET time_spent = ? WHERE id = ?", (new_time, task_id))
        self.conn.commit()