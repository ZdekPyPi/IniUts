import configparser as cp


class IniCp:

    def __init__(self, ini_file, encoding=None):
        self.ini_file = ini_file
        self.encoding = encoding
        self.read_ini()

    def read_ini(self):
        config = cp.RawConfigParser(
            allow_no_value=True, comment_prefixes=(";", "#"), strict=False
        )
        config.optionxform = str
        if self.encoding:
            with open(self.ini_file, "r", encoding=self.encoding) as f:
                config.read_string(f.read())
        else:
            config.read(self.ini_file)

        self.config_parser = config

    def write(self, section, key, value):
        if section not in self.config_parser.sections():
            self.config_parser[section] = {}
        self.config_parser[section][key] = value
        self.config_parser.write(open(self.ini_file, "w", encoding=self.encoding))

    def read(self, section, key):
        if section not in self.config_parser.sections():
            raise Exception("Section not found!")
        if key not in self.config_parser[section]:
            raise Exception("Key not found!")
        return self.config_parser[section][key]

    def getSections(self):
        return list(self.config_parser.sections())

    def getKeys(self, section):
        if section not in self.config_parser.sections():
            raise Exception("Section not found!")

        return list(self.config_parser[section])

    def section2Dict(self, section):
        dc = dict(self.config_parser[section])

        return {x: (y or None) for x, y in dc.items()}

    def __iter__(self):
        sections = self.getSections()
        for sect in sections:
            # Retorna uma tupla (chave, valor) para cada iteração
            yield sect, self.section2Dict(sect)
