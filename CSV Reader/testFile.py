import store_headers
dict = store_headers.colHeaders()
tempFirstNameHolder = []
cell = 'Ravish Devpriya Kulemannege'
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

strNameHolder = ''.join(map(str, tempFirstNameHolder))
print(strNameHolder)