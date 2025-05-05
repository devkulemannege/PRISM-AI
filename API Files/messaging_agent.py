from dotenv import load_dotenv
import os
import requests
import mysql.connector
from mysql.connector import Error
import time
import argparse
from flask import Flask, request

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "credentials.env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print(f"Looking for .env at: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'credentials.env'))}")
print(f"Loaded ACCESS_TOKEN: {ACCESS_TOKEN}")
print(f"Loaded PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

# Initialize Flask
app = Flask(__name__)

# MariaDB Connection
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

def save_conversation(phone, user_msg, ai_reply):
    connection = get_db_connection()
    if connection is None:
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO chats (phone, user_msg, ai_reply) VALUES (?, ?, ?)",
            (phone, user_msg, ai_reply)
        )
        connection.commit()
    except Error as e:
        print(f"Error saving conversation: {e}")
    finally:
        cursor.close()
        connection.close()

# WhatsApp - Send Free-form Message
def send_whatsapp_message(phone, msg):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": msg}
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp API Response (free-form): {res.json()}")
    return res.json()

# WhatsApp - Send Template Message
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

# Groq - Call LLaMA 4 Model
def call_llama(user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are Prismai Test Agent, a friendly and concise WhatsApp bot. Respond to user messages in a helpful and conversational tone as a real sales agent, keeping replies under 100 words. If you don’t understand the message, say 'Sorry, I didn’t understand. Can you please rephrase?' For example: User: 'Hello' -> Bot: 'Hi! How can I assist you today?' User: 'What’s the weather like?' -> Bot: 'I can’t check the weather right now, but I can help with other questions! What else would you like to know?'"
            },
            {"role": "user", "content": user_input}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        response_json = res.json()
        print(f"Groq API Response: {response_json}")
        if 'choices' not in response_json:
            print(f"Groq API Error: {response_json.get('error', 'Unknown error')}")
            return "Sorry, I couldn't process your request right now. Please try again later."
        return response_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API Request Failed: {e}")
        return "Sorry, I couldn't process your request right now. Please try again later."

# Send Template to All
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

# CLI to Send Template Message
def send_template_cli(phone, name):
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    send_template(phone, name)
    return None

# Webhook Routes
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    print(f"Webhook verification: mode={request.args.get('hub.mode')}, token={token}, challenge={challenge}")
    if token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200
    else:
        print("Webhook verification failed")
        return "Verification token mismatch", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Incoming webhook data: {data}")
    try:
        if "entry" in data and len(data["entry"]) > 0:
            entry = data["entry"][0]
            if "changes" in entry and len(entry["changes"]) > 0:
                change = entry["changes"][0]
                if "value" in change and "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    sender = message["from"]
                    text = message.get("text", {}).get("body", "No text")
                    print(f"Received message from {sender}: {text}")

                    # Process with Grok and send reply
                    ai_reply = call_llama(text)
                    send_whatsapp_message(sender, ai_reply)
                    save_conversation(sender, text, ai_reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

# API Endpoints
@app.route("/send-template", methods=["POST"])
def send_template_route():
    data = request.json
    phone = data.get("phone")
    name = data.get("name", "User")
    send_template(phone, name)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    send_template_to_all()
    return "Templates sent to all numbers", 200

# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prism AI WhatsApp Bot")
    parser.add_argument("--send-template", nargs=2, metavar=("PHONE", "NAME"), help="Send a template message to a phone number with a name (e.g., --send-template +94787555063 Thinal)")
    parser.add_argument("--send-to-all", action="store_true", help="Send templates to all numbers in the businesses table")
    args = parser.parse_args()

    if args.send_template:
        phone, name = args.send_template
        send_template_cli(phone, name)
    elif args.send_to_all:
        send_template_to_all()
    else:
        print("Starting Flask app for inbound messaging on port 8080...")
        app.run(host="0.0.0.0", port=8080, debug=True)