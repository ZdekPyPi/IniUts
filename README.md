# Ini Uts
#
### Installation

```sh
pip install iniUts
```

## GitHub
https://github.com/ZdekPyPi/IniUts


## Usage
#
<!-- //==================================================== -->
## read
##### test.ini file
```ini
[Person]
name    = myname
age     = 31
amount  = 20.3
friends = friend1,friend2,friend3
dob     = 1991-12-23
```
##### python code
```py
from iniUts import IniUts

ini = IniUts('test.ini')
p_name = ini.cp_prd.read('Person','name')

print(p_name)
```
##### output
```py
"myname"
```

<!-- //==================================================== -->
## write
##### test.ini file
```ini
[PERSON]
name    = myname
```
##### python code
```py
from iniUts import IniUts

ini = IniUts('test.ini')
ini.cp_prd.write('PERSON','last_name','mylastname')

```
<!-- //==================================================== -->
## getKeys
##### test.ini file
```ini
[PERSON]
name      = myname
last_name = mylastname
```
##### python code
```py
from iniUts import IniUts

ini = IniUts('test.ini')
keys = ini.cp_prd.getKeys("PERSON")
print(keys)
```
##### output
```py
['name','last_name']
```

<!-- //==================================================== -->
## Section2Dict
##### test.ini file
```ini
[PERSON]
name    = myname
age     = 31
amount  = 20.3
friends = friend1,friend2,friend3
dob     = 1991-12-23
```
##### python code
```py
from iniUts import IniUts

ini = IniUts('test.ini')
ini.cp_prd.section2Dict('PERSON')
print(Person)

```
##### output
```py
{
    "name"    = "myname"
    "age"     = "31"
    "amount"  = "20.3"
    "friends" = "friend1,friend2,friend3"
    "dob"     = "1991-12-23"
}

```
<!-- //==================================================== -->
## link
##### test.ini file
```ini
[PERSON]
name    = myname
age     = 31
amount  = 20.3
friends = friend1,friend2,friend3
dob     = 1991-12-23
```
##### python code
```py
from iniUts import IniUts
from datetime import datetime
from dataclasses import dataclass

ini = IniUts('test.ini')

@ini.link('PERSON')
class Person():
    name   : str
    age    : int
    amount : float
    friends: tuple = ','
    dob    : datetime = "%Y-%m-%d"

print(Person.name)
print(Person.age)
print(Person.amount)
print(Person.friends)
print(Person.dob)

```
##### output
```py
myname
31
20.3
("friend1","friend2","friend3")
datetime.datetime(1991, 12, 2, 0, 0)

```

# ENCRYPTION

<!-- //==================================================== -->
## Using Encryption
##### test.ini file
```ini
[CREDENTIALS]
username = myuser
&_password = &_mypassword123
&_api_key  = &_secret_api_key_12345
```
##### python code
```py
from iniUts import IniUts

# Initialize with encryption key
ini = IniUts('test.ini', encryption_key="my_secure_encryption_key_32_chars")

@ini.link('CREDENTIALS')
class Credentials():
    username: str
    password: str
    api_key : str

print(Credentials.username)
print(Credentials.password)
print(Credentials.api_key)

# Save encrypted values back to file
Credentials.password = "new_secure_password"
Credentials.save()
```
##### output
```py
myuser
mypassword123
secret_api_key_12345
```

**Note:** When using encryption, the values in the INI file will be encrypted. The encryption key must be provided every time you read or write to the file.

# ENVIORNMENT CHANGING

<!-- //==================================================== -->
## Link
##### prd.ini file
```ini
[PERSON] 
name    = myName # Will be changed in DEV
age     = 31
amount  = 20.3
friends = friend1,friend2,friend3
dob     = 1991-12-23

[CONFIG]
ip    = <some_ip>
path  = <some_path> # Will be changed in DEV

```
##### dev.ini file
```ini
[PERSON] #change only PERSON name
name    = myOtherName

[CONFIG] #change only CONFIG path
path    = <another_path>

```

##### python code
```py
from iniUts import IniUts,envar
from datetime import datetime
from dataclasses import dataclass


ini = IniUts('prd.ini','dev.ini',in_prd=True) #CHANGE S WILL BE MADE IF IN DEVELOPMENT MODE

@ini.link('PERSON')
class Person():
    name   : str
    age    : int
    amount : float
    friends: tuple = ','
    dob    : datetime = "%Y-%m-%d"
    mode   : envar(key='MODE',default='DEV')

@ini.link('CONFIG')
class Config():
    ip   : str
    path : str


print(Person.name)
print(Person.age)
print(Config.ip)
print(Config.path)

```
##### output
```py
#==================== IN PRD
myName
31
<some_ip>
<some_path>
#==================== IN DEV
myOtherName
16
<some_ip>
<some_path>

```




