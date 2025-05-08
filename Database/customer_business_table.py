import connect_db
connection, cont = connect_db.connection()

def addRow(businessId, phoneNo):
    '''function to add data to the customer_business table. 
    USAGE INSTRUCTIONS: CHECK NOTION "DB Functions Usage Instructions"'''
    # initialization of variables
    customerId = ''

    for singularNo in phoneNo: # add inidividual customerID corresponding to phone number
        try:
            cont.execute(f"SELECT customerId FROM customer WHERE mobileNo = '{singularNo}'")
            customerId = cont.fetchall() # fetch ID to corresponding number
            
            cont.execute('INSERT INTO customer_business VALUES (?,?)',
                        (int(customerId[0][0]), int(businessId[0][0])))
            
            connection.commit()
        except Exception as error:
            raise Exception(f'Error location: customer_business_table.py | Detailed: {error}')

    connection.close()

# for debugging purposes
'''
businessId = [(2,)]
phoneNo = ["+1234567890", "+1987654321", "+1443234567", "0714711537", "+1555123456", "0728000031"]

# You can call the function like this:
addRow(businessId, phoneNo)
'''
