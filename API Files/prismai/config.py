import os
from dotenv import load_dotenv

def load_config(dotenv_path):
    """Load and validate environment variables from .env file."""
    load_dotenv(dotenv_path)
    
    config = {
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
        "PHONE_NUMBER_ID": os.getenv("PHONE_NUMBER_ID"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "VERIFY_TOKEN": os.getenv("VERIFY_TOKEN"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME")
    }
    
    # Validate required variables
    required = ["ACCESS_TOKEN", "PHONE_NUMBER_ID", "GROQ_API_KEY", "VERIFY_TOKEN", "DB_HOST", "DB_USER", "DB_NAME"]
    missing = [key for key in required if not config[key]]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    print(f"Loaded config from: {os.path.abspath(dotenv_path)}")
    return config