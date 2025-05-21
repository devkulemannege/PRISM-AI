import connect_db
connection, cont = connect_db.get_db_connection()


def addRow(sender, campaignId, ai_reply, text):
    '''function which can be used to add data into chatlog table
    within the database. Automatically identifies certain information'''
    # initialization of variables
    customerId = 0
    businessId = 0
    
    # fetches information
    try:
        cont.execute(f"SELECT customerId FROM customer WHERE mobileNo = '{sender}'")
        customerId = cont.fetchall() # fetch customerId to corresponding sender
        cont.execute(f"SELECT businessId FROM campaign WHERE campaignId = {campaignId}")
        businessId = cont.fetchall() # fetch businessId to corresponding productId
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to fetch corresponding values. | Detailed: {error}') # error identification

    # enters data to table
    try:
        cont.execute('INSERT INTO chatlog (customerId, businessId, campaignId, LLM_msg, customer_msg) VALUES (?, ?, ?, ?, ?)',
                    (int(customerId[0][0]), int(businessId[0][0]), int(campaignId[0][0]), ai_reply, text)) # insert data as new row
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | unable to insert data. | Detailed: {error}') # error identification

    # update pastConversation
    try: 
        cont.execute(f'UPDATE customer SET pastConversation = 1 WHERE customerId = {int(customerId[0][0])}') # updates pastConversation in customer table
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to update customer pastConversation value. | Detailed: {error}') # error identification
    
    connection.commit()
