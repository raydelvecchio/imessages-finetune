import os
import shutil
import sqlite3
import json

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

def get_finetune_data(db_path: str = 'imessages.db', test_mode: bool = False) -> list:
    """
    Execute SQL query to get non-group chat messages and format them for fine-tuning.
    If test_mode is True, only process the first non-group chat.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        base_query = """
        SELECT 
            CASE WHEN m.is_from_me = 1 THEN 'Me' ELSE h.id END as sender,
            m.text as message,
            c.chat_identifier,
            m.date as message_date
        FROM 
            message m
        JOIN 
            chat_message_join cmj ON cmj.message_id = m.ROWID
        JOIN 
            chat c ON c.ROWID = cmj.chat_id
        LEFT JOIN
            handle h ON h.ROWID = m.handle_id
        WHERE 
            c.chat_identifier NOT LIKE 'chat%'  -- Exclude group chats
        """

        if test_mode:
            query = f"""
            WITH FirstChat AS (
                SELECT chat_identifier
                FROM ({base_query})
                GROUP BY chat_identifier
                LIMIT 1
            )
            {base_query}
            AND c.chat_identifier = (SELECT chat_identifier FROM FirstChat)
            ORDER BY m.date
            """
        else:
            query = f"{base_query} ORDER BY c.chat_identifier, m.date"

        cursor.execute(query)
        results = cursor.fetchall()

        # Format the messages for fine-tuning
        finetune_data = []
        current_chat = None
        user_messages = []
        assistant_messages = []

        for sender, message, chat_identifier, _ in results:
            if message is None:
                continue  # Skip messages with None content

            if current_chat != chat_identifier:
                # Add the previous conversation if it exists
                if user_messages and assistant_messages:
                    finetune_data.append({
                        "role": "User",
                        "content": "<NEWMESSAGE>".join(user_messages)
                    })
                    finetune_data.append({
                        "role": "Assistant",
                        "content": "<NEWMESSAGE>".join(assistant_messages)
                    })
                # Reset for new chat
                current_chat = chat_identifier
                user_messages = []
                assistant_messages = []

            if sender != "Me":
                if assistant_messages:
                    finetune_data.append({
                        "role": "Assistant",
                        "content": "<NEWMESSAGE>".join(assistant_messages)
                    })
                    assistant_messages = []
                user_messages.append(message)
            else:
                if user_messages:
                    finetune_data.append({
                        "role": "User",
                        "content": "<NEWMESSAGE>".join(user_messages)
                    })
                    user_messages = []
                assistant_messages.append(message)

        # Add the last conversation if it exists
        if user_messages:
            finetune_data.append({
                "role": "User",
                "content": "<NEWMESSAGE>".join(user_messages)
            })
        if assistant_messages:
            finetune_data.append({
                "role": "Assistant",
                "content": "<NEWMESSAGE>".join(assistant_messages)
            })

        conn.close()
        return finetune_data

    except sqlite3.Error as e:
        print(f"Error: Unable to execute query. {e}")
        return None

if __name__ == "__main__":
    finetune_data = get_finetune_data(test_mode=True)
    if finetune_data:
        print(json.dumps(finetune_data, indent=2))
