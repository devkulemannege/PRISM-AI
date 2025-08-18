import pandas 
import customer_table
import pathlib
from machine_model import identify

def readData(file, businessId=None):
    '''Reads the entirety of the imported CSV file.
    sends data to the database as well'''
    # initialize data holder dictionary / variables
    oneInstance = {
        'mobileNo' : '', 
        'fName' : '',
        'lName' : '',
        'email' : '',
    }
    cell = ''
    count = 0 

    extention = pathlib.Path(file) # identify the file extention
    if extention.suffix == '.csv': data = pandas.read_csv(file)
    else: data = pandas.read_excel(file)

    while count == 0: # check whether the top row holds column headers required 
        for rowCheck in range(len(data)): # variable unused
            for colCheck in  range(len(data.columns)): 
                passValue = str(data.columns[colCheck])
                if str(identify(passValue)) in ["['nameHeaders']", "['firstNameHeaders']", "['lastNameHeaders']", "['emailHeaders']", "['mobileNumHeaders']"]:
                    count += 1 # checks if the column row is in fact, a column row 
            if count == 0:
                data.columns = data.iloc[0] # replace col headers with first row
                data = data[1:]
                data = data.reset_index(drop=True) 

    for row in range(len(data)):
        for col in range(len(data.columns)):
            cell = str(data.iloc[row, col]).strip() # read every cell in CSV
            passValue = str(data.columns[col].strip())

            if str(identify(passValue)) == "['nameHeaders']": # if full name is under one column 
                # initialize variables for particular scenario
                tempFirstNameHolder = []
                spaceCount = 0
                secondarySpaceCount = 0
                count_main = 0

                for i in cell:
                    if i == ' ':
                        spaceCount += 1

                if spaceCount == 1: # if 1 whitespace exists, else if multiple exists
                    for i in cell:
                        count_main += 1 # keeps track for str indexing
                        if i == ' ': break
                        tempFirstNameHolder.append(i) 
                    oneInstance['fName'] = ''.join(map(str, tempFirstNameHolder)) # convert from list ot str and assing to first name
                    oneInstance['lName'] = cell[count_main:] # assing last name to last name
                else:
                    for i in cell:
                        count_main += 1
                        if i == ' ': secondarySpaceCount += 1
                        if secondarySpaceCount == spaceCount: break
                    oneInstance['fName'] = oneInstance['lName'] =  cell[count_main:] # assing last name to first name & last name

            elif str(identify(passValue)) == "['firstNameHeaders']":oneInstance['fName'] = cell # if cell contains first name dataoneInstance['fName'] = cell
            
            elif str(identify(passValue)) == "['lastNameHeaders']": oneInstance['lName'] = cell # if cell contains last name data
            
            elif str(identify(passValue)) == "['emailHeaders']": oneInstance['email'] = cell # if cell contains email data               

            elif str(identify(passValue)) == "['mobileNumHeaders']": oneInstance['mobileNo'] = cell # if cell contains mobile number data         

        # Get campaignId if available in context (e.g., pass as argument or set globally)
        campaignId = None
        if hasattr(readData, 'campaignId'):
            campaignId = readData.campaignId

        # fix missing '+' in country code and first '0' in local numbers
        if len(oneInstance['mobileNo']) == 9:
            mobFixList = []
            mobFixList = oneInstance['mobileNo'].split()
            mobFixList.insert(0, '0')
            oneInstance['mobileNo'] = ''.join(map(str, mobFixList))

        elif (len(oneInstance['mobileNo']) == 11 or len(oneInstance['mobileNo']) == 10) and (oneInstance['mobileNo'][0] != '+'):
            mobFixList = []
            for i in oneInstance['mobileNo']: mobFixList.append(i)
            if len(mobFixList) == 10: 
                del(mobFixList[0])
            else:
                del(mobFixList[0])
                del(mobFixList[0])

            mobFixList.insert(0, '0')
            oneInstance['mobileNo'] = ''.join(map(str, mobFixList))
        #print(oneInstance)
        customer_table.addRow(oneInstance['mobileNo'], oneInstance['fName'], oneInstance['lName'], oneInstance['email'], campaignId, businessId)

#readData('C:\\Users\\Devpriya\\Documents\\Extra\\readExcel.xlsx')