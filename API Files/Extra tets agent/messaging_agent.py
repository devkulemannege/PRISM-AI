from dotenv import load_dotenv
import os
import requests
import mysql.connector
from mysql.connector import Error
from chatlog_table import addRow
from connect_db import get_db_connection
import time
import argparse
import sys
from flask import Flask, request
from llm_chain import initialize_llm_chain, call_llm_with_chain

# Load environment variables
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
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

# WhatsApp - Send Free-form Message
def send_whatsapp_message(phone, msg):
    """Send a free-form message to a WhatsApp number."""
    if not isinstance(msg, str):
        raise ValueError(f"Expected string for msg, got {type(msg)}: {msg}")
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

def send_template_to_all(campaign_id):
    """This function is to send template messages to all the customers in a campaign"""
    connection, cursor = get_db_connection()
    if connection is None:
        return

    try:
        # Check if the campaign exists and fetch its details
        cursor.execute("SELECT * FROM campaign WHERE campaignId = %s", (campaign_id,))
        business_row = cursor.fetchone()
        if not business_row:
            print(f"No campaign found with campaignId = {campaign_id}, aborting...")
            return

        campaign_name = business_row[2]
        template_name = business_row[4]
        prompt = business_row[3]
        template_params = business_row[5].split(',') if business_row[3] else ['customer_name', 'campaign_name']
        print(f"Business details: campaignId={campaign_id}, name={campaign_name}, template={template_name}, prompt={prompt}, params={template_params}")

        if not template_name:
            print(f"No template specified for campaignId = {campaign_id}, aborting...")
            return

        # Fetch all customers associated with the campaign
        cursor.execute("""
            SELECT c.customerId, c.fName, c.mobileNo
            FROM customer c
            JOIN customer_campaign cb ON c.customerId = cb.customerId
            WHERE cb.campaignId = %s
        """, (campaign_id,))
        customers = cursor.fetchall()
        print(f"Found {len(customers)} customers associated with campaignId={campaign_id}")

        if not customers:
            print(f"No customers found for campaignId = {campaign_id}, aborting...")
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
            if customer_phone.startswith('0'):
               customer_phone = customer_phone[1:]
            customer_phone = f"+94{customer_phone}"
            print(f"Formatted customer phone: {customer_phone}")

            # Prepare dynamic parameters based on template_parameters
            parameters = []
            if 'customer_name' in template_params:
                parameters.append({"type": "text", "text": customer_name})
            if 'business_name' in template_params:
                parameters.append({"type": "text", "text": campaign_name})
            if 'description' in template_params or 'product_name' in template_params:
                cursor.execute("SELECT offer, campaignName FROM campaign WHERE campaignId = %s LIMIT 1", (campaign_id,))
                product_row = cursor.fetchone()
                if product_row and 'description' in template_params:
                    parameters.append({"type": "text", "text": product_row[0]})
                if product_row and 'product_name' in template_params:
                    parameters.append({"type": "text", "text": product_row[1]})

            print(f"Sending template {template_name} to {customer_phone} with parameters {parameters}")
            print(f"Template expects {len(parameters)} parameters: {parameters}")
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

                    # Keep original sender for WhatsApp API, format for database
                    db_sender = sender
                    if db_sender.startswith('94') and len(db_sender) == 11:
                        db_sender = '0' + db_sender[2:]
                    print(f"Formatted sender for database: {db_sender}")

                    # Fetch customerId and campaign details
                    connection, cursor = get_db_connection()
                    customer_id = None
                    campaign_id = None
                    if connection and cursor:
                        try:
                            cursor.execute("SELECT customerId FROM customer WHERE mobileNo = %s", (db_sender,))
                            customer_row = cursor.fetchone()
                            if customer_row:
                                customer_id = customer_row[0]
                                cursor.execute("""
                                    SELECT b.campaignId
                                    FROM campaign b
                                    JOIN customer_campaign cb ON b.campaignId = cb.campaignId
                                    WHERE cb.customerId = %s LIMIT 1
                                """, (customer_id,))
                                campaign_row = cursor.fetchone()
                                if campaign_row:
                                    campaign_id = campaign_row[0]
                        except Error as e:
                            print(f"Database error fetching customer/campaign: {e}")
                        finally:
                            cursor.close()
                            connection.close()

                    # Initialize LangChain conversation
                    print(f"Initialized LangChain conversation for customerId={customer_id}, sender={db_sender}")
                    runnable, customer_name, campaign_name = initialize_llm_chain(customer_id, db_sender)
                    
                    # Generate AI reply using LangChain
                    ai_reply = call_llm_with_chain(runnable, text, customer_name, campaign_name, session_id=customer_id)
                    print(f"AI reply before sending: {repr(ai_reply)}, type: {type(ai_reply)}")  # Debug the reply
                    if not isinstance(ai_reply, str):
                        raise ValueError(f"Expected string for ai_reply, got {type(ai_reply)}: {ai_reply}")
                    send_whatsapp_message(sender, ai_reply)

                    # Save conversation
                    if customer_id and campaign_id:
                        addRow(db_sender, campaign_id, ai_reply, text)
                    else:
                        print("Skipping saving conversation due to missing customer_id or campaign_id")
    except Exception as e:
        print(f"Webhook Error: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace
    return "OK", 200

# API Endpoints
@app.route("/send-template", methods=["POST"])
def send_template_route():
    """Send a template message to a WhatsApp number."""
    data = request.json
    phone = data.get("phone")
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    data = request.json
    campaign_id = data.get("campaign_id", 1)
    send_template_to_all(campaign_id)
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
        help="Send a template to all customers associated with a campaign (e.g., --send-to-all 1 or --send-to-all 2)"
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
        campaign_id = int(args.send_to_all[0])
        send_template_to_all(campaign_id)
    else:
        print("Starting Flask app for inbound messaging on port 8080...")
        app.run(host="0.0.0.0", port=8080, debug=True)