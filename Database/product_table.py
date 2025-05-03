import mariadb as mdb
import random

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow():

    connection.commit()
    connection.close()

