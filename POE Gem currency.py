import requests
import xlsxwriter
import os
import datetime
import json


import pandas as pd
import numpy as np


URL = 'https://poe.ninja/api/data/itemoverview?league=Kalandra&type=SkillGem'

TheDate = datetime.date.today().strftime('%Y%m%d')
FileName = 'json_'+TheDate+'.txt'
FullFilePath = os.getcwd()+'\\'+FileName

# check to see if we've pulled the json data today
if not os.path.exists(FullFilePath):

    # send get request and save response
    r = requests.get(url = URL)
    
    json_dump = json.dumps(r.json())
    
    with open(FullFilePath, 'w') as f:
        f.write(json_dump)
else:
    print('Already retreived the json for today, skipping.')
    
with open(FullFilePath, 'r') as openfile:
    # Reading from json file
    json_data = json.load(openfile)

sheet_rows = []

# iterate through each item and add name and values as row
for item in json_data['lines']:
    row = [item['name']]

    if item['chaosValue'] is not None:
        row.append(item['chaosValue'])

    if item['gemLevel'] is not None:
        row.append(item['gemLevel'])
    
    try:    
        if item['gemQuality'] is not None:
            row.append(item['gemQuality'])
    except KeyError:
        row.append('')
        
    try:    
        if item['corrupted'] is not None:
            row.append(item['corrupted'])
    except KeyError:
        row.append('')
        
    if item['listingCount'] is not None:
        row.append(item['listingCount'])
    
    if 'Anomalous' in item['name']:
        row.append('Anomalous')
    
    elif 'Divergent' in item['name']:
        row.append('Divergent')    
    
    elif 'Awakened' in item['name']:
        row.append('Awakened')  
    
    elif 'Phantasmal' in item['name']:
        row.append('Phantasmal')      
    
    elif 'Enlighten Support' == item['name']:
        row.append('Enlighten')        
    
    elif 'Enhance Support' == item['name']:
        row.append('Enhance')   
    
    elif 'Empower Support' == item['name']:
        row.append('Empower') 
    else:
        row.append('') 
         
    if 'Vaal' in item['name']:
        row.append('Vaal') 
    else:
        row.append('')     

    sheet_rows.append(row)
    
FullFilePath = os.getcwd()+'\\currency_'+TheDate+'.xlsx'
HeaderRow = ['Item', 'Chaos value', 'Gem Level', 'Gem Quality', 'Corrupted', 'Listing Count','Quality Type','Vaal']

if not os.path.exists(FullFilePath):
    # initialize excel worksheet
    workbook = xlsxwriter.Workbook(FullFilePath)
    worksheet = workbook.add_worksheet()
    
    # write each row from row list to worksheet
    c = 0
    
    #add header for excel
    worksheet.write_row(0,0,HeaderRow)
    
    for r, d in enumerate(sheet_rows):
        worksheet.write_row(r+1, c, d)
    
    # write excel file
    workbook.close()
else:
    print('The excel file was already created for today, skipping.')


df = pd.DataFrame(data=sheet_rows, columns=HeaderRow)

print(df)
