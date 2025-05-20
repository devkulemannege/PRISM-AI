# Contents of prism_agent/db/database.py
import mysql.connector
from mysql.connector import Error
from prism_agent.config import Config  # Import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def save_conversation(phone, user_msg, ai_reply):
    connection = get_db_connection()
    if connection is None:
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO chats (phone, user_msg, ai_reply) VALUES (%s, %s, %s)",
            (phone, user_msg, ai_reply)
        )
        connection.commit()
    except Error as e:
        print(f"Error saving conversation: {e}")
    finally:
        cursor.close()
        connection.close()