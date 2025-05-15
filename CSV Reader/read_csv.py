import pandas as pd
import store_headers

def identifyCSV(file):
    '''Reads the entirety of the imported CSV file.
    sends data to the database as well'''
    # initialize data holder dictionary / variables
    oneInstance = {
        'mobileNo' : '', 
        'fName' : '',
        'lName' : '',
        'email' : '',
    }
    colHeaderDict = store_headers.colHeaders() # retrive header dictionary from module
    data = pd.read_csv(file) # access CSV file
    cell = ''

    for row in len(data):
        for col in len(data.columns):
            cell = data.iloc[row, col] # read every cell in CSV

            if data.columns[col] in colHeaderDict['nameHeaders']: # if full name is under one column (SCENARIO 1)
                # initialize variables for scenario 1
                tempFirstNameHolder = []
                tempLastNameHolder = []
                strNameHolder = ''
                spaceCount = 0
                secondarySpaceCount = 0

                cell = cell.strip() # remove unneccesary whitespaces 
                for i in cell:
                    if i == ' ':
                        spaceCount += 1

                if spaceCount == 1:
                    for i in cell:
                        tempFirstNameHolder.append(i)
                else:
                    for i in cell:
                        if i == ' ': secondarySpaceCount = 1
                        if secondarySpaceCount == spaceCount-1 and spaceCount > 1: break
                        tempFirstNameHolder.append(i) # add characters 

                strNameHolder = ' '.join(map(str, tempFirstNameHolder))
# debug
identifyCSV(1)

