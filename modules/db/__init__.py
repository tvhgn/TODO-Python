"""
Database module - Organized database operations for the task management system.

This module provides a clean interface to all database operations by importing
and re-exporting functions from specialized submodules.
"""

# Database initialization and helpers
from db.database import (
    create_tables,
    check_tables,
    get_latest_value,
    determine_id
)

# Project operations
from db.projects import (
    add_project,
    show_project_tasks
)

# Task operations
from db.tasks import (
    add_task,
    check_subtasks,
    get_reward_value
)

# Subtask operations
from db.subtasks import (
    add_subtask,
    show_subtasks
)

# User operations
from db.users import (
    add_user,
    get_coin_amount,
    update_coin_amount
)

# Shop operations
from db.shop import (
    add_reward,
    buy_reward
)

# Display and retrieval operations
from db.display import (
    list_entries,
    display_and_select,
    get_entry,
    get_today,
    show_inbox
)

# Common operations (update, delete, edit)
from db.operations import (
    delete_entry,
    edit_entry,
    finish_entry
)

# Context menus
from db.context_menu import (
    context_menu
)

# Timer operations
from db.timers import (
    popup_timer,
    update_time_spent,
    timer_list
)

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
