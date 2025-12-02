#TEST FILE
from dotenv import load_dotenv
import sys
import os
sys.path.append("./iniUts")
from iniUts import *
load_dotenv()

ini = IniUts('prd_config.ini')
ini = IniUts('prd_config.ini','dev_config.ini',in_prd=True,encryption_key="asdoajhsdoiuayhsoidhasoidhalijksdhaioshdioaws")

#TODAS AS CHAVES DE DEV DEVE CONTER EM PRD


@ini.link('PERSON')
class Person():
    USERNAME: str = envar("USERNAME","NO_NAME")
    NAME   : str
    age    : int
    amount : float
    friends: tuple = ','
    dob    : datetime = "%Y-%m-%d"

Person.NAME = "Heitor"
Person.friends = ("friend1","friend2","friend3","friend4")
Person.save()



pass
# pass
# a = 1

# @dataclass
# class IPS():
#    ip5   : bool

# @dataclass
# class IPS2():
#    ip5   : str

#import os
#os.system("cls")

#os.environ['ENV'] = 'PRD'

#ini = IniUts('prd_config.ini')
#ini = IniUts('prd_config.ini','dev_config.ini',in_prd=False)
#ini.section2DataClass('PERSON',Person)
#ini.section2DataClass('IPS',IPS)
#ini.section2DataClass('IPS2',IPS2)
#print(IPS2.ip5)

#a  =1

#print(ini.read("PERSON","NAME"))
# ini.Section2Dict('IPS2')
# # ini.section2DataClass('PERSON',Person)
# # ini.section2DataClass('PERSON',Person)
# # print(Person.NAME)

#a  =1