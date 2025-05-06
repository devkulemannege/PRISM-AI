import mariadb as mdb

# initialization of variables 
columnLen = 0
id = 0

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(mobileNo, fName):
    '''function which can be used to add rows
    to the customer data table in the database'''
    pastConversation = 0 # to be changed

    cont.execute('INSERT INTO customer (Mobile_No, Fname, past_conversation) VALUES (?,?,?)',
                 (mobileNo, fName, pastConversation))
    connection.commit()
    connection.close()
