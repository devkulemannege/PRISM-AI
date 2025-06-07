import mariadb as mdb

def connection():
    '''function which holds the database attributes
    to establish connection with database'''
    try:
        connection = mdb.connect(host='localhost', user='root', password='', database='prismaimaster')
        cont = connection.cursor(buffered=True)
        return connection, cont
    except mdb.Error as e:
        print(f"Database connection error: {e}")
        return None, None



