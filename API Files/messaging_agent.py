from dotenv import load_dotenv
import os
import requests
import mysql.connector
from mysql.connector import Error
import time

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "credentials.env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print(f"Looking for .env at: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'credentials.env'))}")
print(f"Loaded ACCESS_TOKEN: {ACCESS_TOKEN}")
print(f"Loaded PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def send_template(phone, name):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "test_template",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name}
                    ]
                }
            ]
        }
    }
    print(f"Sending request with headers: {headers}")
    print(f"Sending request with payload: {payload}")
    res = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp API Response for {phone}: {res.json()}")
    return res.json()

def send_template_to_all():
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT Contact, Name FROM businesses")
        contacts = cursor.fetchall()

        for contact_row in contacts:
            phone = contact_row[0]
            name = contact_row[1]

            # Format phone number to international format (+94, remove leading 0)
            if not phone.startswith('+'):
                if phone.startswith('0'):
                    phone = phone[1:]
                phone = f"+94{phone}"

            print(f"Sending template to {phone} with name {name}")
            send_template(phone, name)
            time.sleep(1)  # Delay to avoid rate limits
    except Error as e:
        print(f"Error querying database: {e}")
    finally:
        cursor.close()
        connection.close()

def send_template_cli(phone, name):
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    print(f"Sending request with headers: {headers}")
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "test_template",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name}
                    ]
                }
            ]
        }
    }
    print(f"Sending request with payload: {payload}")
    res = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp API Response: {res.json()}")
    return res.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4 and sys.argv[1] == "--send-template":
        phone = sys.argv[2]
        name = sys.argv[3]
        send_template_cli(phone, name)
    elif len(sys.argv) == 2 and sys.argv[1] == "--send-to-all":
        # Trigger sending to all numbers only with this command
        send_template_to_all()
    else:
        # Default: Start Flask app for inbound messaging
        from flask import Flask, request
        app = Flask(__name__)

        @app.route("/webhook", methods=["GET", "POST"])
        def webhook():
            if request.method == "GET":
                return request.args.get("hub.challenge")
            elif request.method == "POST":
                # Handle incoming messages (your existing logic)
                return "OK", 200

        @app.route("/send-template", methods=["POST"])
        def send_template_route():
            data = request.json
            phone = data.get("phone")
            name = data.get("name", "User")
            send_template(phone, name)
            return "Template sent", 200

        print("Starting Flask app for inbound messaging...")
        app.run(host="0.0.0.0", port=5000, debug=True)