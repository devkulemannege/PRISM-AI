import pandas as pd
import store_headers

def identifyCSV(file):
    '''Reads the entirety of the imported CSV file.
    sends data to the database as well'''
    
dict = store_headers.colHeaders()
print(dict['firstNameHeaders'])
