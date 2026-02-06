"""
Backward compatibility layer for sqlite_python module.

This file maintains backward compatibility by importing all functions from the new
organized db module structure. Existing code using 'from sqlite_python import *'
will continue to work without modification.
"""

# Import everything from the new organized db module
from db import *

# Re-export for backward compatibility
__all__ = [
    # Database
    'create_tables',
    'check_tables',
    'get_latest_value',
    'determine_id',
    # Projects
    'add_project',
    'show_project_tasks',
    # Tasks
    'add_task',
    'check_subtasks',
    'get_reward_value',
    # Subtasks
    'add_subtask',
    'show_subtasks',
    # Users
    'add_user',
    'get_coin_amount',
    'update_coin_amount',
    # Shop
    'add_reward',
    'buy_reward',
    # Display
    'list_entries',
    'display_and_select',
    'get_entry',
    'get_today',
    'show_inbox',
    # Operations
    'delete_entry',
    'edit_entry',
    'finish_entry',
    # Context
    'context_menu',
    # Timers
    'popup_timer',
    'update_time_spent',
    'timer_list'
]
