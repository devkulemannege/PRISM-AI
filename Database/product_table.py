import mariadb as mdb
import random

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow():
    
    cont.execute('SELECT productId FROM product')
    id = random.randrange(1000000, 9999999)
    while id in cont.fetchall(): id = random.randrange(1000000, 9999999) # creates unique ID for business

    connection.commit()
    connection.close()

