#Module name: app.py
#Location: PRISM/app.py
# Description: This module is the main entry point for the application. It initializes the Flask app, loads environment variables, and sets up the database connection.


import config
from flask import Flask
from routes.whatsapp_routes import whatsapp_bp
from agent.outbound_temp import send_template_to_all, send_template
import argparse
from dotenv import load_dotenv
import os
import sys

#load env variable
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../credentials.env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

app = Flask(__name__)#This line initializes a new Flask application instance.
app.register_blueprint(whatsapp_bp)#This line registers the WhatsApp routes with the Flask app.


def send_template_cli(phone, template_name, parameters):
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    send_template(phone, template_name, parameters)
    return None

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

