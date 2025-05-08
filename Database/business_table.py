import connect_db
connection, cont = connect_db.connection()

def addRow(name, contact, password, type, prompt, parameters):
    '''function which can be used to add rows 
    to the business data table in the database'''
    agentStatus = 0 # to be changed later

    try:
        cont.execute('INSERT INTO business (name, contact, `password`, type, prompt, parameters, agentStatus) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (name, contact, password, type, prompt, parameters, agentStatus))
    except Exception as error: 
        raise Exception(f'Error location: business_table.py | Detailed: {error}') # error identification
    
    connection.commit()
    connection.close()

# for debugging puposes 
'''
# Test values
name = "Alice"
contact = "+1234567890"
password = "secureP@ss123"
type = "admin"
prompt = "Generate a product description for a new smart home device."
parameters = "{'tone': 'professional', 'length': 'short', 'language': 'English'}"

# Test the function
addRow(name, contact, password, type, prompt, parameters)
'''