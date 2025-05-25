import pandas 
import customer_table
import store_headers
import pathlib

def readData(file):
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
    cell = ''

    extention = pathlib.Path(file) # identify the file extention
    if extention.suffix == '.csv': data = pandas.read_csv(file)
    else: data = pandas.read_excel(file)

    for row in range(len(data)):
        for col in range(len(data.columns)):
            cell = str(data.iloc[row, col]).strip() # read every cell in CSV

            if data.columns[col].strip() in colHeaderDict['nameHeaders']: # if full name is under one column 
                # initialize variables for particular scenario
                tempFirstNameHolder = []
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
                    oneInstance['fName'] = ''.join(map(str, tempFirstNameHolder)) # convert from list ot str and assing to first name
                    oneInstance['lName'] = cell[count:] # assing last name to last name
                else:
                    for i in cell:
                        count += 1
                        if i == ' ': secondarySpaceCount += 1
                        if secondarySpaceCount == spaceCount: break
                    oneInstance['fName'] = oneInstance['lName'] =  cell[count:] # assing last name to first name & last name

            elif data.columns[col].strip() in colHeaderDict['firstNameHeaders']: oneInstance['fName'] = cell # if cell contains first name dataoneInstance['fName'] = cell
            
            elif data.columns[col].strip() in colHeaderDict['lastNameHeaders']: oneInstance['lName'] = cell # if cell contains last name data
            
            elif data.columns[col].strip() in colHeaderDict['emailHeaders']: oneInstance['email'] = cell # if cell contains email data               

            elif data.columns[col].strip() in colHeaderDict['mobileNumHeaders']: oneInstance['mobileNo'] = cell # if cell contains mobile number data         

        customer_table.addRow(oneInstance['mobileNo'], oneInstance['fName'], oneInstance['lName'], oneInstance['email']) # send data to database table

readData('PRISM-AI\Online Dashboard\CustomerUpload\Pamula_8.csv')