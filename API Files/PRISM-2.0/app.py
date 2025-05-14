from flask import Flask
from services.campaign_services import send_template_cli, send_template_to_all
from routes.whatsapp_routes import whatsapp_bp
import argparse
import sys
app = Flask(__name__)
app.register_blueprint(whatsapp_bp)


if __name__ == '__main__':
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Prism AI WhatsApp Agent")
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
