import datetime
from os import getcwd
import sqlite3
import config
from psycopg2 import connect

def GetTheDate() -> str:
    return datetime.date.today().strftime('%Y%m%d')

def GetFullJsonFilePath() -> str:
    return getcwd()+f'\\json_{GetTheDate()}.txt' 

def GetValueListFromListOfDict(Dict: dict) -> list:
    TheList = []
    for i in Dict:
        TheList.append(list(i.values()))
    return TheList

def LoadSQLLiteDB(ItemList:list, ListType:str):
    con = sqlite3.connect(f'{ListType}.db')

    cur = con.cursor()

    try:
        res = cur.execute(f'select name from sqlite_master where name = \'{ListType}\'')
        if res.fetchone() is not None:
            cur.execute(f'drop table {ListType}')    
    except sqlite3.OperationalError:
        print(f'{ListType} table was not created previously.')
            
    cur.execute(f'create table {ListType}('+','.join(list(ItemList[0].keys()))+')')

    # Dynamically build the question mark thing for the insert with the number of variables we're inserting
    qs = ''
    for i in range(len(list(ItemList[0].keys()))):
        qs = qs + '?,'
    qs = qs[0:len(qs)-1]

    InsertItems = GetValueListFromListOfDict(ItemList)

    cur.executemany(f'insert into {ListType} values({qs})', InsertItems)
    con.commit()

def LoadToPostgresDB(ItemList, ListType):

    with connect(f'host={config.host} dbname={config.dbname} user={config.username} password={config.password}') as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            try:
                res = cur.execute(f'select table_name from information_schema.tables where table_name = \'{ListType}\'')
                if res.fetchone() is not None:
                    cur.execute(f'drop table {ListType}')    
            except sqlite3.OperationalError:
                print(f'{ListType} table was not created previously.')
                    
            cur.execute(f'create table {ListType}('+' Varchar(500),'.join(list(ItemList[0].keys()))+' Varchar(500)'+')')

            # Dynamically build the question mark thing for the insert with the number of variables we're inserting
            qs = ''
            for i in range(len(list(ItemList[0].keys()))):
                qs = qs + '%s,'
            qs = qs[0:len(qs)-1]

            InsertItems = GetValueListFromListOfDict(ItemList)

            cur.executemany(f'insert into {ListType} values({qs})', InsertItems)
            conn.commit()