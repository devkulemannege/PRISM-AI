from flask import Blueprint, request
from prismai.messaging.whatsapp import send_whatsapp_message, send_template
from prismai.messaging.groq import call_llama
from prismai.Database.db import save_conversation, fetch_customer_data
import time

webhook_bp = Blueprint('webhook', __name__)

def register_routes(app, config):
    """Register webhook and API routes with the Flask app."""
    app.register_blueprint(webhook_bp)

    @webhook_bp.route('/webhook', methods=['GET'])
    def verify():
        """Verify the webhook with Facebook."""
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        print(f"Webhook verification: mode={request.args.get('hub.mode')}, token={token}, challenge={challenge}")
        if token == config['VERIFY_TOKEN']:
            print("Webhook verified successfully")
            return challenge, 200
        else:
            print("Webhook verification failed")
            return "Verification token mismatch", 403

    @webhook_bp.route("/webhook", methods=["POST"])
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

                        ai_reply = call_llama(config, text)
                        send_whatsapp_message(config, sender, ai_reply)
                        save_conversation(config, sender, text, ai_reply)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

    @webhook_bp.route("/send-template", methods=["POST"])
    def send_template_route():
        """Send a template message to a specific phone number."""
        data = request.json
        phone = data.get("phone")
        template_name = data.get("template_name", "test_template")
        parameters = data.get("parameters", [])
        send_template(config, phone, template_name, parameters)
        return "Template sent", 200

    @webhook_bp.route("/send-to-all", methods=["POST"])
    def send_to_all_route():
        """Send a template message to all numbers in the business table."""
        data = request.json
        template_name = data.get("template_name", "retail_template")
        template_data = fetch_customer_data(config, template_name)
        if template_data:
            for data in template_data:
                send_template(config, data["phone"], data["template_name"], data["parameters"])
                time.sleep(1)
        return "Templates sent to all numbers", 200