import pandas 
import customer_table
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
            cell = str(data.iloc[row, col]).strip() # read every cell in CSV

            if data.columns[col] in colHeaderDict['nameHeaders']: # if full name is under one column 
                # initialize variables for particular scenario
                tempFirstNameHolder = []
                secondaryFirstNameHolder = []
                finalValueHolder = ''
                spaceCount = 0
                secondarySpaceCount = 0
                count = 0

                for i in cell:
                    if i == ' ':
                        spaceCount += 1

                if spaceCount == 1: # if 1 whitespace exists, else if multiple exists
                    for i in cell:
                        count += 1 # keeps track for str indexing
                        if i == ' ': break
                        tempFirstNameHolder.append(i) 
                    finalValueHolder = ''.join(map(str, tempFirstNameHolder)) # convert from list ot str                              
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

            elif data.columns[col] in colHeaderDict['firstNameHeaders']: # if cell contains first name data
                oneInstance['fName'] = cell
            
            elif data.columns[col] in colHeaderDict['lastNameHeaders']: # if cell contains last name data
                oneInstance['lName'] = cell
            
            elif data.columns[col] in colHeaderDict['emailHeaders']: # if cell contains email data
                oneInstance['email'] = cell

            elif data.columns[col] in colHeaderDict['mobileNumHeaders']: # if cell contains mobile number data
                oneInstance['mobileNo'] = cell

            else: print(f'Column header not identified for cell address {row+1, col+1}')

        customer_table.addRow(oneInstance['mobileNo'], oneInstance['fName'], oneInstance['lName'], oneInstance['email']) # send data to database table

# debug
identifyCSV('CSV Reader\\TestFile..csv') # send csv file to function
