import store_headers
dict = store_headers.colHeaders()
tempFirstNameHolder = []
secondaryFirstNameholder = []
cell = 'Thinal Pamula Ravish Devpriya Kulemannege'
spaceCount = 0
secondarySpaceCount = 0
count = 0

cell = cell.strip() # remove unneccesary whitespaces 
for i in cell:
    if i == ' ':
        spaceCount += 1

if spaceCount == 1:
    for i in cell:
        if i == ' ': break
        tempFirstNameHolder.append(i)
    strNameHolder = ''.join(map(str, tempFirstNameHolder))
else:
    
    for i in cell:
        count += 1
        if i == ' ': secondarySpaceCount += 1
        if secondarySpaceCount == spaceCount:break
        tempFirstNameHolder.append(i) # add characters 

    for i in tempFirstNameHolder:
        if i == ' ': break
        secondaryFirstNameholder.append(i)
    
    strNameHolder = ''.join(map(str, secondaryFirstNameholder))

print(f'Last name: {cell[count:]}')
print(f'First name: {strNameHolder}')