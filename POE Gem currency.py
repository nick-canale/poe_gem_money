import xlsxwriter
import os
import json
import sqlite3 
import re
from POENinja import GetJsonDataFromPoeNinja
import CommonFunctions as CF


def GetExcelFilePath():
    return os.getcwd()+f'\\currency_{CF.GetTheDate()}.xlsx'


def GetGemsDict(FullJsonFilePath=CF.GetFullJsonFilePath()):

    if not os.path.exists(FullJsonFilePath):
        GetJsonDataFromPoeNinja()
    
    with open(FullJsonFilePath, 'r') as openfile:
        # Reading from json file
        json_data = json.load(openfile)
    

    GemList = []

    # iterate through each item and add name and values as row
    for item in json_data['lines']:

        GemName = item['name']
        ChaosValue = item['chaosValue'] if item['chaosValue'] is not None else ''
        GemLevel = item['gemLevel'] if item['gemLevel'] is not None else ''
        ListingCount = item['listingCount'] if item['listingCount'] is not None else ''
        IsAwakaned = 'Awakened' in item['name']
        
        try:    
            GemQuality = item['gemQuality'] if item['gemQuality'] is not None else 0
        except KeyError:
            GemQuality = 0
            
        try:    
            IsCorrupted = True if item['corrupted'] is not None else False   
        except KeyError:
            IsCorrupted = False
         
        if re.search('Anomalous.+',item['name']):
            AltQualityName = 'Anomalous'
        elif re.search('Divergent.+',item['name']):
            AltQualityName = 'Divergent'
        elif re.search('Phantasmal.+',item['name']):
            AltQualityName = 'Phantasmal'
        else:
            AltQualityName = ''
        
        match item['name']:
            case 'Enlighten Support':
                ExceptionalGem=True
            case 'Enhance Support':
                ExceptionalGem=True
            case 'Empower Support':
                ExceptionalGem=True
            case 'Awakened Enlighten Support':
                ExceptionalGem=True
            case 'Awakened Enhance Support':
                ExceptionalGem=True
            case 'Awakened Empower Support':
                ExceptionalGem=True
            case _:
                ExceptionalGem=False

        IsVaal = 'Vaal' in item['name']
              
        Gem = {
            'GemName': GemName,
            'ChaosValue': ChaosValue,
            'GemLevel': GemLevel,
            'GemQuality': GemQuality,
            'ListingCount': ListingCount,
            'IsAwakened': IsAwakaned,
            'IsCorrupted': IsCorrupted,
            'AltQualityName': AltQualityName,
            'ExceptionalGem': ExceptionalGem
        }

        GemList.append(Gem)
        
    return GemList


def CreateExcelFile(ItemList, FullFilePath=GetExcelFilePath()):

    if os.path.exists(FullFilePath):
        try:
            os.remove(FullFilePath)
        except:
            print('Cannot delete the file, exiting')
            exit()

    HeaderRow = list(ItemList[0].keys())
    # initialize excel worksheet
    workbook = xlsxwriter.Workbook(FullFilePath)
    worksheet = workbook.add_worksheet('DataDump')

    # write each row from row list to worksheet
    c = 0

    #add header for excel
    worksheet.write_row(0,0,HeaderRow)
    
    InsertItems = CF.GetValueListFromListOfDict(ItemList)

    for r, d in enumerate(InsertItems):
        worksheet.write_row(r+1, c, d)
    return workbook

def AddGemProfitToExcel(Workbook, WorksheetName, ProfitQuery, DBName,FullFilePath=GetExcelFilePath()):
    # Create the sheet to hold the data
    worksheet = Workbook.add_worksheet(WorksheetName)
    
    # dynamically set up the header based on the columns returned in the query
    HeaderRow = []
    con = sqlite3.connect(f'{DBName}.db')
    res = con.execute(ProfitQuery)
    for colname in res.description:
        HeaderRow.append(colname[0])
        
    worksheet.write_row(0,0,HeaderRow)
    
    for position, rowdata in enumerate(con.execute(ProfitQuery)):
        worksheet.write_row(position+1,0,rowdata)
    return Workbook

    
