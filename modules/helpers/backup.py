# Import the following modules
import shutil
from datetime import date
import os


# Function for performing the
# backup of the files and folders
def create_backup(src_file_name, 
                dst_file_name=None,
                src_dir='', 
                dst_dir=''):
    try:
      
          # Extract the today's date
        today = date.today()  
        date_format = today.strftime("%d_%b_%Y_")

        # Make the source directory,
        # where we wanna backup our files
        src_dir = os.path.join(src_dir, src_file_name)
        # print("source directory:", src_dir)

        # If user not enter any source file,
        # then just give the error message...
        if not src_file_name:
            print("Please give atleast the Source File Name")
            exit()

        try:
          
            # If user provides all the inputs
            if src_file_name and dst_file_name and src_dir and dst_dir:
                src_dir = src_dir+src_file_name
                dst_dir = dst_dir+dst_file_name
                
            # When User Enter Either 
            # 'None' or empty String ('')
            elif dst_file_name is None or not dst_file_name:
                dst_file_name = src_file_name
                dst_dir = dst_dir+date_format+dst_file_name
                
            # When user Enter an empty
            # string with one or more spaces (' ')
            elif dst_file_name.isspace():
                dst_file_name = src_file_name
                dst_dir = dst_dir+date_format+dst_file_name
                
            # When user Enter an a
            # name for the backup copy
            else:
                dst_dir = dst_dir+dst_file_name
                
            # print("dest directory:", dst_dir)

            # Now, just copy the files
            # from source to destination
            shutil.copy2(src_dir, dst_dir)

            # print("Backup Successful!")
        except FileNotFoundError:
            print("File does not exists!,\
            please give the complete path")
    
    # When we need to backup the folders only...
    except PermissionError:  
        dst_dir = dst_dir+date_format+dst_file_name
        
        # Copy the whole folder
        # from source to destination
        shutil.copytree(src_file_name, dst_dir)
