import configparser as cp
from dataclasses import dataclass
from datetime import datetime
import re
import os

class envar():
    def __init__(self,key:str,default:str=None):
        self.key  = key
        self.default = default
    
    def get_value(self):
        if self.default != None:
            return os.getenv(self.key,self.default)
        else:
            value = os.getenv(self.key)
            if not value:
                raise Exception(f"envar '{self.key}' not found!")
            return value

    


class IniUts():
    def __init__(self,ini_prd,ini_dev=None,in_prd=True):
        self.prd_file = ini_prd
        self.dev_file = ini_dev
        self.in_prd = in_prd
        self.delimiters = {}
        self.dateFormats = {}
        self.dev_sections = []
        self.checkKeys()
    
    #TODAS AS CHAVES DE DEV DEVE CONTER EM PRD
    def checkKeys(self):
        if self.dev_file:
            # VALIDA AS SESSOES
            sections_dev = self.getSections(_file=self.dev_file)
            sections_prd = self.getSections()
            not_sections_in_prd = set(sections_dev) - set(sections_prd)
            if not_sections_in_prd:
                raise Exception(f"could not find {not_sections_in_prd} section at production file, dev ini file must contain same sections as in production ini file")

            #VALIDA AS CHAVES
            for sect in sections_dev:
                keys_dev = self.getKeys(sect,_file=self.dev_file)
                keys_prd = self.getKeys(sect)
                not_keys_in_prd = set(keys_dev) - set(keys_prd)
                if not_keys_in_prd:
                    raise Exception(f"could not find {not_keys_in_prd} keys in section '{sect}' at production file, dev ini file must contain same sections as in production ini file")

            self.dev_sections = self.getSections(_file=self.dev_file)

    def write(self,section,key,value):
        _file = self.dev_file if not self.in_prd and section in self.dev_sections else self.prd_file
        config = cp.RawConfigParser()
        config.optionxform = str
        config.read(_file)
        if not section in config.sections():
            config[section] = {}
            config[section][key] = ""
            config.write(open(_file, 'w'))
        config[section][key] = value
        config.write(open(_file, 'w'))
    
    def read(self,section,key):
        _file = self.dev_file if not self.in_prd and section in self.dev_sections else self.prd_file
        config = cp.RawConfigParser()
        config.optionxform = str
        config.read(_file)
        if not section in config.sections():
            raise Exception("Section not found!")
        if not key in config[section]:
            raise Exception("Key not found!")
        return config[section][key]

    def getSections(self,_file=None):
        _file = _file if _file else self.prd_file
        config = cp.RawConfigParser()
        config.optionxform = str
        config.read(_file)
        return [k for k in config.sections()]

    def getKeys(self,section,_file=None):
        _file = _file if _file else self.prd_file
        config = cp.RawConfigParser()
        config.optionxform = str
        config.read(_file)
        if not section in config.sections():
            raise Exception("Section not found!")

        return [k for k in config[section]]
   
    def Section2Dict(self,section,empty_as_null=False,fileIni=None):
        _file = self.dev_file if not self.in_prd and section in self.dev_sections else self.prd_file
        config = cp.RawConfigParser(allow_no_value=True)
        config.optionxform = str
        config.read(fileIni if fileIni else _file)

        dc = dict(config[section])
        return dc if not empty_as_null else {x:(y or None) for x,y in dc.items()}
    
    def format_data(self,dtClass,k,v):
        cls = dtClass.__annotations__[k]
        if cls == tuple:
            name =  f"{str(dtClass)}_{k}"
            if not name in self.delimiters:
                isFormatDefined = k in [x for x in dir(dtClass) if not re.search("__.*__", x)]
                delimiter = getattr(dtClass,k) if isFormatDefined else ','
                self.delimiters[name]=delimiter
                a = 2

            v = tuple(v.split(self.delimiters[name]))
        elif cls == datetime:
            name =  f"{str(dtClass)}_{k}"
            if not name in self.dateFormats:
                isFormatDefined = k in [x for x in dir(dtClass) if not re.search("__.*__", x)]
                delimiter = getattr(dtClass,k) if isFormatDefined else '%Y-%m-%d'
                self.dateFormats[name]=delimiter
                a = 2

            v = datetime.strptime(v,self.dateFormats[name])
        elif cls == bool:
            val = v.strip().lower()
            v = True if val and val in ['true','1','y'] else False
            v = False if val in ['false','','0','n'] else True

        else:
            v = cls(v)
        return v

    def setup_initial_values(self,dtClass):
        for k in dtClass.__annotations__:
            if not hasattr(dtClass, k):
                setattr(dtClass, k, None)
        return dtClass

    def section2DataClass(self,section,dtClass,skip_missing=False,empty_as_null=False):
        dt = self.Section2Dict(section,empty_as_null=empty_as_null)
        dt2 = self.Section2Dict(section,empty_as_null=empty_as_null,fileIni=self.prd_file)

        dtClass = self.setup_initial_values(dtClass)

        #VALIDA AS KEYS NO INI DE DEV
        for k, v in dt.items():
            if not k in dtClass.__annotations__:
                if not skip_missing:
                    raise Exception(f"please create the key '{k}' in data class object")
                else:
                    continue
            v = self.format_data(dtClass,k,v)
            setattr(dtClass, k, v)
        
        class_keys = [x for x in dtClass.__annotations__ if getattr(dtClass,x) != envar]
        
        MissingKeysFromClass = lambda x:list(set(class_keys)  - set(x.keys()))

        #VERIFICA SE AS KEYS NAO ENCONTRADAS ESTAO NO ARQUIVO DE PRD:
        if not self.in_prd:
            for k in MissingKeysFromClass(dt):
                if not k in dt2.keys():
                    if isinstance(getattr(dtClass,k),envar):
                        v = getattr(dtClass,k).get_value()
                        setattr(dtClass, k, v)
                        continue
                    if not skip_missing:
                        raise Exception(f"Cound not find '{k}' keys at section '{section}' in ini file")
                    continue
                v = self.format_data(dtClass,k,dt2[k])
                setattr(dtClass, k, v)
        else:
            if not skip_missing and MissingKeysFromClass(dt):
                raise Exception(f"Cound not find '{MissingKeysFromClass(dt)}' keys at section '{section}' in ini file")

    def link(self,section,skip_missing=False,empty_as_null=False):
        def wrap(function):
            self.section2DataClass(section,function,skip_missing,empty_as_null)
            return function
        return wrap










