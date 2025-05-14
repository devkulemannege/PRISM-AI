import argparse
import sys
from prismai.messaging.whatsapp import send_template
from prismai.Database.db import fetch_customer_data

def run_cli(config):
    """Parse and execute CLI commands."""
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
        metavar="TEMPLATE_NAME",
        help="Send a template to all numbers in the business table (e.g., -- starting new chunk from prismai.cli import run_cli"
    )
import os
from flask import Flask
from prismai.config import load_config
from prismai.routes.webhook import register_routes

def create_app():
    """Initialize and configure the Flask app."""
    app = Flask(__name__)
    config_path = os.path.join(os.path.dirname(__file__), "credentials.env")
    config = load_config(config_path)
    register_routes(app, config)
    return app, config

if __name__ == "__main__":
    app, config = create_app()
    args = sys.argv[1:]  # Skip script name
    if args:
        run_cli(config)
    else:
        print("Starting Flask app for inbound messaging on port 8080...")
        app.run(host="0.0.0.0", port=8080, debug=True)