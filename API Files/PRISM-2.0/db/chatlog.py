
from db.connection import get_db_connection

def save_conversation(phone, user_msg, ai_reply):
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO chats (phone, user_msg, ai_reply) VALUES (%s, %s, %s)",
            (phone, user_msg, ai_reply)
        )
        connection.commit()
    except Exception as e:
        print(f"Error saving chat: {e}")
    finally:
        cursor.close()
        connection.close()
