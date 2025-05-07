
from dotenv import load_dotenv # Load environment variables from .env file
import os # For loading environment variables
import requests # For making HTTP requests
import mysql.connector 
from mysql.connector import Error 
import time 
import argparse # For command-line argument parsing
import sys 
from flask import Flask, request # For creating a Flask web application

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
    """Create a connection to the MariaDB database."""
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
    """Save the conversation to the database."""
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

# WhatsApp - Send Free-form Message
def send_whatsapp_message(phone, msg):
    """Send a free-form message to a WhatsApp number."""
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
def send_template(phone, template_name, parameters=None):
    """Send a template message to a WhatsApp number.""" 
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    if parameters is None:
        parameters = []
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": parameters
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
    """Call the Groq API and get a response from the LLaMA model by training it with a prompt."""
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
def send_template_to_all(template_name):
    """Send a template message to all numbers in the business table."""
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        # Fetch the customer with customerId = 1 (name and phone number)
        cursor.execute("SELECT fName, mobileNo FROM customer WHERE customerId = 1")
        customer_row = cursor.fetchone()
        if not customer_row:
            print("No customer found with customerId = 1, aborting...")
            return

        customer_name = customer_row[0] if customer_row else "Unknown"
        customer_phone = customer_row[1] if customer_row else None
        print(f"Customer details: customerId=1, name={customer_name}, phone={customer_phone}")

        if not customer_phone:
            print("Customer with customerId = 1 has no phone number, aborting...")
            return

        # Format the customer's phone number
        if not customer_phone.startswith('+'):
            if customer_phone.startswith('0'):
                customer_phone = customer_phone[1:]
            customer_phone = f"+94{customer_phone}"
        print(f"Formatted customer phone: {customer_phone}")

        # Fetch only the business with businessId = 1
        cursor.execute("SELECT businessId, name FROM business WHERE businessId = 1")
        business_row = cursor.fetchone()
        if not business_row:
            print("No business found with businessId = 1, aborting...")
            return

        business_id, business_name = business_row
        print(f"Processing business: businessId={business_id}, name={business_name}")

        # Fetch all products for businessId = 1
        print(f"Querying products for businessId={business_id}")
        cursor.execute("SELECT name, description FROM product WHERE businessId = %s", (business_id,))
        product_rows = cursor.fetchall()
        print(f"Found {len(product_rows)} products for businessId={business_id}")

        if not product_rows:
            print(f"No products found for businessId={business_id}, aborting...")
            return

        # Send a message for each product to the customer's phone
        for product_row in product_rows:
            product_name = product_row[0] if product_row else "Unknown Product"
            product_description = product_row[1] if product_row else "No description"
            print(f"Product details: name={product_name}, description={product_description}")

            parameters = [
                {"type": "text", "text": customer_name},
                {"type": "text", "text": business_name},
                {"type": "text", "text": product_description},
                {"type": "text", "text": product_name}
            ]

            print(f"Sending template {template_name} to {customer_phone} with parameters {parameters}")
            send_template(customer_phone, template_name, parameters)
            time.sleep(1)
    except Error as e:
        print(f"Error querying database: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

# CLI to Send Template Message
def send_template_cli(phone, template_name, parameters):
    """Send a template message to a phone number from the CLI."""
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    send_template(phone, template_name, parameters)
    return None

# Webhook Routes
@app.route('/webhook', methods=['GET'])
def verify():
    """Verify the webhook with Facebook."""
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
    """Handle incoming webhook messages from WhatsApp."""
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

                    ai_reply = call_llama(text)
                    send_whatsapp_message(sender, ai_reply)
                    save_conversation(sender, text, ai_reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

# API Endpoints
@app.route("/send-template", methods=["POST"])
def send_template_route():
    """Send a template message to a specific phone number."""
    data = request.json
    phone = data.get("phone")
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    """Send a template message to all numbers in the business table."""
    data = request.json
    template_name = data.get("template_name", "retail_template")
    send_template_to_all(template_name)
    return "Templates sent to all numbers", 200

# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prism AI WhatsApp Bot")
    parser.add_argument(
        "--send-template",
        nargs=2,
        metavar=("PHONE", "TEMPLATE_NAME"),
        help="Send a template message to a phone number (e.g., --send-template +94787555063 retail_template Janith AdoguaLtd '20% off deals in weekends' Bread)"
    )
    parser.add_argument(
        "params",
        nargs='*',
        help="Parameters for the template (e.g., Janith AdoguaLtd '20% off deals in weekends' Bread)"
    )
    parser.add_argument(
        "--send-to-all",
        nargs=1,
        metavar="TEMPLATE_NAME",
        help="Send a template to all numbers in the business table (e.g., --send-to-all retail_template)"
    )
    args = parser.parse_args()

    if args.send_template:
        phone, template_name = args.send_template
        params = args.params
        if template_name == "retail_template" and len(params) != 4:
            print("Error: retail_template requires exactly 4 parameters (e.g., Janith AdoguaLtd '20% off deals in weekends' Bread)")
            sys.exit(1)
        parameters = [{"type": "text", "text": param} for param in params]
        send_template_cli(phone, template_name, parameters)
    elif args.send_to_all:
        template_name = args.send_to_all[0]
        send_template_to_all(template_name)
    else:
        print("Starting Flask app for inbound messaging on port 8080...")
        app.run(host="0.0.0.0", port=8080, debug=True)