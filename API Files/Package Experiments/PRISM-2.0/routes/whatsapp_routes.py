
from flask import Blueprint, request, jsonify
from config import VERIFY_TOKEN
from db.chatlog import save_conversation
from services.groq_llm import call_llama
from services.whatsapp_api import send_whatsapp_message, send_template

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        entry = data['entry'][0]
        message = entry['changes'][0]['value']['messages'][0]
        sender = message['from']
        text = message.get('text', {}).get('body', '')
        ai_reply = call_llama(text)
        send_whatsapp_message(sender, ai_reply)
        save_conversation(sender, text, ai_reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

@whatsapp_bp.route('/send-template', methods=['POST'])
def send_template_route():
    data = request.json
    send_template(data['phone'], data.get('template_name', 'test_template'), data.get('parameters', []))
    return "Template sent", 200
