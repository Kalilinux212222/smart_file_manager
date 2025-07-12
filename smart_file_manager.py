# Import required modules
import os                         # For file system operations
import sys                        # For command-line arguments
import shutil                     # For moving and deleting files
from datetime import datetime     # For working with dates and file timestamps
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

# ------------------ File Object Structure ------------------

# Define a class to hold file information
class Files:
    def __init__(self, name, path, extension, date):
        self.name = name                    # File name without extension
        self.path = path                    # Path to the directory
        self.extension = extension          # File extension (e.g., .txt)
        self.fullname = name + extension    # Full file name with extension
        self.date = date                    # Optional date (not actively used)

# ------------------ File Type Categories ------------------

# Define known file categories and their extensions
FILE_CATEGORIES = {
    'Documents': ['.txt', '.pdf', '.docx', '.xlsx', '.csv'],
    'Audios': ['.mp3', '.wav', '.aac'],
    'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
    'Pictures': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    'Archives': ['.zip', '.rar', '.7z', '.tar'],
    'Executables': ['.exe', '.msi', '.sh'],
    'Scripts': ['.py', '.js', '.bat'],
    'Website_Languages': ['.html', '.css']
}

# ------------------ Utility Functions ------------------

# Ensure directory exists or create it
def folder_check(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Check if the path exists
def ensure_exists(path):
    if not os.path.exists(path):
        print(f"The path '{path}' does not exist.")
        return False
    return True

# Get only subfolders from a path
def list_dirs(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

# ------------------ Back Up System ------------------
# Backup all files before moving them
class RealTimeBackupHandler(FileSystemEventHandler):
    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path

    def on_created(self, event):
        if event.is_directory or 'Backup' in event.src_path:
            return

        backup_files(self.base_path)

def start_realtime_backup(path):
    event_handler = RealTimeBackupHandler(path)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    print("Real-time backup watcher started...")

    # Keep running in a separate thread
    def keep_running():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    threading.Thread(target=keep_running, daemon=True).start()

def backup_files(base_path):
    from datetime import date

    today = date.today().strftime('%Y-%m-%d')
    backup_root = os.path.join(base_path, 'Backup', today)
    folder_check(backup_root)

    files_backed_up = 0
    for foldername, _, filenames in os.walk(base_path):
        # Skip backup folders
        if 'Backup' in foldername:
            continue

        for filename in filenames:
            source_path = os.path.join(foldername, filename)

            # Preserve relative structure
            relative_folder = os.path.relpath(foldername, base_path)
            target_folder = os.path.join(backup_root, relative_folder)
            target_path = os.path.join(target_folder, filename)

            if not os.path.exists(target_path):
                folder_check(target_folder)
                try:
                    shutil.copy2(source_path, target_path)

                    files_backed_up += 1
                except Exception as e:
                    print(f"Failed to backup {source_path}: {e}")

    if files_backed_up == 0:
        print("All files already backed up. No new files found.")

# ------------------ Core File Management ------------------

# Create new files if they don't already exist
def store_files(events):
    for event in events:
        full_path = os.path.join(event.path, event.fullname)
        if os.path.exists(full_path):
            print(f'{event.fullname} already exists!')
        else:
            with open(full_path, 'w') as f:
                pass  # Create an empty file
            print(f'{event.fullname} stored successfully.')

# List all files in directories and standalone files
def get_file(path):
    dirs = os.listdir(path)
    if not dirs:
        print('No directories found.')
        return
    for d in dirs:
        full_path = os.path.join(path, d)
        if os.path.isdir(full_path):
            for f in os.listdir(full_path):
                print(f'Found: Filename - {f} in directory - {d}')
        else:
            print(f'Found: File - {d} (not in a directory)')

# List only directories from the path
def get_folder(path):
    for d in list_dirs(path):
        print(f'Found: Folder - {d}')

# List all files from a specific folder
def get_file_exact_folder(path, directory):
    for d in list_dirs(path):
        if directory.lower() == d.lower():
            for f in os.listdir(os.path.join(path, d)):
                print(f'Found: Filename - {f}')
            return
    print(f"Directory '{directory}' not found.")

# Delete a folder and all its contents
def delete_folder(path, folder_name):
    for d in list_dirs(path):
        if folder_name.lower() == d.lower():
            full_path = os.path.join(path, d)
            try:
                shutil.rmtree(full_path)
                print(f"Deleted folder and all contents: {d}")
                return
            except Exception as e:
                print(f"Failed to delete folder {d}: {e}")
                return
    print(f"Folder '{folder_name}' not found in {path}")

# Delete files between two dates inside a specific folder
def old_file_clean(path, time_str_s, time_str_e, directory):
    try:
        cutoff_start = datetime.strptime(time_str_s, '%Y-%m-%d').timestamp()
        cutoff_end = datetime.strptime(time_str_e, '%Y-%m-%d').timestamp()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD")
        return

    full_path = os.path.join(path, directory)
    if not ensure_exists(full_path):
        return

    files_deleted = 0
    print(f"Checking files in: {full_path}")

    for file in os.listdir(full_path):
        file_path = os.path.join(full_path, file)
        if os.path.isfile(file_path):
            try:
                mod_time = os.path.getmtime(file_path)
                if cutoff_start < mod_time < cutoff_end:
                    os.remove(file_path)
                    print(f"Deleted: {file}")
                    files_deleted += 1
            except Exception as e:
                print(f"Skipped {file}: {e}")

    print(f"Total files deleted: {files_deleted}" if files_deleted else "No files deleted.")

# Delete folders that are empty
def delete_if_empty(path):
    for d in list_dirs(path):
        full_path = os.path.join(path, d)
        if not os.listdir(full_path):  # Folder is empty
            delete_folder(path, d)

# ------------------ File Sorting and Moving ------------------

# Categorize files based on their extensions
def detect_files(files):
    categorized = {category: [] for category in FILE_CATEGORIES}
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                categorized[category].append(file)
                break
    return categorized

# List all files (not folders) from the given path
def analysis_file_from_folder(path):
    try:
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []

# Move files into their category folder (Documents, Videos, etc.)
def move_files(file_list, folder, base_path):
    target_folder = os.path.join(base_path, folder)
    os.makedirs(target_folder, exist_ok=True)
    for file in file_list:
        try:
            shutil.move(file, target_folder)
        except Exception as e:
            print(f"Failed to move {file}: {e}")

# Detect file categories and move them automatically
def move_file_alternate_destination(path):
    try:
        files = analysis_file_from_folder(path)
        categorized = detect_files(files)
        for category, file_list in categorized.items():
            move_files(file_list, category, path)
        return True
    except Exception as ex:
        print(f"Error moving files: {ex}")
        return False

# ------------------ Main Program Loop ------------------

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else './Desktop'  # Use given path or default to Desktop
    folder_check(path)  # Make sure the base folder exists
    backup_files(path)
    start_realtime_backup(path)

    while True:
        print('\n===== Smart File Manager =====')
        print('1. Store File')
        print('2. List All Files with Directory')
        print('3. List Directories')
        print('4. List Files From Exact Directory')
        print('5. Remove Files in Exact Folder by Date')
        print('6. Remove Folder')
        print('7. Delete Empty Folders')
        print('8. Exit')

        choice = input("Choose an option (1-8): ").strip()

        if choice == '1':
            file_name = input('Enter file name: ')
            extension = '.' + input('Enter file extension (e.g., txt): ').strip().lower()
            events = [Files(file_name, path, extension, '')]
            store_files(events)
            if move_file_alternate_destination(path):
                print('Files successfully sorted.')

        elif choice == '2':
            get_file(path)

        elif choice == '3':
            get_folder(path)

        elif choice == '4':
            directory = input('Enter directory name: ')
            get_file_exact_folder(path, directory)

        elif choice == '5':
            directory = input('Enter directory name: ')
            time_str_s = input('Enter start date (YYYY-MM-DD): ')
            time_str_e = input('Enter end date (YYYY-MM-DD): ')
            old_file_clean(path, time_str_s, time_str_e, directory)

        elif choice == '6':
            folder = input('Enter folder name to delete: ')
            delete_folder(path, folder)

        elif choice == '7':
            delete_if_empty(path)
            print(detect_files(path))

        elif choice == '8':
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please choose between 1-8.")

# ------------------ Entry Point ------------------

if __name__ == '__main__':
    main()
