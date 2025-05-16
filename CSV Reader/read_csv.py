import pandas 
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
    data = pandas.read_csv(file) # access CSV file
    cell = ''

    for row in range(len(data)):
        for col in range(len(data.columns)):
            cell = data.iloc[row, col] # read every cell in CSV

            if data.columns[col] in colHeaderDict['nameHeaders']: # if full name is under one column (SCENARIO 1)
                # initialize variables for scenario 1
                tempFirstNameHolder = []
                secondaryFirstNameHolder = []
                finalValueHolder = ''
                spaceCount = 0
                secondarySpaceCount = 0
                count = 0

                cell = cell.strip() # remove front & end whitespaces 
                for i in cell:
                    if i == ' ':
                        spaceCount += 1

                if spaceCount == 1: # if 1 whitespace exists, else if multiple exists
                    for i in cell:
                        count += 1 # keeps track for str indexing
                        if i == ' ': break
                        tempFirstNameHolder.append(i) 
                    finalValueHolder = ''.join(map(str, tempFirstNameHolder)) # converty from list ot str                              
                else: 
                    for i in cell:
                        count += 1
                        if i == ' ': secondarySpaceCount = 1
                        if secondarySpaceCount == spaceCount: break
                        tempFirstNameHolder.append(i) 

                    for i in tempFirstNameHolder:
                        if i == ' ': break
                        secondaryFirstNameHolder.append(i)
                    finalValueHolder = ''.join(map(str, secondaryFirstNameHolder)) # converty from list ot str

                oneInstance['fName'] = finalValueHolder # save first name to dictionary
                oneInstance['lName'] = cell[count:] # save last name to dictionary

# debug
identifyCSV()
