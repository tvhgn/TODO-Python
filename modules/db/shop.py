"""
Shop and reward system database operations.
"""
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

from db.database import determine_id
from db.users import get_coin_amount, update_coin_amount
from helpers.settings import read_settings_file


def add_reward(cursor, conn):
    """
    Adds a new purchasable reward to the shop.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
    """
    # To build query we need some information
    # Load the settings file
    settings = read_settings_file()
    # Dictionary to define cost value, {reward_value: coin_amount}
    cost_dict = settings['cost_mapping']
    reward_description = inquirer.text(message="What is the reward? ").execute()
    reward_cost = inquirer.text(message="How big is the reward? [0; small, 1;medium, 2; big]",
                                validate=NumberValidator()).execute()
    # Calculate cost
    transformed_cost = cost_dict[reward_cost]
    
    # Get id number
    new_id = determine_id(cursor=cursor, table_name="shop")
        
    # Execute statement and save changes
    cursor.execute(
        """INSERT INTO shop(id, reward, cost) VALUES(?,?,?)""", 
        (new_id, reward_description, transformed_cost)
        )
    conn.commit()


def buy_reward(cursor, conn, checks):   
    """
    Handles the purchase of shop rewards using user coins.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        conn (sqlite3.Connection): The database connection.
        checks (list): List of reward IDs to purchase.
    """
    # Calculate cost based on selection
    cost_total = 0
    for check in checks:
        query = f"""SELECT cost FROM shop WHERE id = {check}"""
        cursor.execute(query)
        cost_total += cursor.fetchone()[0]
    # Get coin balance
    balance = get_coin_amount(cursor=cursor)
    
    # Check if balance is sufficient and act accordingly
    if balance < cost_total:
        print(f"Your balance ({balance} Coins) is not sufficient. Complete more tasks!")
    else:
        # Ask for confirmation
        confirm = inquirer.confirm(message=f"This reward costs {cost_total} Coins. Please confirm your purchase [Y/N]:").execute()
        if confirm:
            # Deduct balance
            update_coin_amount(cursor=cursor, conn=conn, increase_amount=-cost_total)
            if len(checks) > 1:
                # Show new balance and print congratulatory message
                print(f"Enjoy your rewards! Your new balance is {balance-cost_total} Coins.")
            else:
                # Show new balance and print congratulatory message
                print(f"Enjoy your reward! Your new balance is {balance-cost_total} Coins.")
            
            # TODO: store transaction in history
