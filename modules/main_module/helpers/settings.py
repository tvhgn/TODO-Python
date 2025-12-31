import json
import os

def generate_settings_file():
    # Initialize settings file
    settings = {
        "active_user_id": 1, 
        "reward_mapping": {"0": 5, "1": 10, "2": 30},
        "cost_mapping": {"0": 40, "1":80, "2":160}# {reward_value: coin_amount}
    }
    
    # Set details of settings file which we are gonna generate
    settings_path = os.path.join("data", "settings", "settings.json")
    settings_dir = os.path.dirname(settings_path)
    # Create directory if not there yet
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)
    
    # Generate the file
    with open(settings_path, 'w', encoding="utf-8") as f:
        json.dump(settings, f)
        
def read_settings_file():
    # Set the path
    settings_path = os.path.join("data", "settings", "settings.json")
    
    # Read the file
    with open(settings_path, 'r', encoding="utf-8") as f:
        settings = json.load(f)
        
    return settings