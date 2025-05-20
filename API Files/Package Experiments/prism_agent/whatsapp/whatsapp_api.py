# Contents of prism_agent/whatsapp/whatsapp_api.py
import requests
from prism_agent.config import Config  # Import Config

def send_whatsapp_message(phone, msg):
    """Send a free-form message to a WhatsApp number."""
    url = f"https://graph.facebook.com/v19.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
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

def send_template(phone, template_name, parameters=None):
    """Send a template message to a WhatsApp number."""
    url = f"https://graph.facebook.com/v19.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
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