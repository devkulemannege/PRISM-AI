import connect_db
connection, cont = connect_db.connection()

def addRow(name, contact, email, password, type):
    '''function which can be used to add rows 
    to the business data table in the database'''
    agentStatus = 0 # to be changed later

    try:
        cont.execute('INSERT INTO business (name, contact, email, `password`, type, agentStatus) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, contact, email, password, type, agentStatus))
    except Exception as error: 
        raise Exception(f'Error location: business_table.py | Detailed: {error}') # error identification
    
    connection.commit()

'''
# for debugging puposes 
# Test values
name = "Onodera"
contact = "+1234567890"
password = "secureP@ss123"
email = 'devkulamannage@gmail.com'
type = "admin"

cont.execute("SELECT businessId FROM business WHERE name = 'Onodera Kosaki'")
for i in cont.fetchall():
    print(i[0])
'''