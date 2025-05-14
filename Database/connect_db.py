import mariadb as mdb

def connection():
    '''function which holds the database attributes
    to establish connection with database'''
    connection = mdb.connect(host='localhost',user='root',password='',database='prism_ai_database_new')
    cont = connection.cursor() # controller to control the database 
    return connection, cont



