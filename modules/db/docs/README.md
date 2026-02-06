# Database Module Organization

This directory contains the reorganized database operations for the task management system. The original monolithic `sqlite_python.py` file has been broken down into smaller, more manageable modules.

## Module Structure

```
db/
├── __init__.py           # Main module entry point, exports all functions
├── database.py           # Database initialization and low-level helpers
├── projects.py           # Project-related operations
├── tasks.py              # Task-related operations
├── subtasks.py           # Subtask-related operations
├── users.py              # User and coin management
├── shop.py               # Shop and reward system
├── display.py            # Data retrieval and display functions
├── operations.py         # Common CRUD operations (update, delete, edit, finish)
├── context_menu.py       # Context menus for different entity types
├── timers.py             # Timer-related operations
└── README.md             # This file
```

## Module Descriptions

### `database.py`
Core database functionality:
- `create_tables()` - Initialize database schema
- `check_tables()` - Verify table contents
- `get_latest_value()` - Retrieve most recent values
- `determine_id()` - Calculate next available ID

### `projects.py`
Project management:
- `add_project()` - Create new projects
- `show_project_tasks()` - Display tasks for a project

### `tasks.py`
Task management:
- `add_task()` - Create new tasks
- `check_subtasks()` - Check if task has subtasks
- `get_reward_value()` - Get task reward amount

### `subtasks.py`
Subtask management:
- `add_subtask()` - Create new subtasks
- `show_subtasks()` - Display subtasks for a task

### `users.py`
User and economy:
- `add_user()` - Create new user
- `get_coin_amount()` - Get user's coin balance
- `update_coin_amount()` - Update coin balance

### `shop.py`
Shop and rewards:
- `add_reward()` - Add purchasable rewards
- `buy_reward()` - Handle reward purchases

### `display.py`
Data presentation:
- `list_entries()` - List database entries
- `display_and_select()` - Interactive selection interface
- `get_entry()` - Fetch specific records
- `get_today()` - Get today's tasks
- `show_inbox()` - Display inbox tasks

### `operations.py`
Common database operations:
- `delete_entry()` - Delete records
- `edit_entry()` - Edit existing records
- `finish_entry()` - Mark entries as complete

### `context_menu.py`
User interface menus:
- `context_menu()` - Display context-specific menus for tasks, projects, and subtasks

### `timers.py`
Timer functionality:
- `popup_timer()` - Create timer windows
- `update_time_spent()` - Track time spent on tasks
- `timer_list` - Global timer list

## Backward Compatibility

The original `sqlite_python.py` file has been converted to a compatibility layer that imports and re-exports all functions from the new `db` module. This means:

- Existing code using `from sqlite_python import *` will continue to work
- No changes required to `main.py`, `gui.py`, or `ai_assistance.py`
- The module can be gradually refactored to use direct imports from `db` submodules

## Usage Examples

### Direct module imports (recommended for new code)
```python
from db.tasks import add_task
from db.users import get_coin_amount
from db.display import list_entries
```

### Backward compatible imports (for existing code)
```python
from sqlite_python import add_task, get_coin_amount, list_entries
# or
from sqlite_python import *
```

### Using the db module directly
```python
from db import add_task, get_coin_amount, list_entries
```

## Benefits of This Organization

1. **Better Code Organization**: Related functions are grouped together
2. **Easier Navigation**: Smaller files are easier to read and understand
3. **Improved Maintainability**: Changes to one area don't affect others
4. **Clear Separation of Concerns**: Each module has a specific purpose
5. **Backward Compatibility**: No breaking changes to existing code
6. **Better Testing**: Smaller modules are easier to unit test
7. **Clearer Dependencies**: Import statements show module relationships

## Migration Guide

To gradually migrate to the new structure:

1. Start by importing specific functions you need:
   ```python
   from db.tasks import add_task
   ```

2. Update one file at a time to use direct imports

3. Eventually remove the `from sqlite_python import *` pattern

4. Once all code is migrated, `sqlite_python.py` can be removed
