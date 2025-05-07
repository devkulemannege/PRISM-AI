import mariadb as mdb
connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(businessId, customerId):
    cont.execute('INSERT INTO customer_business VALUES (? ,?)',
                 (int(businessId), int(customerId)))
    
    connection.commit()
    connection.close()