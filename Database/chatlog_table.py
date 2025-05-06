import mariadb as mdb
# initialization of variables
customerId = 0
businessId = 0

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(phoneNo, productId, agentMsg, customerMsg):
    '''function which can be used to add data into chatlog table
    within the database. Automatically identifies certain information'''
    global customerId
    global businessId

    cont.execute(f"SELECT customerId FROM customer WHERE mobileNo = '{phoneNo}'")
    customerId = cont.fetchall() # fetch customerId to corresponding phoneNo
    cont.execute(f"SELECT businessId FROM product WHERE productId = {productId}")
    businessId = cont.fetchall() # fetch businessId to corresponding productId

    cont.execute('INSERT INTO chatlog (customerId, businessId, productId, LLM_msg, customer_msg) VALUES (?, ?, ?, ?, ?)',
                (int(customerId[0][0]), int(businessId[0][0]), int(productId[0][0]), agentMsg, customerMsg)) # insert data as new row

    cont.execute(f'UPDATE customer SET pastConversation = 1 WHERE customerId = {int(customerId[0][0])}') # updates pastConversation in customer table
    connection.commit()
    connection.close()
