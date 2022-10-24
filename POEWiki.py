import requests
import json
import sqlite3

def GetGemEXPFromPOEWiki():
    GemExp = []
    query = 'cargoquery'
    url = 'https://www.poewiki.net/api.php'

    #This one gets all normal gems
    params = {
        'action' : 'cargoquery',
        'format' : 'json',
        'tables' : 'skill_levels',
        'fields' : '_pageName=PageName, level, experience ',
        'where' : 'experience <> 0 and level = 20',
        # 'group by' : '_pageName',
        'limit' : 500
    }
    data = requests.get(url, params=params).json()

    for i in data['cargoquery']:
        GemExp.append([i['title']['PageName'], i['title']['level'],i['title']['experience']])

    #this one gets all non-normal gems (awakened, enlighten, etc.)
    params = {
        'action' : 'cargoquery',
        'format' : 'json',
        'tables' : 'skill_levels',
        'fields' : '_pageName=PageName, level, experience ',
        'where' : 'experience > 308712291 and level < 7',
        # 'group by' : '_pageName',
        'limit' : 500
    }
    data = requests.get(url, params=params).json()

    for i in data['cargoquery']:
        GemExp.append([i['title']['PageName'], i['title']['level'],i['title']['experience']])

    # save GemExp to sqlite table
    con = sqlite3.connect(f'Gems.db')

    cur = con.cursor()

    try:
        res = cur.execute(f'select name from sqlite_master where name = \'GemExp\'')
        if res.fetchone() is not None:
            cur.execute(f'drop table GemExp')    
    except sqlite3.OperationalError:
        print(f'GemExp table was not created previously.')
            
    cur.execute(f'create table GemExp(GemID INTEGER PRIMARY KEY AUTOINCREMENT, GemName, level, experience)')


    cur.executemany('insert into GemExp (GemName, level, experience) values(?,?,?)', GemExp)

    con.commit()

if __name__ == '__main__':
    GetGemEXPFromPOEWiki()