import connect_db
connection, cont = connect_db.connection()

def addRow(mobileNo, campaignId):
    '''function which adds data to the customer_campaign table'''
    # initialization of variables
    customerId = ''

    cont.execute(f"SELECT customerId FROM customer WEHRE mobileNo = '{mobileNo}'")
    customerId = cont.fetchall() # fetch customerId according to relevant mobile number

    cont.execute('INSERT INTO customer_campiagn VALUES (?,?)',
                 (int(customerId[0][0]), int(campaignId[0][0])))
    connection.commit()



