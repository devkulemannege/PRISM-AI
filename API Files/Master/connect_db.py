import mariadb as mdb
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import os

#Loading environment variables from .env file
print(f"Looking for .env at: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'credentials.env'))}")
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), 'credentials.env')))
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Function to establish connection with the database
def get_db_connection():
    '''function which holds the database attributes
    to establish connection with database'''
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(buffered=True)
        return connection, cursor
    except Error as e:
        print(f"Error connecting to mariadb: {e}")
        return None






