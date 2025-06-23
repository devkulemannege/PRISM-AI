# Fix import so it always loads the local connect_db, not the one in Master/
import sys
import os
import importlib.util

# Use absolute import with full path manipulation to force import from the correct file
connect_db_path = os.path.join(os.path.dirname(__file__), 'connect_db.py')
spec = importlib.util.spec_from_file_location('connect_db_local', connect_db_path)
connect_db_local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connect_db_local)
connection = connect_db_local.connection

connect, cursor = connection()

def addRow(mobileNo, fName, lName, email, campaignId=None, businessId=None):
    '''function which can be used to add rows
    to the customer data table in the database'''
    customerId = 0
    pastConversation = 0
    if connect is None or cursor is None:
        print("Database connection not available.")
        return
    try:
        if campaignId is not None and businessId is not None:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, campaignId, businessId, pastConversation) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, campaignId, businessId, pastConversation))
        elif campaignId is not None:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, campaignId, pastConversation) VALUES (%s, %s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, campaignId, pastConversation))
        elif businessId is not None:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, businessId, pastConversation) VALUES (%s, %s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, businessId, pastConversation))
        else:
            cursor.execute('INSERT INTO customer (mobileNo, fName, lName, email, pastConversation) VALUES (%s, %s, %s, %s, %s)',
                        (mobileNo, fName, lName, email, pastConversation))
        connect.commit()  # Commit after insert
    except Exception as error: 
        raise Exception(f'Error location: customer_table.py | Detailed: {error}') # Error identification
    
    # Update pastConversation if customer has chatlog
    try:
        cursor.execute("SELECT customerId FROM customer WHERE mobileNo = %s", (mobileNo,))
        customerId_row = cursor.fetchone()
        if customerId_row:
            customerId = customerId_row[0]
            cursor.execute("SELECT COUNT(*) FROM chatlog WHERE customerId = %s", (int(customerId),))
            msg_count = cursor.fetchone()[0]
            if msg_count > 0:
                cursor.execute("UPDATE customer SET pastConversation = 1 WHERE customerId = %s", (int(customerId),))
                connect.commit()
    except Exception as e:
        print(f"Error updating pastConversation: {e}")

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