import requests
import xlsxwriter

import pandas as pd
import numpy as np

URL = "https://poe.ninja/api/data/itemoverview?league=Kalandra&type=SkillGem"

# send get request and save response
r = requests.get(url = URL)
  
# extract data as json
json_data = r.json()

# initialize row list and add row headers as first row
sheet_rows = [["Item", "Chaos value", "Gem Level", "Gem Quality", "Corrupted", "Listing Count","Quality Type"]]

# iterate through each item and add name and values as row
for item in json_data["lines"]:
    row = [item["name"]]

    if item["chaosValue"] is not None:
        row.append(item["chaosValue"])

    if item["gemLevel"] is not None:
        row.append(item["gemLevel"])
    
    try:    
        if item["gemQuality"] is not None:
            row.append(item["gemQuality"])
    except KeyError:
        row.append("")
        
    try:    
        if item["corrupted"] is not None:
            row.append(item["corrupted"])
    except KeyError:
        row.append("")
        
    if item["listingCount"] is not None:
        row.append(item["listingCount"])
    
    if "Anomalous" in item["name"]:
        row.append("Anomalous")
    
    if "Divergent" in item["name"]:
        row.append("Divergent")    
    
    if "Awakened" in item["name"]:
        row.append("Awakened")  
    
    if "Phantasmal" in item["name"]:
        row.append("Phantasmal")       
    
    if "Vaal" in item["name"]:
        row.append("Vaal")             
    
    if "Enlighten Support" == item["name"]:
        row.append("Enlighten")        
    
    if "Enhance Support" == item["name"]:
        row.append("Enhance")   
    
    if "Empower Support" == item["name"]:
        row.append("Empower")               
         

    sheet_rows.append(row)

# initialize excel worksheet
workbook = xlsxwriter.Workbook("currency.xlsx")
worksheet = workbook.add_worksheet()

# write each row from row list to worksheet
col = 0

for row, data in enumerate(sheet_rows):
    worksheet.write_row(row, col, data)

# write excel file
workbook.close()