# script which imports data into the database
import mariadb as mdb 

#initalization of variables
id = 0
agentstatus = ''

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def addRow(name, contact, password, type, template, prompt):
    '''function which can be used to add rows 
    to the business data table in the database'''
    agentStatus = 0 # to be changed later

    cont.execute('INSERT INTO business (name, contact, `password`, type, template, `prompt`, agentStatus) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, contact, password, type, template, prompt, agentStatus))
    
    connection.commit()
    connection.close
