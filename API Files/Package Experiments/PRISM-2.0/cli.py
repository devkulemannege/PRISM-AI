import argparse
from routes.whatsapp_routes import send_to_all

def run_cli(config):
      parser = argparse.ArgumentParser(description='WhatsApp Messaging Agent CLI')
      parser.add_argument('--send-to-all', type=int, help='Send template messages to all numbers using the specified business ID')
      args = parser.parse_args()

      if args.send_to_all:
          business_id = args.send_to_all
          send_to_all(config, business_id)
          print(f"Completed sending templates for template ID {business_id}")
      else:
          print("No CLI action specified. Use --send-to-all <business_id> to send messages.")