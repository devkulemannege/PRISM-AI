#Module name: config.py
#Location: PRISM/config.py
# Description: This module loads environment variables from a .env file and provides access to them.

import os
from dotenv import load_dotenv
from db.connection import get_db_connection

#variable intialization
conn=get_db_connection

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "credentials.env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

#check if the variables are loaded
print(f"Looking for .env at: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'credentials.env'))}")
print(f"Loaded ACCESS_TOKEN: {ACCESS_TOKEN}")
print(f"Loaded PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

# Check if the database connection is successful
if conn:
    print("Connection successful!")
else:
    print("Failed to connect to the database.")
