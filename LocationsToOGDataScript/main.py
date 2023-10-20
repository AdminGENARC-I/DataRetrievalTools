import pandas as pd

with open('./source.xlsx', 'rb') as sourceFile:
    sourceData = pd.read_excel(sourceFile)

    idToLocation = {}
    for index, row in sourceData.iterrows():
        currentDocumentId = sourceData.at[index, 'document_id']
        idToLocation[currentDocumentId] = sourceData.at[index, 'location']

    with open('./target.xlsx', 'rb') as targetFile:
        targetData = pd.read_excel(targetFile)

        for index, row in targetData.iterrows():
            currentId = targetData.at[index, 'id']
            if idToLocation.get(currentId) != None:
                targetData.at[index, 'project_location'] = idToLocation[currentId]
        
        targetData.to_excel('./target.xlsx', index=False)