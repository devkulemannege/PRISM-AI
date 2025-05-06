import mariadb as mdb

# initialization of variables 
columnLen = 0
id = 0
customerId = 0

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(mobileNo, fName):
    '''function which can be used to add rows
    to the customer data table in the database'''
    global customerId
    pastConversation = 0

    cont.execute('INSERT INTO customer (mobileNo, fName, pastConversation) VALUES (?,?,?)',
                 (mobileNo, fName, pastConversation))
    
    # DISCLAIMER: code below does not logically work.
    try:
        cont.execute(f"SELECT customerId FROM customer WEHRE mobileNo = '{mobileNo}'")
        customerId = cont.fetchall() # fetch customerId corresponding to phone number

        cont.execute(f"SELECT msgId FROM chatlog WHERE customerId = {int(customerId[0][0])}")
        print(cont.fetchall())
        cont.execute(f"UPDATE customer SET pastConversation = 1 WEHRE customerId = {int(customerId[0][0])}") # update pastConversation column
        print(cont.fetchall())
    except:
        pastConversation = 0

    connection.commit()
    connection.close()
