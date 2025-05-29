import store_headers
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder   
from sklearn.feature_extraction.text import TfidfVectorizer

# initialize variables
colHeaderDict = store_headers.colHeaders() # access dictionary 
xDataSet = [] # store values of relevant key
yDataset = [] #  store classification keys

for key in colHeaderDict.keys():
    for value in colHeaderDict[key]:
        xDataSet.append(value)
        yDataset.append(key)

def identify(keyword):
    '''ML based column type identification 
    for a wider range of inupts'''
    print(keyword)
    xTrain, xTest, yTrain, yTest = train_test_split(xDataSet, yDataset, test_size=0.1, random_state=1) # split data for training 

    dataEncode = LabelEncoder() # prepare training for keys (Encoded)
    yTrainEncode = dataEncode.fit_transform(yTrain)
    dataVector = TfidfVectorizer() # prepare training for key values (Vectorized )
    xTrainVector = dataVector.fit_transform(xTrain)

    model = LogisticRegression()
    model.fit(xTrainVector, yTrainEncode) # train model (identify correct values for keys [PlaceHolders: value, key])

    inputDataVec = dataVector.transform([keyword]) # vector conversion 
    predict = model.predict(inputDataVec) # identification using xTrainVector Vector
    confidency = model.predict_proba(inputDataVec)
    #print(f'Key: {dataEncode.inverse_transform(predict)}') # decode identified key using dataEncode 
        
    if max(confidency[0]) < 0.4: return 'None'
    else: return dataEncode.inverse_transform(predict)


# debug
#if str(identify('name')) == "['nameHeaders']": print('YES')
#print(identify('state'))



