"""
Timer-related database operations.
"""
from timers import Timer, TimerWindow

# Global variable declaration
timer_list = []


def popup_timer(cursor, conn, checks):
    """
    Creates Timer and Timewindow objects, which results in a pop-up timer. 
    """
    # Fetch global timer_list variable
    global timer_list
    # Exit function if no selection made
    if not checks or len(checks) != 1:
        return
    # Get the task_name
    task_id = checks[0]
    cursor.execute(f"SELECT name FROM tasks WHERE id = {task_id}")
    row = cursor.fetchone()
    task_name = row[0] if row else f"Task {task_id}"
    
    # Create Timer object
    task_timer = Timer(task_name=task_name, task_id=task_id)
    # Create Timer Window
    popup_timer = TimerWindow(task_timer=task_timer, cursor=cursor, conn=conn)

        
def update_time_spent(cursor, conn, table, timer_object):
    """Add elapsed_time (seconds) to the task's time_spent. Uses parameterized queries."""
    # Get timer attributes
    task_id = timer_object.task_id
    elapsed_time = timer_object.elapsed_time
    # Get the time already spent on the given task
    cursor.execute(f"SELECT time_spent FROM tasks WHERE id = {task_id}")
    row = cursor.fetchone()
    prev_time = row[0] if row is not None and row[0] is not None else 0
    # Calculate new amount of time spent and update database
    new_time = prev_time + int(elapsed_time)
    cursor.execute("UPDATE tasks SET time_spent = ? WHERE id = ?", (new_time, task_id))
    conn.commit()
