import connect_db
connection, cont = connect_db.connection()

def addRow(phoneNo, campaignId, agentMsg, customerMsg):
    '''function which can be used to add data into chatlog table
    within the database. Automatically identifies certain information'''
    # initialization of variables
    customerId = 0
    businessId = 0
    
    # fetches information
    try:
        cont.execute(f"SELECT customerId FROM customer WHERE mobileNo = '{phoneNo}'")
        customerId = cont.fetchall() # fetch customerId to corresponding phoneNo
        cont.execute(f"SELECT businessId FROM campaign WHERE campaignId = {campaignId}")
        businessId = cont.fetchall() # fetch businessId to corresponding productId
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to fetch corresponding values. | Detailed: {error}') # error identification

    # enters data to table
    try:
        cont.execute('INSERT INTO chatlog (customerId, businessId, campaignId, LLM_msg, customer_msg) VALUES (?, ?, ?, ?, ?)',
                    (int(customerId[0][0]), int(businessId[0][0]), int(campaignId[0][0]), agentMsg, customerMsg)) # insert data as new row
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | unable to insert data. | Detailed: {error}') # error identification

    # update pastConversation
    try: 
        cont.execute(f'UPDATE customer SET pastConversation = 1 WHERE customerId = {int(customerId[0][0])}') # updates pastConversation in customer table
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to update customer pastConversation value. | Detailed: {error}') # error identification
    
    connection.commit()
