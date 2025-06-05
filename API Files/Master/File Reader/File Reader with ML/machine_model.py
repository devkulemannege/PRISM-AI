import store_headers
from sklearn.linear_model import LogisticRegression
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

    if '_' in keyword: keyword = keyword.replace('_',' ') # removes underscore if found

    dataEncode = LabelEncoder() # prepare training for keys (Encoded)
    yTrainEncode = dataEncode.fit_transform(yDataset)
    dataVector = TfidfVectorizer() # prepare training for key values (Vectorized )
    xTrainVector = dataVector.fit_transform(xDataSet)

    model = LogisticRegression()
    model.fit(xTrainVector, yTrainEncode) # train model (identify correct values for keys [PlaceHolders: value, key])

    inputDataVec = dataVector.transform([keyword]) # vector conversion 
    predict = model.predict(inputDataVec) # identification using xTrainVector Vector
    confidency = model.predict_proba(inputDataVec)
        
    if max(confidency[0]) < 0.5: 
        #print(max(confidency[0]))
        return 'None'
    else: return dataEncode.inverse_transform(predict)

# debug
#if str(identify('name')) == "['nameHeaders']"": print('YES')
#print(identify(input('Enter Keyword: ')))



