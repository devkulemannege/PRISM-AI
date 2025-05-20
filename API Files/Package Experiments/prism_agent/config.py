# Contents of prism_agent/config.py
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.env"))

class Config:
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DEBUG = True # Set this to False in production