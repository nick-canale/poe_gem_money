import datetime
from os import getcwd

def GetTheDate():
    return datetime.date.today().strftime('%Y%m%d')

def GetFullJsonFilePath():
    return getcwd()+f'\\json_{GetTheDate()}.txt' 