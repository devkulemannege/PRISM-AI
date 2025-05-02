# script which imports data into the database
import mariadb as mdb 

#initalization of variables
columnLen = 0
id = 0
agentstatus = ''

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(name, contact, type):
    '''function which can be used to add rows 
    to the business data table in the database'''

    cont.execute('SELECT businessId FROM business')
    columnLen = len(cont.fetchall()) # identify the number of ID's available

    id = columnLen+1 # increase ID number for new row
    agentStatus = 0 

    cont.execute(f"INSERT INTO business VALUES ({id},'{name}','{contact}','{type}',{agentStatus})")

    connection.commit()
    connection.close