"""
User-related database operations.
"""
from db.database import determine_id


def add_user(cursor, conn):
    """
    Prompts for a name and adds a new user to the database.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
    """
    # Initialize values
    user_name = ""
    coins = 0
    # Create a cursor
    cursor = conn.cursor()
    # Get user input
    while user_name == "":
        user_name = input("What is your name?: ")

    # Determine next id number
    new_id = determine_id(cursor=cursor, table_name="user")
    
    # Execute statement
    cursor.execute("""
        INSERT INTO user(id, name, coins) VALUES(?, ?, ?)
        """, (new_id, user_name, 0))
    print("User has been added!")

    # Commit changes
    conn.commit()


def get_coin_amount(cursor):
    """
    Retrieves the current coin balance for the user.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        
    Returns:
        int: Total coins.
    """
    # Define query
    query="""SELECT coins FROM user WHERE id = 1"""
    # Execute statement
    cursor.execute(query)
    # Fetch result
    coins = cursor.fetchone()[0]

    return coins


def update_coin_amount(cursor, conn, increase_amount: int):
    """
    Updates the user's coin balance.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        increase_amount (int): Amount to add (use negative for deduction).
    """
    # Get current amount
    current_amount = get_coin_amount(cursor)
    
    # Calculate new amount
    new_amount = current_amount + increase_amount
    
    # Define query
    query = f"""UPDATE user SET coins = {new_amount} where id = 1"""
    # Execute command
    cursor.execute(query)
    # Commit changes
    conn.commit()
