import os
import shutil
import sqlite3

def copy_imessage_database():
    """
    Copy the iMessage database to the specified directory or current working directory.
    """
    source_path = os.path.expanduser("~/Library/Messages/chat.db")
        
    destination_path = os.path.join(os.getcwd(), "imessages.db")

    if not os.path.exists(source_path):
        print(f"Error: iMessage database not found at {source_path}")
        return None

    try:
        shutil.copy2(source_path, destination_path)
        print(f"Successfully copied iMessage database to {destination_path}")

        conn = sqlite3.connect(destination_path)
        conn.close()
        print("Successfully verified the copied database.")
        
        return destination_path
    except PermissionError:
        print("Error: Permission denied. Make sure you have the necessary permissions to access the iMessage database.")
    except sqlite3.Error as e:
        print(f"Error: Unable to verify the copied database. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None

def get_database_structure(db_path: str = 'imessages.db') -> dict:
    """
    Get the tables and structure of the database.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        db_structure = {}

        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            db_structure[table_name] = [
                {
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': col[3],
                    'dflt_value': col[4],
                    'pk': col[5]
                }
                for col in columns
            ]

        conn.close()
        return db_structure

    except sqlite3.Error as e:
        print(f"Error: Unable to get database structure. {e}")
        return None

if __name__ == "__main__":
    print(get_database_structure())
