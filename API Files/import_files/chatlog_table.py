import connect_db
connection, cursor = connect_db.connection()


def addRow(sender, campaign_id, ai_reply, text):
    '''function which can be used to add data into chatlog table
    within the database. Automatically identifies certain information'''
    print(f"addRow called with: sender={sender}, user_msg={text}, ai_reply={ai_reply}, campaign_id={campaign_id}")
    # initialization of variables
    customerId = 0
    businessId = 0
    
    # fetches information
    try:
        cursor.execute(f"SELECT customerId FROM customer WHERE mobileNo = '{sender}'")
        customerId = cursor.fetchall() # fetch customerId to corresponding sender
        cursor.execute(f"SELECT businessId FROM campaign WHERE campaignId = {campaign_id}")
        businessId = cursor.fetchall() # fetch businessId to corresponding productId
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to fetch corresponding values. | Detailed: {error}') # error identification

    # enters data to table
    try:
        cursor.execute('INSERT INTO chatlog (customerId, businessId, campaignId, LLM_msg, customer_msg) VALUES (?, ?, ?, ?, ?)',
                    (int(customerId[0][0]), int(businessId[0][0]), int(campaign_id[0][0]), ai_reply, text)) # insert data as new row
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | unable to insert data. | Detailed: {error}') # error identification

    # update pastConversation
    try: 
        cursor.execute(f'UPDATE customer SET pastConversation = 1 WHERE customerId = {int(customerId[0][0])}') # updates pastConversation in customer table
    except Exception as error:
        raise Exception(f'Error location: chatlog_table.py | Unable to update customer pastConversation value. | Detailed: {error}') # error identification
    print("addRow functioned called and conversation saved successfully")
    connection.commit()
