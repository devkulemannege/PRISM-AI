import connect_db

def addRow(db_sender, campaign_id, ai_reply, text):
      '''function which can be used to add data into chatlog table
      within the database. Automatically identifies certain information'''
      # initialization of variables
      customerId = None
      businessId = None
      
      # fetches information
      connection, cont = connect_db.get_db_connection()
      try:
          cont.execute("SELECT customerId FROM customer WHERE mobileNo = %s", (db_sender,))
          customerId = cont.fetchone()  # fetch customerId to corresponding sender
      except Exception as error:
          raise Exception(f'Error location: chatlog_table.py | Unable to fetch corresponding values. | Detailed: {error}')  # error identification
      finally:
          if connection and cont:
              cont.close()
              connection.close()

      # enters data to table
      if customerId is not None and campaign_id is not None:
          connection, cont = connect_db.get_db_connection()
          try:
              cont.execute('INSERT INTO chatlog (customerId, LLM_msg, customer_msg, campaignId) VALUES (%s, %s, %s, %s)',
                          (int(customerId[0]), ai_reply, text, campaign_id))  # insert data as new row
              cont.execute('UPDATE customer SET pastConversation = 1 WHERE customerId = %s', (int(customerId[0]),))  # updates pastConversation in customer table
              connection.commit()
          except Exception as error:
              raise Exception(f'Error location: chatlog_table.py | unable to insert data. | Detailed: {error}')  # error identification
          finally:
              if connection and cont:
                  cont.close()
                  connection.close()