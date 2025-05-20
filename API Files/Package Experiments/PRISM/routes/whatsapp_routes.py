#Module name: whatsapp_routes.py
#Location: PRISM/routes/whatsapp_routes.py
# Description: This module contains the routes for handling WhatsApp messages and webhooks. It includes verification of the webhook, processing incoming messages, and sending template messages.


import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from agent.inbound_reply import send_whatsapp_message 
from agent.outbound_temp import send_template, send_template_to_all
from agent.call_llama import call_llama
from db.chatlog_table import addRow
from db.connection import get_db_connection
from mysql.connector import Error

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../credentials.env"))
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify():
    """""this function verifies the webhook by checking the token provided by WhatsApp. If the token matches, it returns the challenge code."""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

@whatsapp_bp.route("/webhook", methods=["POST"])
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
                    customerMsg = message["from"]
                    text = message.get("text", {}).get("body", "No text")
                    print(f"Received message from {customerMsg}: {text}")

                    # Fetch the dynamic prompt based on the customerMsg's phone number
                    connection = get_db_connection()
                    prompt = "You are a friendly and concise WhatsApp bot. Respond in a helpful and conversational tone as a real sales agent, keeping replies under 100 words."
                    business_name = None
                    customer_name = None

                    if connection:
                        cursor = connection.cursor()
                        try:
                            # Look up customerId based on mobileNo
                            cursor.execute("SELECT customerId, fName FROM customer WHERE mobileNo = %s", (customerMsg,))
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
                                print("No customer found for customerMsg, using default prompt")
                        except Error as e:
                            print(f"Database error fetching prompt: {e}")
                        finally:
                            cursor.close()
                            connection.close()
                    else:
                        print("Database connection failed, using default prompt")

                    # Generate AI reply with dynamic prompt
                    agentMsg = call_llama(text, prompt)#calls the LLM with the text and prompt
                    send_whatsapp_message(customerMsg, agentMsg)#calls the function to send the message
                    addRow(customerMsg, text, agentMsg)#calls the function to add the row to the chatlog table
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

# API Endpoints
@whatsapp_bp.route("/send-template", methods=["POST"])
def send_template_route():
    """Send a template message to a specific phone number."""
    # Endpoint to send a template message
    data = request.json
    phone = data.get("phone")
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@whatsapp_bp.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    # Endpoint to send a template to all customers associated with a business
    data = request.json
    business_id = data.get("business_id", 1)  # Default to 1 if not provided
    send_template_to_all(business_id)
    return "Templates sent to customers", 200