import mariadb as mdb
import random

# initialization of variables 
columnLen = 0
id = 0

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(mobileNo, fName):
    '''function which can be used to add rows
    to the customer data table in the database'''

    cont.execute('SELECT customerId FROM customer')
    id = random.randrange(1000000, 9999999)
    while id in cont.fetchall(): id = random.randrange(1000000, 9999999) # creates unique ID for business

    pastConversation = 0
    pastPurchase = 0

    cont.execute(f"INSERT INTO customer VALUES ({id},'{mobileNo}','{fName}',{pastConversation},{pastPurchase})")

    connection.commit()
    connection.close()
