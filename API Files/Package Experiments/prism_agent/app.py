# Contents of prism_agent/app.py
from flask import Flask, request
from prism_agent.whatsapp.whatsapp_api import send_whatsapp_message # Import send_whatsapp_message
from prism_agent.groq.groq_api import call_llama # Import call_llama
from prism_agent.db.database import get_db_connection, save_conversation # Import get_db_connection, save_conversation

import argparse
import sys
import time
from mysql.connector import Error
from prism_agent.cli import send_template_cli # Import send_template_cli
from prism_agent.whatsapp.whatsapp_api import send_template # Import send_template
from dotenv import load_dotenv
import os

# Load environment variables from .env file
loaded = load_dotenv(dotenv_path="credentials.env") #or the correct path
print(f"load_dotenv() returned: {loaded}")  # Add this line
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
print(f"Loaded VERIFY_TOKEN: {VERIFY_TOKEN}")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

#VERIFY_TOKEN


# Initialize Flask
app = Flask(__name__)

# Webhook Routes
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    print(f"Webhook verification: mode={request.args.get('hub.mode')}, token={token}, challenge={challenge}")
    if token == VERIFY_TOKEN: # Use Config
        print("Webhook verified successfully")
        return challenge, 200
    else:
        print("Webhook verification failed")
        print(f"Loaded VERIFY_TOKEN: {VERIFY_TOKEN}")
        return "Verification token mismatch", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    # Handle incoming messages from WhatsApp
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
    """Send a template message to a specific phone number."""
    # Endpoint to send a template message
    data = request.json
    phone = data.get("phone")
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    # Endpoint to send a template to all customers associated with a business
    data = request.json
    business_id = data.get("business_id", 1)  # Default to 1 if not provided
    send_template_to_all(business_id) #change the function location
    return "Templates sent to customers", 200

# Main (moved to app.py)
if __name__ == "__main__":
    from prism_agent.cli import send_template_to_all
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
        app.run(host="0.0.0.0", port=8080, debug=True) # Use Config