import connect_db
connection, cont = connect_db.connection()

def addRow(mobileNo, fName, lName, email):
    '''function which can be used to add rows
    to the customer data table in the database'''
    customerId = 0
    pastConversation = 0
    
    try:
        cont.execute('INSERT INTO customer (mobileNo, fName, lName, email, pastConversation) VALUES (?,?,?,?,?)',
                    (mobileNo, fName, lName, email, pastConversation))
    except Exception as error: 
        raise Exception(f'Error location: customer_table.py | Detailed: {error}') # Error identification
    
    # DISCLAIMER: code below does not LOGICALLY work.
    try:
        cont.execute(f"SELECT customerId FROM customer WEHRE mobileNo = '{mobileNo}'")
        customerId = cont.fetchall() # fetch customerId corresponding to phone number

        cont.execute(f"SELECT msgId FROM chatlog WHERE customerId = {int(customerId[0][0])}")
        cont.execute(f"UPDATE customer SET pastConversation = 1 WEHRE customerId = {int(customerId[0][0])}") # update pastConversation column
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