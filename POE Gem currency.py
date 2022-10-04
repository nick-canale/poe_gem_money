import requests
import xlsxwriter
import os
import datetime
import json
import sqlite3


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

if os.path.exists(FullFilePath):
    try:
        os.remove(FullFilePath)
    except:
        print('Cannot delete the file, exiting')
        exit()

HeaderRow = ['Item', 'Chaos value', 'Gem Level', 'Gem Quality', 'Corrupted', 'Listing Count','Quality Type','Vaal']

# initialize excel worksheet
workbook = xlsxwriter.Workbook(FullFilePath)
worksheet = workbook.add_worksheet('DataDump')

# write each row from row list to worksheet
c = 0

#add header for excel
worksheet.write_row(0,0,HeaderRow)

for r, d in enumerate(sheet_rows):
    worksheet.write_row(r+1, c, d)


#messing around with pandas
#df = pd.DataFrame(data=sheet_rows, columns=HeaderRow)

#print(df)


con = sqlite3.connect('Gems.db')

cur = con.cursor()

try:
    res = cur.execute('select name from sqlite_master where name = \'Gems\'')
    if res.fetchone() is not None:
        cur.execute('drop table Gems')    
except sqlite3.OperationalError:
    print('Gems table was not created previously.')
        
    
cur.execute('create table Gems('+','.join(HeaderRow).replace(' ','')+')')

cur.executemany('insert into Gems values(?,?,?,?,?,?,?,?)', sheet_rows)
con.commit()


def GetGemProfit(Workbook, WorksheetName, ProfitQuery, SQLConnection):
    # Create the sheet to hold the data
    worksheet = workbook.add_worksheet(WorksheetName)
    
    # dynamically set up the header based on the columns returned in the query
    HeaderRow = []
    res = SQLConnection.execute(ProfitQuery)
    for colname in res.description:
        HeaderRow.append(colname[0])
        
    worksheet.write_row(0,0,HeaderRow)
    
    for position, rowdata in enumerate(SQLConnection.execute(ProfitQuery)):
        worksheet.write_row(position+1,0,rowdata)

    
#first, let's look at normal superior gems
ProfitQuery = """
SELECT a.Item GemName
, a.ChaosValue BuyPrice
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, b.ChaosValue - a.ChaosValue Profit
FROM Gems a
inner join Gems b
    on a.item = b.item
    and a.QualityType = ''
    and b.GemLevel = 20
    and b.GemQuality = 20
    and b.Corrupted = ''
where a.GemLevel = 1
and a.Corrupted = ''
and a.QualityType = ''
and a.GemQuality = 20
order by Profit desc
"""

GetGemProfit(workbook, 'NormalGems', ProfitQuery, con)

# next, let's look at normal superior gems at level 21
# it's a 1/8 chance to get level 21 on corrupt according to this thread 
# https://www.reddit.com/r/pathofexile/comments/f2qgk3/how_are_the_chances_of_corruption_of_a_gem/
ProfitQuery = """
SELECT a.Item GemName
, a.ChaosValue BuyPrice
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, b.ChaosValue - a.ChaosValue Profit
FROM Gems a
inner join Gems b
    on a.item = b.item
    and a.QualityType = ''
    and b.GemLevel = 21
    and b.GemQuality = 20
where a.GemLevel = 1
and a.Corrupted = ''
and a.QualityType = ''
and a.GemQuality = 20
order by Profit desc
"""
GetGemProfit(workbook, 'NormalGems21', ProfitQuery, con)


# alt quality gems
ProfitQuery = """
SELECT a.Item GemName
, a.ChaosValue BuyPrice
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, b.ChaosValue - a.ChaosValue Profit
FROM Gems a
inner join Gems b
    on a.item = b.item
    and a.QualityType = b.QualityType
    and a.QualityType in('Anomalous','Divergent','Phantasmal')
    and b.GemLevel = 20
    and b.GemQuality = 20
where a.GemLevel <> 20
and a.Corrupted = ''
and a.QualityType in('Anomalous','Divergent','Phantasmal')
order by Profit desc
"""

GetGemProfit(workbook, 'AltQualityGems', ProfitQuery, con)

# Enhance / Enlighten / Empower
ProfitQuery = """
SELECT a.Item GemName
, a.ChaosValue BuyPrice
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, b.ChaosValue - a.ChaosValue Profit
FROM Gems a
inner join Gems b
    on a.item = b.item
    and a.QualityType in ('Enhance','Enlighten','Empower')
    and b.GemLevel = 3
    and b.GemQuality = 20
    and b.Corrupted = ''
where a.GemLevel = 1
and a.Corrupted = ''
and a.QualityType in('Enhance','Enlighten','Empower')
union all
SELECT a.Item GemName
, a.ChaosValue BuyPrice
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, b.ChaosValue - a.ChaosValue Profit
FROM Gems a
inner join Gems b
    on a.item = b.item
    and a.QualityType in ('Enhance','Enlighten','Empower')
    and b.GemLevel = 4
where a.GemLevel = 1
and a.Corrupted = ''
and a.QualityType in('Enhance','Enlighten','Empower')
order by Profit desc
"""

GetGemProfit(workbook, 'EEEGems', ProfitQuery, con)

    
# write excel file
workbook.close()
