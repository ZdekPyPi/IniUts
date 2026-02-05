from datetime import datetime
import re
import types
from iniUts.secret import decrypt, encrypt
from iniUts.config_parser_ini import IniCp
from iniUts.envar import Envar


class IniUts:

    def __init__(
        self, ini_prd, ini_dev=None, in_prd=True, encryption_key=None, encoding=None
    ):
        self.delimiters = {}
        self.dateFormats = {}
        self.cp_prd = IniCp(ini_prd, encoding=encoding)
        self.cp_dev = IniCp(ini_dev, encoding=encoding) if ini_dev else None
        self.in_prd = in_prd
        self.encryption_key = encryption_key
        self.checkKeys()

    def refresh(self):
        self.cp_prd = IniCp(self.cp_prd.ini_file, encoding=self.cp_prd.encoding)
        self.cp_dev = (
            IniCp(self.cp_dev.ini_file, encoding=self.cp_dev.encoding)
            if self.cp_dev
            else None
        )

    # TODAS AS CHAVES DE DEV DEVE CONTER EM PRD
    def checkKeys(self):
        if self.cp_dev:
            # VALIDA AS SESSOES
            sections_dev = self.cp_dev.getSections()
            sections_prd = self.cp_prd.getSections()
            not_sections_in_prd = set(sections_dev) - set(sections_prd)
            if not_sections_in_prd:
                raise Exception(
                    f"could not find {not_sections_in_prd} section at production file, dev ini file must contain same sections as in production ini file"
                )

            # VALIDA AS CHAVES
            for sect in sections_dev:
                keys_dev = self.cp_dev.getKeys(sect)
                keys_prd = self.cp_prd.getKeys(sect)
                not_keys_in_prd = set(keys_dev) - set(keys_prd)
                if not_keys_in_prd:
                    raise Exception(
                        f"could not find {not_keys_in_prd} keys in section '{sect}' at production file, dev ini file must contain same sections as in production ini file"
                    )

    def format_data(self, dtClass, k, v):
        cls = dtClass.__annotations__[k]
        if k in dtClass.__CRYPTED_KEYS__:
            v = decrypt(v, self.encryption_key)

        if cls == tuple:
            name = f"{str(dtClass)}_{k}"
            if name not in self.delimiters:
                isFormatDefined = k in [
                    x for x in dir(dtClass) if not re.search("__.*__", x)
                ]
                delimiter = getattr(dtClass, k) or "," if isFormatDefined else ","
                self.delimiters[name] = delimiter

            v = tuple(v.split(self.delimiters[name]))
        elif cls == datetime:
            name = f"{str(dtClass)}_{k}"
            if name not in self.dateFormats:
                isFormatDefined = k in [
                    x for x in dir(dtClass) if not re.search("__.*__", x)
                ]
                delimiter = getattr(dtClass, k) if isFormatDefined else "%Y-%m-%d"
                self.dateFormats[name] = delimiter

            v = datetime.strptime(v, self.dateFormats[name])
        elif cls == bool:
            val = v.strip().lower()
            v = True if val and val in ["true", "1", "y"] else False
            v = False if val in ["false", "", "0", "n"] else True

        else:
            v = cls(v) if v else None
        return v

    # COLOCA TODOS COMO NONE INICIALMENTE
    def setup_initial_values(self, dtClass):
        for k in dtClass.__annotations__:
            if not hasattr(dtClass, k):
                setattr(dtClass, k, None)
        return dtClass

    def section2DataClass(
        self, section, dtClass, skip_missing=False, empty_as_null=False
    ):
        dtClass = self.setup_initial_values(dtClass)

        dtClass.save = types.MethodType(save, dtClass)
        dtClass.__SECTION__ = section
        dtClass.__ENVARS__ = [
            x for x in dtClass.__annotations__ if isinstance(getattr(dtClass, x), Envar)
        ]
        dtClass.__INIUTS__ = self
        dtClass.__CRYPTED_KEYS__ = [
            x.replace("&_", "") for x in self.cp_prd.getKeys(section) if "&_" in x
        ]
        dict_prd = {
            k.replace("&_", ""): v for k, v in self.cp_prd.section2Dict(section).items()
        }
        dict_dev = (
            {
                k.replace("&_", ""): v
                for k, v in self.cp_dev.section2Dict(section).items()
            }
            if self.cp_dev and section in self.cp_dev.getSections()
            else {}
        )

        # ENCRIPTA VARIAVEIS INICIAIS
        for k in dtClass.__CRYPTED_KEYS__:
            # ENCRIPTA VARIAVEIS INICIAIS NO ARQUIVO DE DEV
            if self.cp_dev:
                if (
                    k in dict_dev.keys()
                    and dict_dev[k]
                    and dict_dev[k].startswith("&_")
                ):
                    cripted_value = encrypt(
                        dict_dev[k].replace("&_", ""), self.encryption_key
                    )
                    dict_dev[k] = cripted_value
                    self.cp_dev.write(section, "&_" + k, cripted_value)

            # ENCRIPTA VARIAVEIS INICIAIS NO ARQUIVO DE PRD
            if k in dict_prd.keys() and dict_prd[k] and dict_prd[k].startswith("&_"):
                cripted_value = encrypt(
                    dict_prd[k].replace("&_", ""), self.encryption_key
                )
                dict_prd[k] = cripted_value
                self.cp_prd.write(section, "&_" + k, cripted_value)

        for key in dtClass.__annotations__:
            if key in dtClass.__ENVARS__:
                v = getattr(dtClass, key).get_value()
                v = self.format_data(dtClass, key, v)
                setattr(dtClass, key, v)
                continue
            if key in dict_prd.keys():
                if key in dict_dev.keys() and not self.in_prd:
                    v = dict_dev.get(key)
                else:
                    v = dict_prd.get(key)
                v = self.format_data(dtClass, key, v)
                setattr(dtClass, key, v)
                continue
            raise Exception(
                f"Cound not find '{key}' key at section '{section}' in ini file"
            )

    def link(self, section, skip_missing=False, empty_as_null=False):
        def wrap(function):
            self.section2DataClass(section, function, skip_missing, empty_as_null)
            return function

        return wrap


def save(self):
    ini = self.__INIUTS__
    types_to_str = [str, int, float, bool]
    is_str = lambda t: any([t == x for x in types_to_str])

    for k, t in self.__annotations__.items():
        if k in self.__ENVARS__:
            continue

        if is_str(t):
            value = str(getattr(self, k))
        elif t == tuple:
            value = getattr(self, k)
            delimiter = ini.delimiters[f"{str(self)}_{k}"]
            value = delimiter.join(value)
        elif t == datetime:
            value = getattr(self, k)
            dateFormat = ini.dateFormats[f"{str(self)}_{k}"]
            value = value.strftime(dateFormat)

        if k in self.__CRYPTED_KEYS__:
            k = "&_" + k
            value = encrypt(value, ini.encryption_key)

        if not ini.in_prd and k in ini.cp_dev.getKeys(self.__SECTION__):
            ini.cp_dev.write(self.__SECTION__, k, value)
        else:
            ini.cp_prd.write(self.__SECTION__, k, value)
