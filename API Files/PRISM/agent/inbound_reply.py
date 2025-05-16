#Module name: inbound_reply.py
#Location: PRISM/massenging_agent/inbound_reply.py
# Description: This module handles the processing of incoming messages from WhatsApp. It includes functions to fetch dynamic prompts, process messages, and send replies.


from dotenv import load_dotenv
import  os
import requests

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../credentials.env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")




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








