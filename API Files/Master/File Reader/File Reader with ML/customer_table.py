import mariadb as mdb
from connect_db import connection

connection, cursor = connection()

def addRow(mobileNo, fName, lName, email, campaignId=None):
    '''function which can be used to add rows
    to the customer data table in the database'''
    customerId = 0
    pastConversation = 0
    
    try:
        if campaignId is not None:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, campaignId, pastConversation) VALUES (%s, %s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, campaignId, pastConversation))
        else:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, pastConversation) VALUES (%s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, pastConversation))
    except Exception as error: 
        raise Exception(f'Error location: customer_table.py | Detailed: {error}') # Error identification
    
    # DISCLAIMER: code below does not LOGICALLY work.
    try:
        cursor.execute(f"SELECT customerId FROM customer WEHRE mobileNo = '{mobileNo}'")
        customerId = cursor.fetchall() # fetch customerId corresponding to phone number

        cursor.execute(f"SELECT msgId FROM chatlog WHERE customerId = {int(customerId[0][0])}")
        cursor.execute(f"UPDATE customer SET pastConversation = 1 WEHRE customerId = {int(customerId[0][0])}") # update pastConversation column
    except:
        pastConversation = 0

    connection.commit()

# for debugging purposes
'''
# Test values
mobileNo1 = "+1234567890"
fName1 = "Alice"
mobileNo2 = "+1987654321"
fName2 = "Bob"
mobileNo3 = "+1443234567"
fName3 = "Charlie"
mobileNo4 = "0714711537"
fName4 = "David"
mobileNo5 = "+1555123456"
fName5 = "Eve"
mobileNo6 = "0728000031"
fName6 = "Frank"

# Function calls with test values
addRow(mobileNo1, fName1)
addRow(mobileNo2, fName2)
addRow(mobileNo3, fName3)
addRow(mobileNo4, fName4)
addRow(mobileNo5, fName5)
addRow(mobileNo6, fName6)
'''