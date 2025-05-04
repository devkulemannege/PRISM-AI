'''getBussId function should be called BEFORE addRow function is called.'''
import mariadb as mdb

# initialization of variables
bussIdHolder = ''

connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database')
cont = connection.cursor() # controller to control the database

def getBussId():
    '''retrieves the latest business ID which
    has been entered to the system'''
    global bussIdHolder

    cont.execute('SELECT MAX(Business_ID) FROM business;')
    bussIdHolder = cont.fetchall() # assign ID to variable

def addRow(name, price, description):
    '''function which adds data to 
    product table of database'''

    try: cont.execute(f"INSERT INTO product (businessId, Name, price, description) VALUES ({int(bussIdHolder[0][0])},'{name}','{price}','{description}')")
    except IndexError: print(f'Error: {__doc__}') # displays correct instructions (docstring) if indexerror occurs

    connection.commit()
    connection.close()


