# Prism AI WhatsApp Bot using Meta Cloud API + LLaMA 4 (Groq)

# ✅ Requirements:
# - Flask (or FastAPI)
# - requests
# - MariaDB connector (mariadb)





from flask import Flask, request
import requests
import mariadb
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="test_agent/credentials.env")  # Optional: path if not in root



# Configurations
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

#  Initialize Flask
app = Flask(__name__)

#  MariaDB Connection
conn = mariadb.connect(
    user="root",
    password="",
    host="localhost",
    database="prismai"
)
cursor = conn.cursor()

def save_conversation(phone, user_msg, ai_reply):
    cursor.execute(
        "INSERT INTO chats (phone, user_msg, ai_reply) VALUES (?, ?, ?)",
        (phone, user_msg, ai_reply)
    )
    conn.commit()

#  WhatsApp - Send Message (Free-form)
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
    print(f"WhatsApp API Response: {res.json()}")  # Debug print

#  Groq - Call LLaMA 4 Model

def call_llama(user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",  # Updated model
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

#To veirify the webhook
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

# Webhook to Handle Incoming Messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        phone = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        ai_reply = call_llama(message)
        send_whatsapp_message(phone, ai_reply)
        save_conversation(phone, message, ai_reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

# ✅ Endpoint to Trigger Outbound Template Message
@app.route("/send-template", methods=["POST"])
def send_template():
    phone = request.json.get("phone")
    name = request.json.get("name")
    link = request.json.get("link")
    
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
            "name": "promo_offer",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name},
                        {"type": "text", "text": link}
                    ]
                }
            ]
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.text, res.status_code

# ✅ Main
if __name__ == "__main__":
    app.run(port=8080, debug=False)

