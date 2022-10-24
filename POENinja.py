import requests
from os import path
from json import dumps
import CommonFunctions


def GetGemDataFromPoeNinja(League: str='Kalandra',DataType: str='SkillGem'):
    URL = f'https://poe.ninja/api/data/itemoverview?league={League}&type={DataType}'
    TheDate = CommonFunctions.GetTheDate()
    JSONFilePath = CommonFunctions.GetFullJsonFilePath()

    # check to see if we've pulled the json data today
    if not path.exists(JSONFilePath):

        # send get request and save response
        r = requests.get(url = URL)
        
        json_dump = dumps(r.json())
        
        with open(JSONFilePath, 'w') as f:
            f.write(json_dump)
    else:
        print('Already retreived the json for today, skipping.')


if __name__ == '__main__':
    GetGemDataFromPoeNinja()