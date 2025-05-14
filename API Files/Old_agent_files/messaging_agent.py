from dotenv import load_dotenv
import os
import requests
import mysql.connector
from mysql.connector import Error
import time
import argparse
import sys
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
def call_llama(user_input, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",#in here its the role of the system set the prompt
                "content": prompt#In here its the 
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

def send_template_to_all(business_id):
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        # Check if the business exists and fetch its details
        cursor.execute("SELECT name, template, prompt, template_parameters FROM business WHERE businessId = %s", (business_id,))
        business_row = cursor.fetchone()
        if not business_row:
            print(f"No business found with businessId = {business_id}, aborting...")
            return

        business_name = business_row[0]
        template_name = business_row[1]
        prompt = business_row[2]
        template_params = business_row[3].split(',') if business_row[3] else ['customer_name', 'business_name']
        print(f"Business details: businessId={business_id}, name={business_name}, template={template_name}, prompt={prompt}, params={template_params}")

        if not template_name:
            print(f"No template specified for businessId = {business_id}, aborting...")
            return

        # Fetch all customers associated with the business
        cursor.execute("""
            SELECT c.customerId, c.fName, c.mobileNo
            FROM customer c
            JOIN customer_business cb ON c.customerId = cb.customerId
            WHERE cb.businessId = %s
        """, (business_id,))
        customers = cursor.fetchall()
        print(f"Found {len(customers)} customers associated with businessId={business_id}")

        if not customers:
            print(f"No customers found for businessId = {business_id}, aborting...")
            return

        # For each customer, send the template message
        for customer_row in customers:
            customer_id = customer_row[0]
            customer_name = customer_row[1]
            customer_phone = customer_row[2]
            print(f"Processing customer: customerId={customer_id}, name={customer_name}, phone={customer_phone}")

            if not customer_phone:
                print(f"Customer with customerId = {customer_id} has no phone number, skipping...")
                continue

            # Format the customer's phone number
            if not customer_phone.startswith('+'):
                if customer_phone.startswith('0'):
                    customer_phone = customer_phone[1:]
                customer_phone = f"+94{customer_phone}"
            print(f"Formatted customer phone: {customer_phone}")

            # Prepare dynamic parameters based on template_parameters
            parameters = []
            if 'customer_name' in template_params:
                parameters.append({"type": "text", "text": customer_name})
            if 'business_name' in template_params:
                parameters.append({"type": "text", "text": business_name})
            if 'description' in template_params or 'product_name' in template_params:
                cursor.execute("SELECT description, name FROM product WHERE businessId = %s LIMIT 1", (business_id,))
                product_row = cursor.fetchone()
                if product_row and 'description' in template_params:
                    parameters.append({"type": "text", "text": product_row[0]})
                if product_row and 'product_name' in template_params:
                    parameters.append({"type": "text", "text": product_row[1]})

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
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    send_template(phone, template_name, parameters)
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

                    # Fetch the dynamic prompt based on the sender's phone number
                    connection = get_db_connection()
                    prompt = "You are a friendly and concise WhatsApp bot. Respond in a helpful and conversational tone as a real sales agent, keeping replies under 100 words."
                    business_name = None
                    customer_name = None

                    if connection:
                        cursor = connection.cursor()
                        try:
                            # Look up customerId based on mobileNo
                            cursor.execute("SELECT customerId, fName FROM customer WHERE mobileNo = %s", (sender,))
                            customer_row = cursor.fetchone()
                            if customer_row:
                                customer_id, customer_name = customer_row
                                # Find associated businessId and prompt
                                cursor.execute("""
                                    SELECT b.businessId, b.name, b.prompt
                                    FROM business b
                                    JOIN customer_business cb ON b.businessId = cb.businessId
                                    WHERE cb.customerId = %s LIMIT 1
                                """, (customer_id,))
                                business_row = cursor.fetchone()
                                if business_row:
                                    business_id, business_name, prompt = business_row
                                    print(f"Found businessId={business_id}, business_name={business_name} with prompt: {prompt}")
                                    # Format the prompt with customer_name and business_name
                                    prompt = prompt.format(customer_name=customer_name, business_name=business_name)
                                else:
                                    print("No business associated with customer, using default prompt")
                            else:
                                print("No customer found for sender, using default prompt")
                        except Error as e:
                            print(f"Database error fetching prompt: {e}")
                        finally:
                            cursor.close()
                            connection.close()
                    else:
                        print("Database connection failed, using default prompt")

                    # Generate AI reply with dynamic prompt
                    ai_reply = call_llama(text, prompt)
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
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    data = request.json
    business_id = data.get("business_id", 1)  # Default to 1 if not provided
    send_template_to_all(business_id)
    return "Templates sent to customers", 200

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
        metavar=("BUSINESS_ID"),
        help="Send a template to all customers associated with a business (e.g., --send-to-all 1 or --send-to-all 2)"
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
        business_id = int(args.send_to_all[0])  # Convert to integer
        send_template_to_all(business_id)
    else:
        print("Starting Flask app for inbound messaging on port 8080...")
        app.run(host="0.0.0.0", port=8080, debug=True)