def PopulateExcelFile(GemsDict):
    # Create the excel file and load the data tab
    Workbook = CreateExcelFile(GemsDict)

    #first, let's look at normal superior gems
    ProfitQuery1 = """
    SELECT a.GemName
    , a.ChaosValue BuyPrice
    , a.GemQuality BuyGemQuality
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
    , b.ChaosValue - a.ChaosValue Profit
    FROM Gems a
    inner join Gems b
        on a.GemName = b.GemName
        and b.GemLevel = 20
        and b.GemQuality = 20
        and b.IsCorrupted = 0
    where a.GemLevel = 1
    and a.GemQuality = 20
    and a.IsCorrupted = 0
    order by Profit desc
    """

    AddGemProfitToExcel(Workbook, 'NormalGems', ProfitQuery1, 'Gems')

    # next, let's look at normal superior gems at level 21
    # it's a 1/8 chance to get level 21 on corrupt according to this thread 
    # https://www.reddit.com/r/pathofexile/comments/f2qgk3/how_are_the_chances_of_corruption_of_a_gem/
    ProfitQuery2 = """
    SELECT a.GemName
    , a.ChaosValue BuyPrice
    , a.GemQuality BuyGemQuality
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
    , case when a.IsCorrupted = 1 then (b.ChaosValue - a.ChaosValue * 8)*(1/8) else b.ChaosValue - a.ChaosValue end Profit
    FROM Gems a
    inner join Gems b
        on a.GemName = b.GemName
        and a.IsCorrupted = b.IsCorrupted
        and b.GemLevel = 21
        and b.GemQuality = 20
    where a.GemLevel = 1
    and a.GemQuality = 20
    order by Profit desc
    """
    AddGemProfitToExcel(Workbook, 'NormalGems21', ProfitQuery2, 'Gems')


    # alt quality gems
    ProfitQuery3 = """
    SELECT a.GemName
    , a.ChaosValue BuyPrice
    , a.GemQuality BuyGemQuality
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
    , b.ChaosValue - a.ChaosValue Profit
    FROM Gems a
    inner join Gems b
        on a.GemName = b.GemName
        and a.AltQualityName = b.AltQualityName
        and a.AltQualityName in('Anomalous','Divergent','Phantasmal')
        and b.GemLevel = 20
        and b.GemQuality = 20
    where a.GemLevel <> 20
    and a.IsCorrupted = False
    and a.AltQualityName in('Anomalous','Divergent','Phantasmal')
    order by Profit desc
    """

    AddGemProfitToExcel(Workbook, 'AltQualityGems', ProfitQuery3, 'Gems')

    # Enhance / Enlighten / Empower
    ProfitQuery4 = """
    SELECT a.GemName GemName
    , a.ChaosValue BuyPrice
    , a.GemQuality BuyGemQuality
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
    , b.ChaosValue - a.ChaosValue Profit
    FROM Gems a
    inner join Gems b
        on a.GemName = b.GemName
        and a.ExceptionalGem <> ''
        and b.GemLevel = 3
        and b.GemQuality = 20
        and b.IsCorrupted = False
    where a.GemLevel = 1
    and a.IsCorrupted = False
    and a.ExceptionalGem <> ''
    union all
    SELECT a.GemName GemName
    , a.ChaosValue BuyPrice
    , a.GemQuality BuyGemQuality
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
    , b.ChaosValue - a.ChaosValue Profit
    FROM Gems a
    inner join Gems b
        on a.GemName = b.GemName
        and b.ExceptionalGem <> ''
        and b.GemLevel = 4
    where a.GemLevel = 1
    and a.IsCorrupted = False
    and a.ExceptionalGem <> ''
    order by Profit desc
    """

    AddGemProfitToExcel(Workbook, 'EEEGems', ProfitQuery4, 'Gems')

    Workbook.close()



# Get the gems list from the json file
GemsDict = GetGemsDict()



