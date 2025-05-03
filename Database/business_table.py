# script which imports data into the database
import mariadb as mdb 
import random

#initalization of variables
id = 0
agentstatus = ''

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(name, contact, type):
    '''function which can be used to add rows 
    to the business data table in the database'''
    global id

    cont.execute('SELECT businessId FROM business')
    id = random.randrange(1000000, 9999999)
    while id in cont.fetchall(): id = random.randrange(1000000, 9999999) # creates unique ID for business

    agentStatus = 0 #to be changed later

    cont.execute(f"INSERT INTO business VALUES ({id},'{name}','{contact}','{type}',{agentStatus})")

    connection.commit()
    connection.close