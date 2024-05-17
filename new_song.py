import os
import shutil
import tkinter as tk
from tkinter import filedialog

def rename_file(old_path, new_name, target_dir):
    try:
        new_path = os.path.join(target_dir, new_name)
        os.replace(old_path, new_path)
        print(f"File '{old_path}' renamed to '{new_path}'.")
    except FileNotFoundError:
        print(f"File '{old_path}' not found.")

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"Folder '{folder_path}' not found.")

def main():
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Select file to play
    file_to_rename = filedialog.askopenfilename(title="Select File to play")
    if file_to_rename:
        target_dir = os.path.dirname(os.path.abspath(__file__))  # Get directory of the script
        new_file_name = "beatmap.osz"
        rename_file(file_to_rename, new_file_name, target_dir)

    # Delete folder
    folder_to_delete = os.path.join(target_dir, "beatmaps")
    delete_folder(folder_to_delete)

if __name__ == "__main__":
    main()