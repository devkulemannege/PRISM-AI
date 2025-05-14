import sys
import os
from flask import Flask
from prismai.config import load_config
from prismai.routes.webhook import register_routes
from prismai.CLI import run_cli

def create_app():
    """Initialize and configure the Flask app."""
    app = Flask(__name__)
    config_path = os.path.join(os.path.dirname(__file__), "credentials.env")
    print(f"Config path resolved to: {config_path}")
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