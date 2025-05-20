#Module name: connection.py
#Location: PRISM/db/connection.py
# Description: This module is to get the connection from the database

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "credentials.env"))
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

